"""合同抽取 ReAct Agent 测试（标准库 unittest，无需 pytest）。

运行：python -m unittest backend.tests.test_contract_agent -v

覆盖：
1. 工具：能力过滤、coverage 可行性统计、check_profile 冲突识别
2. Agent 主循环：模式 B（纯需求）全链路、finalize 清洗、幻觉/违约模型剔除、不收敛保护
"""

import json
import unittest

from backend.agent import contract_agent, tools


def _tool_call(name: str, args: dict, cid: str = "call_1") -> dict:
    return {
        "id": cid,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)},
    }


def _resp(*calls: dict) -> dict:
    return {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": list(calls)}}]}


class ScriptedLLM:
    """按脚本依次返回 tool_calls，用于替换真实的 OpenRouter 调用。"""

    def __init__(self, responses: list[dict]):
        self._responses = list(responses)
        self.calls = 0

    async def __call__(self, messages: list[dict], **kwargs) -> dict:
        self.calls += 1
        if not self._responses:
            raise AssertionError("LLM script exhausted")
        return self._responses.pop(0)


class ToolsTest(unittest.TestCase):
    def test_capability_filters(self):
        fast = tools.list_models(max_latency_ms=400, sort_by="latency")
        self.assertTrue(fast)
        self.assertTrue(all(m["avg_latency_ms"] <= 400 for m in fast))
        self.assertEqual([m["avg_latency_ms"] for m in fast], sorted(m["avg_latency_ms"] for m in fast))

        long_ctx = tools.list_models(min_context_tokens=200000)
        self.assertTrue(long_ctx)
        self.assertTrue(all(m["max_context"] >= 200000 for m in long_ctx))

        cheap = tools.list_models(max_cost_per_m_input=0.3)
        self.assertTrue(cheap)
        self.assertTrue(all(m["cost_per_m_input"] <= 0.3 for m in cheap))

    def test_check_coverage_cn_contract(self):
        """华康/法盾：CN-only + 仅 DeepSeek/GLM → simple/complex 应无合规模型。"""
        report = tools.check_coverage(
            {"region": "CN-only", "allowed_providers": ["deepseek", "glm"]}
        )
        self.assertIn("simple", report["gaps"])
        self.assertIn("complex", report["gaps"])
        self.assertGreaterEqual(report["tiers"]["medium"]["count"], 1)

    def test_check_coverage_eu_contract(self):
        """Helios：EU-only + 仅 Anthropic/OpenAI → complex 应无合规模型。"""
        report = tools.check_coverage(
            {
                "region": "EU-only",
                "allowed_providers": ["anthropic", "openai"],
                "forbidden_providers": ["google", "deepseek"],
            }
        )
        self.assertEqual(report["tiers"]["complex"]["count"], 0)
        self.assertIn("complex", report["gaps"])

    def test_check_profile_flags_forbidden_model(self):
        report = tools.check_profile(
            {
                "constraints": {"region": "EU-only", "forbidden_providers": ["anthropic"]},
                "routing_preferences": {"simple": ["gpt-4o-mini"], "medium": ["claude-sonnet"], "complex": ["gemini-2.5-pro"]},
            }
        )
        self.assertIn("medium", [i["tier"] for i in report["issues"]])


class AgentLoopTest(unittest.TestCase):
    def setUp(self):
        self._original = contract_agent._call_llm

    def tearDown(self):
        contract_agent._call_llm = self._original

    def test_mode_b_requirement_driven(self):
        """模式 B：合约只写需求 → agent 查 providers → 查 coverage → 按能力选型 → finalize。"""
        finalize_args = {
            "customer_name": "华康医疗集团",
            "use_case": "互联网医院智能分诊与病历摘要",
            "objective": "low_cost",
            "constraints": {
                "region": "CN-only",
                "privacy_tier": "high",
                "forbidden_providers": ["openai", "anthropic", "google"],
                "allowed_providers": ["deepseek", "glm"],
            },
            "performance": {"latency_target_ms": 1200, "cost_sensitivity": "high"},
            "routing_preferences": {
                "simple": ["deepseek-v3"],
                "medium": ["deepseek-v3"],
                "complex": ["deepseek-v3"],
            },
            "warnings": [
                {
                    "type": "model_gap",
                    "severity": "warning",
                    "tier": "complex",
                    "message": "CN 合规目录无 complex 模型，降级到 deepseek-v3",
                }
            ],
        }
        fake = ScriptedLLM(
            [
                _resp(_tool_call("list_providers", {})),
                _resp(_tool_call("check_coverage", {"constraints": finalize_args["constraints"]}, "call_2")),
                _resp(_tool_call("list_models", {"tier": "medium", "provider": "deepseek"}, "call_3")),
                _resp(_tool_call("check_profile", {"profile": finalize_args}, "call_4")),
                _resp(_tool_call("finalize", finalize_args, "call_5")),
            ]
        )
        contract_agent._call_llm = fake

        messages_seen: list[list[dict]] = []

        async def tracking(messages, **kwargs):
            messages_seen.append(list(messages))
            return await fake(messages)

        contract_agent._call_llm = tracking

        import asyncio

        profile = asyncio.run(contract_agent.run_react_agent("合约正文", "华康医疗集团"))

        # 三轮工具结果必须回填，agent 才能继续推理
        self.assertEqual(fake.calls, 5)
        self.assertGreater(len(messages_seen[-1]), 5)

        # 输出必须满足合约约束
        self.assertEqual(profile.constraints.region, "CN-only")
        for tier in ["simple", "medium", "complex"]:
            self.assertEqual(profile.routing_preferences[tier], ["deepseek-v3"])
            for model in profile.routing_preferences[tier]:
                info = tools.get_model(model)
                self.assertEqual(info["provider"], "deepseek")
        self.assertTrue(any(w.get("type") == "model_gap" for w in profile.warnings))

    def test_finalize_strips_forbidden_and_hallucinated_models(self):
        """agent 若选出违约/不存在模型，finalize 清洗必须剔除并补 gap warning。"""
        finalize_args = {
            "customer_name": "Helios Energy",
            "use_case": "grid analytics",
            "objective": "high_quality",
            "constraints": {
                "region": "EU-only",
                "privacy_tier": "high",
                "forbidden_providers": ["google", "deepseek"],
                "allowed_providers": ["anthropic", "openai"],
            },
            "performance": {"latency_target_ms": 2000, "cost_sensitivity": "low"},
            "routing_preferences": {
                "simple": ["claude-haiku", "gemini-2.0-flash"],   # google 违约
                "medium": ["gpt-4o"],
                "complex": ["gemini-2.5-pro", "claude-opus-4"],   # 违约 + 幻觉
            },
            "warnings": [],
        }
        contract_agent._call_llm = ScriptedLLM([_resp(_tool_call("finalize", finalize_args))])

        import asyncio

        profile = asyncio.run(contract_agent.run_react_agent("合约正文", "Helios Energy"))

        self.assertEqual(profile.routing_preferences["simple"], ["claude-haiku"])
        self.assertEqual(profile.routing_preferences["medium"], ["gpt-4o"])
        self.assertEqual(profile.routing_preferences["complex"], [])
        self.assertTrue(
            any(w.get("type") == "model_gap" and w.get("tier") == "complex" for w in profile.warnings)
        )

    def test_malformed_tool_arguments_fed_back(self):
        """工具参数 JSON 损坏时不能中断 Agent，应把错误回灌给模型重试。"""
        finalize_args = {
            "customer_name": "Loop Corp",
            "use_case": "test",
            "objective": "low_cost",
            "constraints": {
                "region": "any",
                "privacy_tier": "standard",
                "forbidden_providers": [],
                "allowed_providers": [],
            },
            "performance": {"latency_target_ms": 3000, "cost_sensitivity": "medium"},
            "routing_preferences": {
                "simple": ["gpt-4o-mini"],
                "medium": ["claude-sonnet"],
                "complex": ["gemini-2.5-pro"],
            },
            "warnings": [],
        }
        bad = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {"name": "list_models", "arguments": '{"tier": "simp'},
                            }
                        ],
                    }
                }
            ]
        }
        fake = ScriptedLLM([bad, _resp(_tool_call("finalize", finalize_args, "call_2"))])

        messages_seen: list[list[dict]] = []

        async def tracking(messages, **kwargs):
            messages_seen.append(list(messages))
            return await fake(messages)

        contract_agent._call_llm = tracking

        import asyncio

        profile = asyncio.run(contract_agent.run_react_agent("合约正文", "Loop Corp"))

        self.assertEqual(profile.customer_id, "loop-corp")
        self.assertEqual(fake.calls, 2)
        tool_msgs = [m for m in messages_seen[-1] if m.get("role") == "tool"]
        self.assertTrue(any("Invalid JSON arguments" in m["content"] for m in tool_msgs))

    def test_unknown_tool_fed_back(self):
        """模型编造工具名时不能抛错中断，应返回可用工具清单让它重试。"""
        finalize_args = {
            "customer_name": "Loop Corp",
            "use_case": "test",
            "objective": "low_cost",
            "constraints": {
                "region": "any",
                "privacy_tier": "standard",
                "forbidden_providers": [],
                "allowed_providers": [],
            },
            "performance": {"latency_target_ms": 3000, "cost_sensitivity": "medium"},
            "routing_preferences": {
                "simple": ["gpt-4o-mini"],
                "medium": ["claude-sonnet"],
                "complex": ["gemini-2.5-pro"],
            },
            "warnings": [],
        }
        fake = ScriptedLLM(
            [_resp(_tool_call("delete_model", {"name": "gpt-4o"})), _resp(_tool_call("finalize", finalize_args, "call_2"))]
        )

        messages_seen: list[list[dict]] = []

        async def tracking(messages, **kwargs):
            messages_seen.append(list(messages))
            return await fake(messages)

        contract_agent._call_llm = tracking

        import asyncio

        profile = asyncio.run(contract_agent.run_react_agent("合约正文", "Loop Corp"))

        self.assertEqual(profile.customer_id, "loop-corp")
        tool_msgs = [m for m in messages_seen[-1] if m.get("role") == "tool"]
        self.assertTrue(any("Available tools" in m["content"] for m in tool_msgs))

    def test_rejects_on_non_convergence(self):
        """反复调用工具直到轮次预算 → 强制 finalize 也失败时抛错（由上层回退单次抽取）。"""
        fake = ScriptedLLM(
            [_resp(_tool_call("list_providers", {})) for _ in range(contract_agent.AGENT_MAX_ITERS)]
        )
        contract_agent._call_llm = fake

        import asyncio

        with self.assertRaises(RuntimeError):
            asyncio.run(contract_agent.run_react_agent("合约正文", "Loop Corp"))


    def test_token_budget_forces_finalize(self):
        """token 硬预算触发后应复用已有上下文强制 finalize，而不是丢弃结果。"""
        finalize_args = {
            "customer_name": "Budget Corp",
            "use_case": "support bot",
            "objective": "low_cost",
            "constraints": {"region": "EU-only", "allowed_providers": ["anthropic", "openai"]},
            "performance": {"latency_target_ms": 2000, "cost_sensitivity": "medium"},
            "routing_preferences": {
                "simple": ["gpt-4o-mini"],
                "medium": ["gpt-4o"],
                "complex": ["claude-sonnet"],
            },
        }
        first = _resp(_tool_call("list_providers", {}))
        first["usage"] = {"prompt_tokens": 50000, "completion_tokens": 50000}
        forced = _resp(_tool_call("finalize", finalize_args, "call_2"))
        forced["usage"] = {"prompt_tokens": 1000, "completion_tokens": 100}

        fake = ScriptedLLM([first, forced])
        seen_kwargs: list[dict] = []

        async def tracking(messages, **kwargs):
            seen_kwargs.append(kwargs)
            return await fake(messages)

        contract_agent._call_llm = tracking

        import asyncio

        profile = asyncio.run(contract_agent.run_react_agent("合约正文", "Budget Corp"))

        self.assertEqual(profile.extraction["finalized_by"], "forced")
        self.assertEqual(profile.extraction["budget_hit"], "tokens")
        self.assertEqual(profile.extraction["llm_calls"], 2)
        self.assertEqual(seen_kwargs[-1]["tool_choice"]["function"]["name"], "finalize")


if __name__ == "__main__":
    unittest.main(verbosity=2)
