DEFAULT_MODELS: dict[str, dict] = {
    "claude-haiku": {
        "provider": "anthropic",
        "openrouter_id": "anthropic/claude-3-5-haiku-20241022",
        "tier": "simple",
        "cost_per_m_input": 0.80,
        "cost_per_m_output": 4.00,
        "avg_latency_ms": 350,
        "regions": ["US", "EU"],
        "max_context": 200000,
        "description": "Fast, affordable model for simple tasks",
    },
    "gpt-4o-mini": {
        "provider": "openai",
        "openrouter_id": "openai/gpt-4o-mini",
        "tier": "simple",
        "cost_per_m_input": 0.15,
        "cost_per_m_output": 0.60,
        "avg_latency_ms": 400,
        "regions": ["US", "EU"],
        "max_context": 128000,
        "description": "Cost-effective model for basic queries",
    },
    "claude-sonnet": {
        "provider": "anthropic",
        "openrouter_id": "anthropic/claude-sonnet-4",
        "tier": "medium",
        "cost_per_m_input": 3.00,
        "cost_per_m_output": 15.00,
        "avg_latency_ms": 900,
        "regions": ["US", "EU"],
        "max_context": 200000,
        "description": "Balanced model for moderate analysis",
    },
    "gpt-4o": {
        "provider": "openai",
        "openrouter_id": "openai/gpt-4o",
        "tier": "medium",
        "cost_per_m_input": 2.50,
        "cost_per_m_output": 10.00,
        "avg_latency_ms": 800,
        "regions": ["US", "EU"],
        "max_context": 128000,
        "description": "Strong general-purpose model",
    },
    "gemini-2.0-flash": {
        "provider": "google",
        "openrouter_id": "google/gemini-2.0-flash-001",
        "tier": "simple",
        "cost_per_m_input": 0.10,
        "cost_per_m_output": 0.40,
        "avg_latency_ms": 300,
        "regions": ["US", "EU"],
        "max_context": 1000000,
        "description": "Ultra-fast, cheapest option for simple tasks",
    },
    "gemini-2.5-pro": {
        "provider": "google",
        "openrouter_id": "google/gemini-2.5-pro-preview-06-05",
        "tier": "complex",
        "cost_per_m_input": 2.50,
        "cost_per_m_output": 15.00,
        "avg_latency_ms": 1500,
        "regions": ["US", "EU"],
        "max_context": 1000000,
        "description": "Advanced reasoning for complex tasks",
    },
    "deepseek-v3": {
        "provider": "deepseek",
        "openrouter_id": "deepseek/deepseek-chat-v3-0324",
        "tier": "medium",
        "cost_per_m_input": 0.30,
        "cost_per_m_output": 0.80,
        "avg_latency_ms": 600,
        "regions": ["CN", "US"],
        "max_context": 128000,
        "description": "Cost-effective Chinese provider model",
    },
}


def get_active_catalog() -> dict[str, dict]:
    """Return DB models if any exist, otherwise return DEFAULT_MODELS."""
    try:
        from backend.database import get_global_models_full
        db_models = get_global_models_full()
        if db_models:
            return db_models
    except Exception:
        pass
    return DEFAULT_MODELS


def get_model_info(model_name: str) -> dict | None:
    return get_active_catalog().get(model_name)


def get_openrouter_id(model_name: str) -> str:
    info = get_active_catalog().get(model_name)
    if info:
        return info["openrouter_id"]
    return model_name


def get_models_for_tier(tier: str) -> list[str]:
    return [name for name, info in get_active_catalog().items() if info["tier"] == tier]


def estimate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    info = get_active_catalog().get(model_name)
    if not info:
        return 0.0
    input_cost = (input_tokens / 1_000_000) * info["cost_per_m_input"]
    output_cost = (output_tokens / 1_000_000) * info["cost_per_m_output"]
    return round(input_cost + output_cost, 8)


def get_all_providers() -> list[str]:
    return list(set(info["provider"] for info in get_active_catalog().values()))


def get_all_model_names() -> list[str]:
    return list(get_active_catalog().keys())
