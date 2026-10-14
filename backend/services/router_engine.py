import logging
from backend.models import CustomerProfile, RoutingDecision
from backend.services.classifier import classify_prompt
from backend.services.provider_registry import get_active_catalog, get_model_info
from backend.database import get_enabled_models

logger = logging.getLogger(__name__)

TIER_QUALITY_SCORES = {"simple": 1, "medium": 2, "complex": 3}
TIER_ESCALATION = {"simple": "medium", "medium": "complex", "complex": "complex"}


def route(profile: CustomerProfile, prompt: str, tier_override: str | None = None) -> RoutingDecision:
    classification = tier_override if tier_override else classify_prompt(prompt)

    candidates = list(profile.routing_preferences.get(classification, []))
    if not candidates:
        candidates = _get_default_candidates(classification)

    # Get the set of enabled models (respects admin toggles)
    enabled_models = set(get_enabled_models())

    eliminated: dict[str, str] = {}
    valid_candidates: list[str] = []

    for model_name in candidates:
        if model_name not in enabled_models:
            eliminated[model_name] = "model disabled by admin"
            continue

        model_info = get_model_info(model_name)
        if model_info is None:
            eliminated[model_name] = "model not found in registry"
            continue

        provider = model_info["provider"]

        if provider in profile.constraints.forbidden_providers:
            eliminated[model_name] = f"provider '{provider}' forbidden by contract"
            continue

        if (
            profile.constraints.allowed_providers
            and provider not in profile.constraints.allowed_providers
        ):
            eliminated[model_name] = f"provider '{provider}' not in allowed list"
            continue

        if profile.constraints.region != "any":
            required_region = profile.constraints.region.replace("-only", "")
            if required_region not in model_info.get("regions", []):
                eliminated[model_name] = f"region '{required_region}' not supported"
                continue

        valid_candidates.append(model_name)

    # If all candidates eliminated, try escalating tier
    if not valid_candidates:
        next_tier = TIER_ESCALATION.get(classification, "complex")
        escalation_candidates = profile.routing_preferences.get(next_tier, [])
        for model_name in escalation_candidates:
            if model_name not in eliminated and model_name in enabled_models:
                model_info = get_model_info(model_name)
                if model_info and _passes_policy(model_info, profile):
                    valid_candidates.append(model_name)

    # Last resort: pick any allowed and enabled model from the catalog
    if not valid_candidates:
        for name, info in get_active_catalog().items():
            if name in enabled_models and _passes_policy(info, profile):
                valid_candidates.append(name)
                break

    if not valid_candidates:
        # Absolute fallback
        valid_candidates = ["gpt-4o-mini"]

    best = _score_and_select(valid_candidates, profile)
    best_info = get_model_info(best) or {}

    reason_parts = [
        f"{classification} complexity",
        f"{best_info.get('provider', '?')}/{best} selected",
    ]

    latency = best_info.get("avg_latency_ms", 0)
    target = profile.performance.latency_target_ms
    if latency <= target:
        reason_parts.append(f"meets {target}ms latency target ({latency}ms avg)")
    else:
        reason_parts.append(f"latency {latency}ms exceeds {target}ms target (best available)")

    reason_parts.append(f"objective: {profile.objective}")
    reason = "; ".join(reason_parts)

    return RoutingDecision(
        selected_provider=best_info.get("provider", "unknown"),
        selected_model=best,
        classification=classification,
        reason=reason,
        candidates_considered=candidates,
        candidates_eliminated=eliminated,
    )


def _passes_policy(model_info: dict, profile: CustomerProfile) -> bool:
    provider = model_info["provider"]
    if provider in profile.constraints.forbidden_providers:
        return False
    if (
        profile.constraints.allowed_providers
        and provider not in profile.constraints.allowed_providers
    ):
        return False
    if profile.constraints.region != "any":
        required_region = profile.constraints.region.replace("-only", "")
        if required_region not in model_info.get("regions", []):
            return False
    return True


def _score_and_select(candidates: list[str], profile: CustomerProfile) -> str:
    scores: dict[str, float] = {}

    for name in candidates:
        info = get_model_info(name)
        if not info:
            continue

        score = 0.0

        if profile.objective == "low_latency":
            score += (1.0 / max(info["avg_latency_ms"], 1)) * 10000
        elif profile.objective == "low_cost":
            score += (1.0 / max(info["cost_per_m_input"], 0.00001)) * 0.01
        elif profile.objective == "high_quality":
            score += TIER_QUALITY_SCORES.get(info["tier"], 1) * 10

        if info["avg_latency_ms"] <= profile.performance.latency_target_ms:
            score += 5

        if profile.performance.cost_sensitivity == "high":
            score += (1.0 / max(info["cost_per_m_input"], 0.00001)) * 0.001

        scores[name] = score

    if not scores:
        return candidates[0]

    return max(scores, key=scores.get)


def _get_default_candidates(tier: str) -> list[str]:
    defaults = {
        "simple": ["gpt-4o-mini", "claude-haiku", "gemini-2.0-flash"],
        "medium": ["claude-sonnet", "gpt-4o"],
        "complex": ["gemini-2.5-pro", "claude-sonnet"],
    }
    return defaults.get(tier, ["gpt-4o-mini"])
