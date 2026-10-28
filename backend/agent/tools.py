"""合同抽取 ReAct Agent 的事实核查工具集。

这些工具只提供「事实」（环境里有什么 provider/模型、模型能力如何、
给定约束下每档还剩什么、给定草稿是否自洽），不做任何「决策」。
选型与权衡由 LLM 主导。
"""

from backend.models import CustomerConstraints, CustomerPerformance, CustomerProfile
from backend.services.provider_registry import (
    get_active_catalog,
    get_all_providers,
    get_model_info,
)
from backend.services.router_engine import _evaluate_candidates, _get_default_candidates

TIERS = ["simple", "medium", "complex"]


def _normalize_region(region: str) -> str:
    """把 "EU-only" / "US-only" 归一化为目录里存储的 "EU" / "US"。"""
    return region.replace("-only", "")


def _compact(info: dict, name: str) -> dict:
    """模型精简视图：只暴露选型需要的字段，避免 context 膨胀。"""
    return {
        "name": name,
        "provider": info.get("provider"),
        "tier": info.get("tier"),
        "regions": info.get("regions", []),
        "avg_latency_ms": info.get("avg_latency_ms"),
        "max_context": info.get("max_context"),
        "cost_per_m_input": info.get("cost_per_m_input"),
        "cost_per_m_output": info.get("cost_per_m_output"),
        "description": info.get("description"),
    }


def list_providers() -> list[str]:
    """返回环境里所有 provider 名（不含模型明细，控制 token）。"""
    return sorted(get_all_providers())


def list_models(
    tier: str | None = None,
    provider: str | None = None,
    region: str | None = None,
    max_latency_ms: int | None = None,
    min_context_tokens: int | None = None,
    max_cost_per_m_input: float | None = None,
    sort_by: str | None = None,
) -> list[dict]:
    """按约束与能力需求过滤返回模型精简信息。

    能力维度（max_latency_ms / min_context_tokens / max_cost_per_m_input）用于把合约里的
    「1200ms 内」「支持 40 页文档」「成本优先」这类需求翻译成可执行的筛选条件。
    """
    catalog = get_active_catalog()
    result: list[dict] = []
    for name, info in catalog.items():
        if tier and info.get("tier") != tier:
            continue
        if provider and info.get("provider") != provider:
            continue
        if region:
            required = _normalize_region(region)
            if required not in info.get("regions", []):
                continue
        if max_latency_ms is not None and (info.get("avg_latency_ms") or 0) > max_latency_ms:
            continue
        if min_context_tokens is not None and (info.get("max_context") or 0) < min_context_tokens:
            continue
        if max_cost_per_m_input is not None and (info.get("cost_per_m_input") or 0) > max_cost_per_m_input:
            continue
        result.append(_compact(info, name))

    if sort_by == "latency":
        result.sort(key=lambda m: m["avg_latency_ms"] or 0)
    elif sort_by == "cost":
        result.sort(key=lambda m: m["cost_per_m_input"] or 0)
    elif sort_by == "context":
        result.sort(key=lambda m: -(m["max_context"] or 0))

    return result


def get_model(name: str) -> dict | None:
    """返回单个模型的完整信息；不存在则返回 None（用于防幻觉校验）。"""
    return get_model_info(name)


def _constraints_from(constraints_data: dict) -> CustomerConstraints:
    """只保留场景约束字段，避免调用方传入的未知字段导致校验失败。"""
    return CustomerConstraints(
        region=constraints_data.get("region", "any"),
        privacy_tier=constraints_data.get("privacy_tier", "standard"),
        forbidden_providers=constraints_data.get("forbidden_providers", []),
        allowed_providers=constraints_data.get("allowed_providers", []),
    )


def check_coverage(constraints: dict) -> dict:
    """可行性统计：给定合约约束，返回每档可用模型清单与「无任何合规模型」的档。

    只返回事实——某档为空时是降级还是报缺口，由 agent 推理决定。
    """
    profile = CustomerProfile(
        customer_id="coverage",
        customer_name="coverage",
        use_case="general",
        objective="low_cost",
        constraints=_constraints_from(constraints or {}),
        performance=CustomerPerformance(),
        routing_preferences={},
    )

    catalog = get_active_catalog()
    tiers_report: dict[str, dict] = {}
    gaps: list[str] = []

    for tier in TIERS:
        tier_models = [name for name, info in catalog.items() if info.get("tier") == tier]
        valid, _ = _evaluate_candidates(profile, tier_models)
        tiers_report[tier] = {"available": valid, "count": len(valid)}
        if not valid:
            gaps.append(tier)

    return {"tiers": tiers_report, "gaps": gaps}


def check_profile(profile_data: dict) -> dict:
    """自检工具：输入部分/完整 profile（dict），返回三档候选状态与冲突明细。

    只返回事实，不返回修复建议——怎么修由 agent 自己推理。
    """
    constraints = profile_data.get("constraints") or {}
    performance = profile_data.get("performance") or {}
    prefs = profile_data.get("routing_preferences") or {"simple": [], "medium": [], "complex": []}

    # 用默认值填充缺失字段，构造一个可校验的临时 profile
    profile = CustomerProfile(
        customer_id=profile_data.get("customer_id", "check"),
        customer_name=profile_data.get("customer_name", "check"),
        use_case=profile_data.get("use_case", "general"),
        objective=profile_data.get("objective", "low_cost"),
        constraints=_constraints_from(constraints),
        performance=CustomerPerformance(**performance),
        routing_preferences=prefs,
        warnings=profile_data.get("warnings", []),
    )

    tiers_report: dict[str, dict] = {}
    issues: list[dict] = []

    for tier in TIERS:
        candidates = list(prefs.get(tier, []))
        if not candidates:
            candidates = _get_default_candidates(tier)

        valid, eliminated = _evaluate_candidates(profile, candidates)

        tiers_report[tier] = {
            "candidates": candidates,
            "valid": valid,
            "eliminated": eliminated,
        }

        if not valid:
            issues.append(
                {
                    "tier": tier,
                    "problem": "empty_or_all_eliminated",
                    "eliminated": eliminated,
                }
            )

    return {"tiers": tiers_report, "issues": issues}
