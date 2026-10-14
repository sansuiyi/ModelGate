import json
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_model = None
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
    global _model, _model_loaded
    try:
        from llama_cpp import Llama
        from backend.config import CLASSIFIER_GGUF_PATH, CLASSIFIER_N_CTX, CLASSIFIER_N_GPU_LAYERS

        if not Path(CLASSIFIER_GGUF_PATH).exists():
            logger.warning(f"GGUF model not found at {CLASSIFIER_GGUF_PATH}")
            logger.warning("Falling back to heuristic classifier")
            _model_loaded = False
            return

        logger.info(f"Loading GGUF classification model: {CLASSIFIER_GGUF_PATH}")
        _model = Llama(
            model_path=CLASSIFIER_GGUF_PATH,
            n_ctx=CLASSIFIER_N_CTX,
            n_gpu_layers=CLASSIFIER_N_GPU_LAYERS,
            verbose=False,
        )
        _model_loaded = True
        logger.info(f"GGUF model loaded (n_gpu_layers={CLASSIFIER_N_GPU_LAYERS}) — running warmup...")

        # Warmup: one inference to initialize CUDA context
        warmup_prompt = _build_arch_prompt("Hello, what is your return policy?")
        _model.create_chat_completion(
            messages=[{"role": "user", "content": warmup_prompt}],
            max_tokens=10,
            temperature=0,
        )
        logger.info("Classification model warmed up and ready")
    except Exception as e:
        logger.warning(f"Failed to load classification model: {e}")
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
            logger.warning(f"Arch Router classification failed: {e}, using heuristic")
    return heuristic_classify(prompt)


def _arch_router_classify(prompt: str) -> str:
    arch_prompt = _build_arch_prompt(prompt)

    output = _model.create_chat_completion(
        messages=[{"role": "user", "content": arch_prompt}],
        max_tokens=30,
        temperature=0,
    )

    response = output["choices"][0]["message"]["content"].strip()

    try:
        parsed = json.loads(response)
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
