"""合同抽取 ReAct Agent 的 system prompt 与工具 JSON schema。"""

SYSTEM_PROMPT = """You are a contract-to-routing-profile agent for an AI model gateway. You turn a customer contract into a valid, self-consistent CustomerProfile.

CRITICAL CONTEXT: Most contracts do NOT name specific models. They specify approved/forbidden providers plus business requirements (latency, privacy, region, cost sensitivity, document length, quality). Your main job is to DERIVE model selection from those requirements.

STEP 0 — CLASSIFY THE CONTRACT:
- Mode A: the contract explicitly names models (rare). Verify and use them if compliant.
- Mode B: the contract only gives providers + requirements (common). You must select models yourself.

MODE B WORKFLOW (must follow this order):
1. Extract constraints: region (EU-only/US-only/any), privacy_tier, forbidden_providers, allowed_providers.
   Map provider names in any language (深度求索=deepseek, 智谱=glm/zhipu, OpenAI, Anthropic, Google, 字节/bytedance).
   A phrase like "any US-headquartered provider is prohibited" means forbidden_providers must list every US provider present in this environment — check with list_providers first.
2. Extract PER-TIER requirements from the contract (simple / medium / complex). Contracts usually give different targets per tier, e.g. "分诊 1200ms" → simple, "病历摘要 5000ms" → medium, "多学科会诊 10000ms, quality first" → complex. Also capture: cost sensitivity per tier, quality priority, minimum context (e.g. "40 pages of documents" → ~100k tokens), and any ban on lightweight models for a tier.
3. Call check_coverage(constraints) FIRST. It tells you which tiers have zero compliant models under the contract constraints.
4. For each tier, call list_models with the capability filters that match that tier's requirement (max_latency_ms, min_context_tokens, max_cost_per_m_input, sort_by). Narrow until 1-2 best models remain.
5. If a tier has zero candidates even after relaxing cost/latency filters, decide explicitly:
   - If a compliant model from an adjacent tier satisfies the requirement, downgrade/escalate to it and add a model_gap warning.
   - If no compliant model exists at all, still fill the tier with the best compliant model available and add a model_gap warning stating the gap and the risk.
   - NEVER pick a forbidden model to satisfy performance. Compliance always wins.
6. Call check_profile(draft) to self-check. Fix any eliminated model and re-check.
7. Call finalize.

PRIORITY ORDER when requirements conflict:
compliance (region / forbidden / allowed) > privacy > quality > latency > cost.
Never violate compliance for latency or cost.

SELECTION HEURISTICS:
- Cost-sensitive simple tier: choose the cheapest compliant model, then prefer lower latency.
- Quality-first complex tier: choose the highest capability compliant model; latency may be relaxed.
- Long-document needs: require max_context >= required tokens.
- "No lightweight/economy models allowed for this query class": exclude simple-tier models from that tier.
- Prefer models whose avg_latency_ms leaves headroom under the tier's target.

RULES:
- Only reference models that exist in the catalog (verify with get_model when unsure).
- routing_preferences[tier] should PREFER models whose tier equals that tier. Cross-tier fallback is allowed ONLY when a tier has no compliant same-tier model: reuse the best compliant model from an adjacent tier for that tier and add a model_gap warning.
- Record the reasoning for each tier in warnings as structured entries, e.g.
  {"type": "tier_requirement", "severity": "info", "tier": "simple", "message": "contract requires 1200ms & lowest cost; selected deepseek-v3 (600ms, $0.30/M)"}
  and for shortages:
  {"type": "model_gap", "severity": "warning", "tier": "complex", "message": "no compliant complex model; using deepseek-v3, quality risk needs review"}
- Every tool call must bring NEW information. Do not repeat identical queries.
- For simple contracts (Mode A, few constraints), minimize tool calls and finalize quickly.
- You MUST finish by calling finalize."""


def _function(name: str, description: str, properties: dict, required: list[str] | None = None) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
            },
        },
    }


TOOLS_SCHEMA = [
    _function(
        "list_providers",
        "List all provider names available in this environment.",
        {},
    ),
    _function(
        "list_models",
        (
            "List models filtered by structural and capability criteria. Use capability filters to translate "
            "contract requirements (latency targets, document length, cost limits) into model candidates."
        ),
        {
            "tier": {"type": "string", "enum": ["simple", "medium", "complex"]},
            "provider": {"type": "string"},
            "region": {"type": "string", "enum": ["EU", "US", "CN"]},
            "max_latency_ms": {"type": "integer", "description": "Only models with avg latency <= this value"},
            "min_context_tokens": {"type": "integer", "description": "Only models with max_context >= this value"},
            "max_cost_per_m_input": {
                "type": "number",
                "description": "Only models with input cost (USD per 1M tokens) <= this value",
            },
            "sort_by": {"type": "string", "enum": ["latency", "cost", "context"]},
        },
    ),
    _function(
        "get_model",
        "Get full info for a single model by name. Returns null if the model does not exist.",
        {"name": {"type": "string"}},
        ["name"],
    ),
    _function(
        "check_coverage",
        (
            "Given contract constraints, report for each tier which models remain compliant and which tiers have "
            "zero compliant models. Facts only; call this before selecting models."
        ),
        {
            "constraints": {
                "type": "object",
                "properties": {
                    "region": {"type": "string", "enum": ["EU-only", "US-only", "any"]},
                    "privacy_tier": {"type": "string", "enum": ["low", "standard", "high"]},
                    "forbidden_providers": {"type": "array", "items": {"type": "string"}},
                    "allowed_providers": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["region", "forbidden_providers", "allowed_providers"],
            }
        },
        ["constraints"],
    ),
    _function(
        "check_profile",
        "Self-check a draft profile. Returns per-tier valid candidates, eliminated models and issues. Does NOT suggest fixes.",
        {"profile": {"type": "object"}},
        ["profile"],
    ),
    _function(
        "finalize",
        "Submit the final, complete CustomerProfile. Must be the last call.",
        {
            "customer_name": {"type": "string"},
            "use_case": {"type": "string"},
            "objective": {"type": "string", "enum": ["low_latency", "high_quality", "low_cost"]},
            "constraints": {
                "type": "object",
                "properties": {
                    "region": {"type": "string", "enum": ["EU-only", "US-only", "any"]},
                    "privacy_tier": {"type": "string", "enum": ["low", "standard", "high"]},
                    "forbidden_providers": {"type": "array", "items": {"type": "string"}},
                    "allowed_providers": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["region", "privacy_tier", "forbidden_providers", "allowed_providers"],
            },
            "performance": {
                "type": "object",
                "properties": {
                    "latency_target_ms": {"type": "integer"},
                    "cost_sensitivity": {"type": "string", "enum": ["low", "medium", "high"]},
                },
                "required": ["latency_target_ms", "cost_sensitivity"],
            },
            "routing_preferences": {
                "type": "object",
                "properties": {
                    "simple": {"type": "array", "items": {"type": "string"}},
                    "medium": {"type": "array", "items": {"type": "string"}},
                    "complex": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["simple", "medium", "complex"],
            },
            "warnings": {"type": "array", "items": {"type": "object"}},
        },
        ["customer_name", "use_case", "objective", "constraints", "performance", "routing_preferences", "warnings"],
    ),
]
