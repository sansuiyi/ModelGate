"""CustomerProfile 的共享清洗与抽取观测逻辑。

被 ReAct Agent、单次抽取路由和 API 层共同使用，保证所有入库 profile
都经过同一套合规清理和 warning 归一化。
"""

from backend.config import DEEPSEEK_INPUT_PRICE_PER_M, DEEPSEEK_OUTPUT_PRICE_PER_M
from backend.models import CustomerProfile
from backend.services.provider_registry import get_active_catalog
from backend.services.router_engine import _passes_policy

TIERS = ["simple", "medium", "complex"]


def sanitize_routing_preferences(profile: CustomerProfile) -> None:
    """防御性清理：去掉目录里不存在的模型、以及违反合约约束的模型。

    注意：**不强制模型档位与所在档相等**。需求驱动场景下允许跨档降级
    （例如 CN 合规客户没有 simple 档模型时，simple 档指向 medium 档的 deepseek-v3），
    这与 router_engine 的淘汰逻辑一致（它也不校验档位）。
    """
    catalog = get_active_catalog()
    cleaned: dict[str, list[str]] = {}

    for tier in TIERS:
        kept: list[str] = []
        for name in profile.routing_preferences.get(tier, []) or []:
            info = catalog.get(name)
            if info is None:
                continue
            if not _passes_policy(info, profile):
                continue
            kept.append(name)
        cleaned[tier] = kept

        already_warned = any(
            isinstance(w, dict) and w.get("type") == "model_gap" and w.get("tier") == tier
            for w in profile.warnings
        )
        if not kept and not already_warned:
            profile.warnings.append(
                {
                    "type": "model_gap",
                    "severity": "warning",
                    "tier": tier,
                    "message": f"no compliant model available for tier '{tier}' after sanitization",
                }
            )

    profile.routing_preferences = cleaned


def normalize_warnings(profile: CustomerProfile) -> None:
    """把字符串 warning 统一成 {type, severity, message} 结构，供前端直接渲染。"""
    normalized: list[dict] = []
    for w in profile.warnings or []:
        if isinstance(w, dict):
            item = dict(w)
            item.setdefault("type", "contract_ambiguity")
            item.setdefault("severity", "warning")
            if not item.get("message"):
                item["message"] = item.get("msg") or str(item)
            normalized.append(item)
        else:
            normalized.append(
                {"type": "contract_ambiguity", "severity": "warning", "message": str(w)}
            )
    profile.warnings = normalized


def build_extraction_metrics(
    *,
    mode: str,
    llm_calls: int,
    prompt_tokens: int,
    completion_tokens: int,
    elapsed_ms: int,
    iterations: int = 0,
    fallback_from: str | None = None,
    fallback_reason: str | None = None,
    finalized_by: str | None = None,
    budget_hit: str | None = None,
) -> dict:
    """构造抽取观测数据：token、调用次数、耗时，以及可选成本估算。"""
    total_tokens = prompt_tokens + completion_tokens

    estimated_cost: float | None = None
    if DEEPSEEK_INPUT_PRICE_PER_M or DEEPSEEK_OUTPUT_PRICE_PER_M:
        estimated_cost = round(
            prompt_tokens / 1_000_000 * DEEPSEEK_INPUT_PRICE_PER_M
            + completion_tokens / 1_000_000 * DEEPSEEK_OUTPUT_PRICE_PER_M,
            6,
        )

    metrics = {
        "mode": mode,
        "llm_calls": llm_calls,
        "iterations": iterations,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": estimated_cost,
        "elapsed_ms": elapsed_ms,
    }
    if fallback_from:
        metrics["fallback_from"] = fallback_from
    if fallback_reason:
        metrics["fallback_reason"] = fallback_reason
    if finalized_by:
        metrics["finalized_by"] = finalized_by
    if budget_hit:
        metrics["budget_hit"] = budget_hit
    return metrics
