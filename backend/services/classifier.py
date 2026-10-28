import json
import logging

import httpx

from backend.config import OLLAMA_BASE_URL, OLLAMA_CLASSIFIER_MODEL

logger = logging.getLogger(__name__)

_model_loaded = False

ROUTE_POLICIES = [
    {
        "name": "simple",
        "description": "Simple factual questions, greetings, basic lookups, yes/no answers, FAQ-style queries, single-step tasks, status checks, straightforward requests",
    },
    {
        "name": "medium",
        "description": "Multi-step reasoning, summarization of moderate-length text, data extraction, moderate analysis, comparison tasks, troubleshooting, explanations requiring some depth",
    },
    {
        "name": "complex",
        "description": "Complex multi-document reasoning, deep analysis, legal or financial interpretation, creative writing, code generation, multi-constraint problem solving, liability assessment, comprehensive evaluation",
    },
]


def load_classifier():
    global _model_loaded
    try:
        with httpx.Client(base_url=OLLAMA_BASE_URL, timeout=10.0) as client:
            resp = client.post(
                "/api/show",
                json={"model": OLLAMA_CLASSIFIER_MODEL},
            )
            resp.raise_for_status()
        _model_loaded = True
        logger.info(
            f"Ollama classifier ready: model={OLLAMA_CLASSIFIER_MODEL} "
            f"({OLLAMA_BASE_URL})"
        )
    except Exception as e:
        logger.warning(f"Failed to reach Ollama classifier: {e}")
        logger.warning("Falling back to heuristic classifier")
        _model_loaded = False


def is_model_loaded() -> bool:
    return _model_loaded


def classify_prompt(prompt: str) -> str:
    # Very short prompts are always simple — skip the model entirely
    stripped = prompt.strip()
    word_count = len(stripped.split())
    if word_count <= 5 and not any(kw in stripped.lower() for kw in ["analyze", "build", "create", "write", "code", "implement"]):
        return "simple"

    if _model_loaded:
        try:
            return _arch_router_classify(prompt)
        except Exception as e:
            logger.warning(f"Ollama classification failed: {e}, using heuristic")
    return heuristic_classify(prompt)


def _arch_router_classify(prompt: str) -> str:
    arch_prompt = _build_arch_prompt(prompt)

    with httpx.Client(base_url=OLLAMA_BASE_URL, timeout=120.0) as client:
        resp = client.post(
            "/api/chat",
            json={
                "model": OLLAMA_CLASSIFIER_MODEL,
                "messages": [{"role": "user", "content": arch_prompt}],
                "stream": False,
                "options": {"temperature": 0},
            },
        )
        resp.raise_for_status()

    response = resp.json()["message"]["content"].strip()

    # Ollama 的 qwen2 模型有时返回单引号 JSON，先规范化
    try:
        parsed = json.loads(response)
        route = parsed.get("route", "medium")
        if route in ("simple", "medium", "complex"):
            return route
    except json.JSONDecodeError:
        pass

    # 兼容单引号 JSON：{'route': 'simple'}
    try:
        normalized = response.replace("'", '"')
        parsed = json.loads(normalized)
        route = parsed.get("route", "medium")
        if route in ("simple", "medium", "complex"):
            return route
    except json.JSONDecodeError:
        pass

    # Regex fallback
    for tier in ("simple", "medium", "complex"):
        if tier in response.lower():
            return tier

    return "medium"


def _build_arch_prompt(prompt: str) -> str:
    policies_json = json.dumps(ROUTE_POLICIES)
    conversation_json = json.dumps([{"role": "user", "content": prompt}])

    return f"""You are a routing assistant. Given the route policies and user message, select the best matching route.

<route_policies>
{policies_json}
</route_policies>

<conversation>
{conversation_json}
</conversation>

Select the best route for this user message. Respond with ONLY valid JSON: {{"route": "route_name"}}"""


def heuristic_classify(prompt: str) -> str:
    tokens = prompt.split()
    token_count = len(tokens)
    prompt_lower = prompt.lower()

    complex_keywords = [
        "analyze", "evaluate", "compare", "assess", "investigate",
        "multi", "comprehensive", "detailed analysis", "liability",
        "legal", "compliance", "financial", "strategy", "recommend",
        "across multiple", "in-depth", "thoroughly", "architect",
        "design", "implement", "build", "create", "develop", "write",
        "refactor", "debug", "optimize", "security", "audit",
        "research", "essay", "report", "review", "critique",
        "feature rich", "production", "full", "complete", "entire",
    ]
    medium_keywords = [
        "explain", "describe", "summarize", "translate", "convert",
        "difference between", "how does", "why does", "list",
        "steps to", "example of", "pros and cons", "rewrite",
    ]
    simple_keywords = [
        "what is", "where is", "when does", "status",
        "hello", "hi ", "hey", "thanks", "help", "faq", "return policy",
        "hours", "price", "cost of", "yes", "no", "ok", "sure",
    ]

    complex_score = sum(1 for kw in complex_keywords if kw in prompt_lower)
    medium_score = sum(1 for kw in medium_keywords if kw in prompt_lower)
    simple_score = sum(1 for kw in simple_keywords if kw in prompt_lower)

    # Code generation is always complex
    code_signals = ["```", "code", "function", "class", "program", "script",
                    "api", "database", "algorithm", "game", "app", "application"]
    code_score = sum(1 for kw in code_signals if kw in prompt_lower)

    # Short greetings/questions are simple
    if token_count <= 5 and complex_score == 0 and code_score == 0 and medium_score == 0:
        return "simple"
    if simple_score > 0 and complex_score == 0 and code_score == 0 and medium_score == 0 and token_count < 20:
        return "simple"

    # Code generation → complex
    if code_score >= 1:
        return "complex"

    # Multiple complex signals or long prompts
    if complex_score >= 2:
        return "complex"
    if complex_score >= 1 and token_count > 25:
        return "complex"
    if token_count > 80:
        return "complex"

    # Medium signals
    if medium_score >= 1 or token_count > 30:
        return "medium"
    if complex_score >= 1:
        return "medium"

    return "simple"
