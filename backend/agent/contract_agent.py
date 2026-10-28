"""合同抽取 ReAct Agent 主循环。

把「合同文本」通过多步推理 + 事实核查 + 自检，产出自洽的 CustomerProfile。
LLM 主导推理与修复，工具只提供事实。
"""

import json
import logging
import time

import httpx

from backend.agent import tools
from backend.agent.prompts import SYSTEM_PROMPT, TOOLS_SCHEMA
from backend.config import (
    AGENT_MAX_ITERS,
    AGENT_MAX_OUTPUT_TOKENS,
    AGENT_MAX_SECONDS,
    AGENT_MAX_TOKENS,
    AGENT_MAX_TOOL_CALLS_PER_ROUND,
    AGENT_SOFT_TOKEN_RATIO,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_DISABLE_THINKING,
    REACT_MODEL,
)
from backend.models import CustomerConstraints, CustomerPerformance, CustomerProfile
from backend.services.profile_policy import (
    build_extraction_metrics,
    normalize_warnings,
    sanitize_routing_preferences,
)

logger = logging.getLogger(__name__)

TIERS = ["simple", "medium", "complex"]


def _build_user_prompt(contract_text: str, customer_name: str, custom_instructions: str) -> str:
    return (
        f"Customer name: {customer_name}\n\n"
        f"<contract>\n{contract_text}\n</contract>\n\n"
        f"<custom_instructions>\n{custom_instructions or 'None'}\n</custom_instructions>"
    )


def _build_profile_from_finalize(args: dict, customer_name: str) -> CustomerProfile:
    constraints = args.get("constraints") or {}
    performance = args.get("performance") or {}
    prefs = args.get("routing_preferences") or {"simple": [], "medium": [], "complex": []}

    profile = CustomerProfile(
        customer_id="",  # 由 model_post_init 从 customer_name 生成
        customer_name=args.get("customer_name") or customer_name,
        use_case=args.get("use_case", "general"),
        objective=args.get("objective", "low_cost"),
        constraints=CustomerConstraints(**constraints),
        performance=CustomerPerformance(**performance),
        routing_preferences={tier: list(prefs.get(tier, []) or []) for tier in TIERS},
        warnings=list(args.get("warnings") or []),
    )
    sanitize_routing_preferences(profile)
    normalize_warnings(profile)
    return profile


def _execute_tool(name: str, args: dict):
    if name == "list_providers":
        return tools.list_providers()
    if name == "list_models":
        return tools.list_models(
            tier=args.get("tier"),
            provider=args.get("provider"),
            region=args.get("region"),
            max_latency_ms=args.get("max_latency_ms"),
            min_context_tokens=args.get("min_context_tokens"),
            max_cost_per_m_input=args.get("max_cost_per_m_input"),
            sort_by=args.get("sort_by"),
        )
    if name == "get_model":
        return tools.get_model(args.get("name"))
    if name == "check_coverage":
        return tools.check_coverage(args.get("constraints") or {})
    if name == "check_profile":
        return tools.check_profile(args.get("profile") or {})
    raise ValueError(f"Unknown tool: {name}")


async def _call_llm(
    messages: list[dict],
    *,
    timeout: float = 120.0,
    tool_choice: dict | str = "auto",
) -> dict:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": REACT_MODEL,
                "messages": messages,
                "temperature": 0.0,
                "max_tokens": AGENT_MAX_OUTPUT_TOKENS,
                "tools": TOOLS_SCHEMA,
                "tool_choice": tool_choice,
                **({"thinking": {"type": "disabled"}} if DEEPSEEK_DISABLE_THINKING else {}),
            },
        )
        response.raise_for_status()
        return response.json()


def _tool_error_result(tc: dict, message: str) -> dict:
    """构造 tool 错误结果，回灌给模型让它自我修正。"""
    return {
        "role": "tool",
        "tool_call_id": tc.get("id", ""),
        "content": json.dumps({"error": message}, ensure_ascii=False),
    }


async def run_react_agent(
    contract_text: str,
    customer_name: str,
    custom_instructions: str = "",
) -> CustomerProfile:
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(contract_text, customer_name, custom_instructions)},
    ]

    started = time.perf_counter()
    prompt_tokens = 0
    completion_tokens = 0
    llm_calls = 0
    iteration = 0
    soft_nudged = False

    def record_usage(usage: dict) -> None:
        nonlocal prompt_tokens, completion_tokens
        prompt_tokens += int(usage.get("prompt_tokens") or 0)
        completion_tokens += int(usage.get("completion_tokens") or 0)

    def attach_metrics(
        profile: CustomerProfile,
        *,
        finalized_by: str = "model",
        budget_hit: str | None = None,
    ) -> CustomerProfile:
        profile.extraction = build_extraction_metrics(
            mode="react",
            llm_calls=llm_calls,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            elapsed_ms=int((time.perf_counter() - started) * 1000),
            iterations=iteration,
            finalized_by=finalized_by,
            budget_hit=budget_hit,
        )
        return profile

    budget_hit: str | None = None

    while True:
        remaining = AGENT_MAX_SECONDS - (time.perf_counter() - started)
        total_tokens = prompt_tokens + completion_tokens

        # 预算检查放在每次调用之前：超限就不再调查，转入强制 finalize
        if iteration >= AGENT_MAX_ITERS:
            budget_hit = "iterations"
            break
        if remaining <= 5:
            budget_hit = "time"
            break
        if total_tokens >= AGENT_MAX_TOKENS:
            budget_hit = "tokens"
            break

        # 软预算：提示模型收敛，不改变路线
        if not soft_nudged and total_tokens >= AGENT_MAX_TOKENS * AGENT_SOFT_TOKEN_RATIO:
            logger.info(
                f"Agent soft token budget reached ({total_tokens}/{AGENT_MAX_TOKENS}); "
                "nudging model to finalize"
            )
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Budget notice: you are approaching the token budget. "
                        "Finish the remaining checks quickly and call the finalize tool "
                        "with the information you already have."
                    ),
                }
            )
            soft_nudged = True

        iteration += 1
        llm_calls += 1
        data = await _call_llm(messages, timeout=min(120.0, remaining))
        record_usage(data.get("usage") or {})

        msg = data["choices"][0]["message"]
        tool_calls = msg.get("tool_calls") or []

        if not tool_calls:
            # 模型未调工具就结束（异常路径），尝试从 content 解析兜底
            content = msg.get("content") or ""
            logger.warning("Agent ended without finalize; falling back to content parse")
            try:
                return attach_metrics(_build_profile_from_finalize(json.loads(content), customer_name))
            except (json.JSONDecodeError, TypeError, ValueError):
                raise RuntimeError("Agent ended without a valid profile")

        messages.append(msg)
        for index, tc in enumerate(tool_calls):
            if index >= AGENT_MAX_TOOL_CALLS_PER_ROUND:
                # 必须为每个 tool_call_id 回一条消息，否则下一轮请求非法
                messages.append(
                    _tool_error_result(
                        tc,
                        "Tool call skipped: per-round tool call limit reached. "
                        "Re-issue only if it is still necessary.",
                    )
                )
                continue

            fn = tc.get("function") or {}
            name = fn.get("name") or ""
            raw_args = fn.get("arguments")

            # 1) 参数解析失败：把错误回灌给模型重试，而不是中断整个 Agent
            try:
                args = json.loads(raw_args) if raw_args else {}
                if not isinstance(args, dict):
                    raise ValueError("arguments must be a JSON object")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Malformed tool arguments for '{name}': {e}")
                messages.append(
                    _tool_error_result(
                        tc,
                        f"Invalid JSON arguments for tool '{name}': {e}. "
                        "Re-issue the same tool call with a valid JSON object.",
                    )
                )
                continue

            # 2) finalize 校验失败：把原因回灌，让模型修正后重新 finalize
            if name == "finalize":
                try:
                    return attach_metrics(_build_profile_from_finalize(args, customer_name))
                except Exception as e:
                    logger.warning(f"finalize rejected: {type(e).__name__}: {e}")
                    messages.append(
                        _tool_error_result(
                            tc,
                            f"finalize rejected: {type(e).__name__}: {e}. "
                            "Fix the profile fields and call finalize again.",
                        )
                    )
                    continue

            # 3) 工具执行失败（未知工具/参数不合法等）：同样回灌
            try:
                result = _execute_tool(name, args)
            except Exception as e:
                logger.warning(f"Tool '{name}' failed: {type(e).__name__}: {e}")
                known = "list_providers, list_models, get_model, check_coverage, check_profile, finalize"
                messages.append(
                    _tool_error_result(
                        tc,
                        f"Tool '{name}' failed: {type(e).__name__}: {e}. Available tools: {known}.",
                    )
                )
                continue

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    # 预算触发：复用已积累的上下文，强制模型 finalize（而不是丢弃后重跑单次抽取）
    force_timeout = min(120.0, max(10.0, remaining))
    logger.info(f"Agent budget hit ({budget_hit}); forcing finalize")
    try:
        iteration += 1
        llm_calls += 1
        force_messages = messages + [
            {
                "role": "user",
                "content": (
                    f"Budget reached ({budget_hit}). Stop investigating and call the finalize "
                    "tool NOW with the best profile you can build from the information already "
                    "collected. Do not call any other tool."
                ),
            }
        ]
        data = await _call_llm(
            force_messages,
            timeout=force_timeout,
            tool_choice={"type": "function", "function": {"name": "finalize"}},
        )
        record_usage(data.get("usage") or {})

        msg = data["choices"][0]["message"]
        tool_calls = msg.get("tool_calls") or []
        if tool_calls:
            raw_args = (tool_calls[0].get("function") or {}).get("arguments")
        else:
            raw_args = msg.get("content")
        args = json.loads(raw_args or "{}")
        profile = _build_profile_from_finalize(args, customer_name)
        return attach_metrics(profile, finalized_by="forced", budget_hit=budget_hit)
    except Exception as e:
        raise RuntimeError(
            f"Budget hit ({budget_hit}) and forced finalize failed: {type(e).__name__}: {e}"
        ) from e
