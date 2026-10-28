import json
import logging
import time
from pathlib import Path

import httpx

from backend.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_DISABLE_THINKING,
    EXTRACTION_MODEL,
    FALLBACK_PROFILES_DIR,
)
from backend.models import CustomerProfile, slugify
from backend.services.profile_policy import (
    build_extraction_metrics,
    normalize_warnings,
    sanitize_routing_preferences,
)
from backend.services.provider_registry import get_active_catalog

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Extract an AI routing profile from this contract. Output ONLY raw JSON — no markdown, no explanation.

<contract>
{contract_text}
</contract>

<custom_instructions>
{custom_instructions}
</custom_instructions>

<environment>
Providers in this environment: {available_providers}

Models by tier:
{models_by_tier}
</environment>

Output this exact JSON schema:
{{
  "customer_name": "<short company name>",
  "use_case": "<3-6 word description>",
  "objective": "<one of: low_latency | high_quality | low_cost>",
  "constraints": {{
    "region": "<one of: EU-only | US-only | any>",
    "privacy_tier": "<one of: low | standard | high>",
    "forbidden_providers": [],
    "allowed_providers": []
  }},
  "performance": {{
    "latency_target_ms": <integer>,
    "cost_sensitivity": "<one of: low | medium | high>"
  }},
  "routing_preferences": {{
    "simple": ["<model_name>", "<model_name>"],
    "medium": ["<model_name>", "<model_name>"],
    "complex": ["<model_name>", "<model_name>"]
  }},
  "warnings": [
    {{
      "type": "<one of: provider_gap | model_gap | region_gap | missing_field | contract_ambiguity>",
      "severity": "<one of: critical | warning | info>",
      "message": "<short actionable message>"
    }}
  ]
}}

RULES:

1. TERSE VALUES:
   - customer_name: company name only
   - use_case: max 6 words

2. PROVIDERS vs MODELS are DIFFERENT things:
   - forbidden_providers / allowed_providers → PROVIDER names: {available_providers}
   - routing_preferences → MODEL names from the tier lists above
   - NEVER mix them up

3. PROVIDERS:
   - forbidden_providers: only if contract EXPLICITLY bans a provider (e.g. "China-based" → ["deepseek"])
   - allowed_providers: only if contract EXPLICITLY restricts to specific providers. Empty [] means all allowed.

4. ROUTING PREFERENCES — respect model tiers:
   - The models above are grouped by tier (simple/medium/complex). This is their CONFIGURED tier.
   - routing_preferences["simple"]/["medium"]/["complex"] should PREFER models from that tier's list
   - If a tier has NO compatible model after applying constraints, reuse the best compatible model from an adjacent tier and add a model_gap warning
   - Pick 1-2 models per tier that are compatible with the contract constraints (allowed providers, region)

5. LATENCY: use contract value if specified, else default: low_latency=1000, high_quality=5000, low_cost=3000

6. WARNINGS — structured objects, only for actionable issues:
   - provider_gap: contract requires a provider not deployed (e.g. "Contract requires Anthropic but no anthropic models in environment")
   - model_gap: a tier has no compatible models after applying constraints
   - region_gap: required region not supported by available models
   - missing_field: contract doesn't specify something important (latency, region, etc.)
   - contract_ambiguity: contract is unclear about a routing-relevant requirement
   - Do NOT warn about compliance, legal, auditing, retention, or anything outside AI routing
   - severity "critical" = blocks routing, "warning" = degraded routing, "info" = FYI"""


async def _chat(client: httpx.AsyncClient, messages: list[dict]) -> tuple[str, dict]:
    """调用 DeepSeek，返回（回复文本, usage）。"""
    response = await client.post(
        f"{DEEPSEEK_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": EXTRACTION_MODEL,
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": 1200,
            **({"thinking": {"type": "disabled"}} if DEEPSEEK_DISABLE_THINKING else {}),
        },
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"] or "", data.get("usage") or {}


def _parse_profile_json(content: str) -> dict:
    """把模型输出解析为 JSON 对象，容忍 markdown 代码围栏。"""
    text = (content or "").strip()

    # Strip markdown code blocks if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("extraction output is not a JSON object")
    return data


async def extract_profile(
    customer_name: str, contract_text: str, custom_instructions: str = ""
) -> CustomerProfile:
    catalog = get_active_catalog()

    # Group models by tier for the prompt
    tiers: dict[str, list[str]] = {"simple": [], "medium": [], "complex": []}
    for name, info in catalog.items():
        tier = info.get("tier", "medium")
        desc = f"{name} (provider: {info['provider']}, ${info.get('cost_per_m_input', 0):.2f}/MTok, {info.get('avg_latency_ms', 0)}ms)"
        tiers.setdefault(tier, []).append(desc)

    models_by_tier_lines = []
    for tier in ["simple", "medium", "complex"]:
        models_by_tier_lines.append(f"  {tier}: {', '.join(tiers.get(tier, ['none']))}")
    models_by_tier = "\n".join(models_by_tier_lines)

    # Compute available providers
    providers = sorted(set(info["provider"] for info in catalog.values()))

    prompt = EXTRACTION_PROMPT.format(
        contract_text=contract_text,
        custom_instructions=custom_instructions or "None",
        models_by_tier=models_by_tier,
        available_providers=", ".join(providers),
    )

    started = time.perf_counter()
    prompt_tokens = 0
    completion_tokens = 0
    llm_calls = 0

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            content, usage = await _chat(client, [{"role": "user", "content": prompt}])
            llm_calls += 1
            prompt_tokens += int(usage.get("prompt_tokens") or 0)
            completion_tokens += int(usage.get("completion_tokens") or 0)
            try:
                profile_data = _parse_profile_json(content)
            except (json.JSONDecodeError, ValueError) as e:
                # 模型输出不是合法 JSON：追加一轮修复提示，避免直接失败
                logger.warning(f"Extraction output is not valid JSON ({e}); retrying with repair prompt")
                repair_messages = [{"role": "user", "content": prompt}]
                if content.strip():
                    repair_messages.append({"role": "assistant", "content": content})
                repair_messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Your previous output is not valid JSON. Reply with ONLY the raw JSON object "
                            "required by the original instructions. No markdown fences, no explanation."
                        ),
                    }
                )
                content, usage = await _chat(client, repair_messages)
                llm_calls += 1
                prompt_tokens += int(usage.get("prompt_tokens") or 0)
                completion_tokens += int(usage.get("completion_tokens") or 0)
                profile_data = _parse_profile_json(content)

        customer_id = slugify(customer_name)

        profile = CustomerProfile(
            customer_id=customer_id,
            customer_name=profile_data.get("customer_name", customer_name),
            use_case=profile_data.get("use_case", "general"),
            objective=profile_data.get("objective", "low_cost"),
            constraints=profile_data.get("constraints", {}),
            performance=profile_data.get("performance", {}),
            routing_preferences=profile_data.get("routing_preferences", {
                "simple": ["gpt-4o-mini"],
                "medium": ["claude-sonnet"],
                "complex": ["gemini-2.5-pro"],
            }),
            warnings=profile_data.get("warnings", []),
        )

        # 单次抽取同样经过合规清理与 warning 归一化，避免绕过 Agent 的校验
        sanitize_routing_preferences(profile)
        normalize_warnings(profile)
        profile.extraction = build_extraction_metrics(
            mode="single_shot",
            llm_calls=llm_calls,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            elapsed_ms=int((time.perf_counter() - started) * 1000),
        )
        return profile

    except Exception as e:
        logger.error(f"Extraction failed: {type(e).__name__}: {e!r}")
        fallback = _load_fallback(customer_name)
        if fallback:
            logger.info(f"Using fallback profile for {customer_name}")
            fallback.extraction = build_extraction_metrics(
                mode="fallback_file",
                llm_calls=llm_calls,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                elapsed_ms=int((time.perf_counter() - started) * 1000),
            )
            return fallback
        raise


def _load_fallback(customer_name: str) -> CustomerProfile | None:
    slug = slugify(customer_name)
    fallback_path = FALLBACK_PROFILES_DIR / f"{slug}.json"
    if fallback_path.exists():
        return CustomerProfile.model_validate_json(fallback_path.read_text())

    # Try matching by filename
    for f in FALLBACK_PROFILES_DIR.glob("*.json"):
        if slug in f.stem or f.stem in slug:
            return CustomerProfile.model_validate_json(f.read_text())

    return None
