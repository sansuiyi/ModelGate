from pydantic import BaseModel
import re
from datetime import datetime, timezone


class CustomerConstraints(BaseModel):
    region: str = "any"  # "EU-only", "US-only", "any"
    privacy_tier: str = "standard"  # "low", "standard", "high"
    forbidden_providers: list[str] = []
    allowed_providers: list[str] = []  # empty = all allowed


class CustomerPerformance(BaseModel):
    latency_target_ms: int = 3000
    cost_sensitivity: str = "medium"  # "low", "medium", "high"


class CustomerProfile(BaseModel):
    customer_id: str
    customer_name: str
    use_case: str
    objective: str  # "low_latency", "high_quality", "low_cost"
    constraints: CustomerConstraints
    performance: CustomerPerformance
    routing_preferences: dict[str, list[str]]  # {"simple": [...], "medium": [...], "complex": [...]}
    warnings: list = []  # list of str or {"type", "severity", "message"} dicts
    created_at: str = ""

    def model_post_init(self, __context):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.customer_id:
            self.customer_id = slugify(self.customer_name)


class RequestLogEntry(BaseModel):
    id: int = 0
    customer_id: str
    timestamp: str = ""
    prompt_preview: str
    classification: str
    selected_provider: str
    selected_model: str
    reason: str
    latency_ms: int
    estimated_cost: float
    tokens_used: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    ttft_ms: int = 0
    status: str = "success"
    candidates_considered: list[str] = []
    candidates_eliminated: dict[str, str] = {}

    def model_post_init(self, __context):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class RoutingDecision(BaseModel):
    selected_provider: str
    selected_model: str
    classification: str
    reason: str
    candidates_considered: list[str]
    candidates_eliminated: dict[str, str] = {}


class ExtractionRequest(BaseModel):
    customer_name: str
    contract_text: str
    custom_instructions: str = ""


class CustomerStats(BaseModel):
    total_requests: int
    avg_latency_ms: float
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    total_cost: float
    cost_savings_vs_premium: float
    total_tokens: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    avg_ttft_ms: float = 0.0
    success_rate: float = 100.0
    model_distribution: dict[str, int] = {}
    requests_by_tier: dict[str, int] = {}
    provider_distribution: dict[str, int] = {}
    cost_by_model: dict[str, float] = {}
    latency_by_model: dict[str, float] = {}
    hourly_requests: list[dict] = []


class ChatCompletionRequest(BaseModel):
    model: str = "auto"
    messages: list[dict]
    temperature: float = 0.7
    max_tokens: int | None = None


class ChatMessage(BaseModel):
    role: str
    content: str


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug
