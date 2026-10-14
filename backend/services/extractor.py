import json
import logging
from pathlib import Path

import httpx

from backend.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, EXTRACTION_MODEL, FALLBACK_PROFILES_DIR
from backend.models import CustomerProfile, slugify
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

4. ROUTING PREFERENCES — MUST respect model tiers:
   - The models above are grouped by tier (simple/medium/complex). This is their CONFIGURED tier.
   - routing_preferences["simple"] MUST only contain models from the "simple" tier list
   - routing_preferences["medium"] MUST only contain models from the "medium" tier list
   - routing_preferences["complex"] MUST only contain models from the "complex" tier list
   - Pick 1-2 models per tier that are compatible with the contract constraints (allowed providers, region)
   - Do NOT put a medium-tier model into the complex routing preference or vice versa

5. LATENCY: use contract value if specified, else default: low_latency=1000, high_quality=5000, low_cost=3000

6. WARNINGS — structured objects, only for actionable issues:
   - provider_gap: contract requires a provider not deployed (e.g. "Contract requires Anthropic but no anthropic models in environment")
   - model_gap: a tier has no compatible models after applying constraints
   - region_gap: required region not supported by available models
   - missing_field: contract doesn't specify something important (latency, region, etc.)
   - contract_ambiguity: contract is unclear about a routing-relevant requirement
   - Do NOT warn about compliance, legal, auditing, retention, or anything outside AI routing
   - severity "critical" = blocks routing, "warning" = degraded routing, "info" = FYI"""


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

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://modelgate.app",
                    "X-Title": "ModelGate",
                },
                json={
                    "model": EXTRACTION_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0,
                    "max_tokens": 1200,
                },
            )
            response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()

        # Strip markdown code blocks if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        profile_data = json.loads(content)
        customer_id = slugify(customer_name)

        return CustomerProfile(
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

    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        fallback = _load_fallback(customer_name)
        if fallback:
            logger.info(f"Using fallback profile for {customer_name}")
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
