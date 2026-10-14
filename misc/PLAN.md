# PLAN.md -- Contract-Aware AI Control Plane

## Full Hackathon Build Plan

### Project Name
**ModelGate** — Contract-Aware AI Control Plane

### Timeline
- **Thursday Mar 19, ~7:00 PM -- 11:30 PM** (4.5 hrs) -- Phase 0 + Phase 1
- **Friday Mar 20, all day virtual** (~10 hrs) -- Phase 2 + Phase 3
- **Saturday Mar 21, 10:00 AM -- ~12:30 PM** (2.5 hrs) -- Phase 4 (polish + demo prep)
- **Saturday Mar 21, ~1:00 PM** -- Presentations begin
- **Total working time budget: ~17 hours** (be realistic about sleep and breaks)

---

## 1. Rubric-Driven Priorities

Every decision below is anchored to the rubric from the Assurant PDF (page 16):

| Category | Weight | What earns a 3 |
|---|---|---|
| **Problem Selection** | 25% | Solution for large population of users; connects 3+ aspects of connected world; great improvement; high-impact problem with few existing tech solutions; OR a very well-developed enhancement to something that exists |
| **Planning** | 15% | Well-defined MVP with subsequent iterations; 3+ design artifacts; work distributed across members with alignment to skillsets; iterative builds, small merges |
| **Development** | 35% | Software works without errors; MVP delivered; additional scope beyond MVP delivered |
| **Presentation** | 25% | 3+ personas covered; clearly covers key points without rambling; polished group dynamic; everything within 5 minutes |

**Key takeaway:** Development is 35% -- the software MUST work. Presentation is 25% -- the demo flow must be crisp. Problem Selection is 25% -- the framing must be sharp. Planning is only 15% but they want 3+ artifacts and evidence of iterative work (small commits, distributed tasks).

---

## 2. Tech Stack (Final Decisions)

### Backend: Python FastAPI
- **Why:** Fast to build, excellent for OpenAI-compatible endpoints, Pydantic for data models, easy async support
- **Install:** `pip install fastapi uvicorn[standard] python-multipart pydantic httpx python-dotenv`

### Frontend: Next.js 14 (App Router) with Tailwind CSS + shadcn/ui
- **Why:** Fast scaffolding with `npx create-next-app`, Tailwind gives polished look fast, shadcn/ui provides pre-built components (cards, tables, badges, charts)
- **Install:** `npx create-next-app@latest frontend --typescript --tailwind --app --src-dir --use-npm`

### Storage: SQLite via Python `sqlite3` standard library
- **Why:** Zero config, file-based, ships with Python. No ORM needed for this scope.
- **Contract docs:** stored as files in `data/contracts/`
- **Profiles:** stored in SQLite `customers` table
- **Request logs:** stored in SQLite `request_logs` table

### Prompt Classification: Arch Router 1.5B via vLLM
- **Model:** `katanemo/Arch-Router-1.5B` — purpose-built 1.5B routing model (fine-tuned Qwen2.5-1.5B)
- **Why Arch Router:** 93% routing accuracy, 51ms latency, beats GPT-4o at classification tasks. No fine-tuning needed — route policies are passed at inference time as natural language descriptions.
- **Serving:** vLLM on port 8001 with FP16 (no quantization — model is only ~3GB, RTX 3080 has 8GB VRAM)
- **How it works:** We define route policies (simple/medium/complex with descriptions), send the user prompt + policies, and Arch Router returns `{"route": "simple"}` etc. Fully decoupled from model assignment.
- **Install:** `pip install vllm`
- **Run:** `vllm serve katanemo/Arch-Router-1.5B --dtype float16 --port 8001`
- **Fallback:** If vLLM/Arch Router is down, fall back to keyword + token count heuristic

### LLM Calls: OpenRouter for everything
- **Why:** One API key, one endpoint, all models. No provider-specific SDKs needed.
- **For extraction:** Claude Sonnet via OpenRouter
- **For proxied inference:** All models via OpenRouter (`https://openrouter.ai/api/v1/chat/completions`)
- **One env var:** `OPENROUTER_API_KEY`
- All calls go through `httpx.post()` to OpenRouter — no Anthropic SDK, no OpenAI SDK

### File Upload for Contract Intake
- Drag-and-drop file upload (TXT/PDF) in the dashboard
- Reads file contents, passes to extraction LLM
- Flashier for demo — shows how simple the onboarding process is

### Deployment: Local with NVIDIA GPU
- All services run locally on a machine with an NVIDIA GPU (RTX 3080 or similar)
- vLLM (Arch Router) on port 8001, FastAPI on port 8000, Next.js on port 3000
- Deployment script (`scripts/start.sh`) to launch all three services
- No Docker — fewer breaking points for a hackathon

---

## 3. Directory Structure

```
ksu-sg-hackathon/
|-- PLAN.md
|-- README.md
|-- ASSURANT_CONTRACT_AWARE_AI_CONTROL_PLANE_SPEC.md
|-- assurant_hackathon_2026.pdf
|
|-- backend/
|   |-- main.py                      # FastAPI app entry point, CORS, mount routers
|   |-- requirements.txt
|   |-- config.py                    # API keys, model registry, constants
|   |-- database.py                  # SQLite init, connection helpers
|   |-- models.py                    # Pydantic models
|   |
|   |-- routers/
|   |   |-- customers.py             # CRUD endpoints for customer profiles
|   |   |-- extraction.py            # Contract upload + LLM extraction endpoint
|   |   |-- proxy.py                 # OpenAI-compatible proxy endpoint (per-customer)
|   |   |-- logs.py                  # Request log query endpoints
|   |
|   |-- services/
|   |   |-- extractor.py             # LLM-based contract -> profile extraction
|   |   |-- classifier.py            # Prompt complexity classification
|   |   |-- router_engine.py         # Policy filter + model selection logic
|   |   |-- provider_registry.py     # Available models/providers + capabilities
|   |
|   |-- data/
|   |   |-- contracts/               # Uploaded contract files
|   |   |-- sample_contracts/        # Pre-built demo contracts
|   |   |   |-- acme_support.txt
|   |   |   |-- globex_claims.txt
|   |   |-- fallback_profiles/       # Static fallback profiles if extraction fails
|   |   |   |-- acme_support.json
|   |   |   |-- globex_claims.json
|   |   |-- controlplane.db          # SQLite database (gitignored)
|
|-- frontend/
|   |-- src/
|   |   |-- app/
|   |   |   |-- page.tsx             # Landing / customer list
|   |   |   |-- layout.tsx           # Root layout with nav
|   |   |   |-- customers/
|   |   |   |   |-- page.tsx         # Customer list view
|   |   |   |   |-- new/
|   |   |   |   |   |-- page.tsx     # Upload/intake form (View A)
|   |   |   |   |-- [id]/
|   |   |   |   |   |-- page.tsx     # Customer profile detail (View B)
|   |   |   |   |   |-- logs/
|   |   |   |   |   |   |-- page.tsx # Request logs for customer (View C)
|   |   |   |-- playground/
|   |   |   |   |-- page.tsx         # Simple chat/prompt tester against customer endpoint
|   |   |-- components/
|   |   |   |-- CustomerCard.tsx
|   |   |   |-- ProfileView.tsx
|   |   |   |-- ConstraintBadges.tsx
|   |   |   |-- RoutingTable.tsx
|   |   |   |-- RequestLogTable.tsx
|   |   |   |-- MetricsCharts.tsx
|   |   |   |-- FileUpload.tsx
|   |   |   |-- Navbar.tsx
|   |   |-- lib/
|   |   |   |-- api.ts               # Fetch helpers for backend
|   |   |   |-- types.ts             # TypeScript types matching backend models
|
|-- docs/
|   |-- architecture.png             # System diagram (design artifact)
|   |-- demo-script.md               # 5-minute demo script
|   |-- personas.md                  # 3 personas writeup
|
|-- .gitignore
|-- .env.example
```

---

## 4. Phased Build Plan

### PHASE 0: Scaffolding + Foundation (Thursday 7:00 PM -- 8:30 PM) [1.5 hrs]

**Goal:** Both frontend and backend runnable with hello-world endpoints. Git repo initialized.

| Task | Owner | Time |
|---|---|---|
| Create `.gitignore`, push to GitHub | Aaryan | 10 min |
| Create `backend/` scaffold: `main.py` with FastAPI hello world, `requirements.txt`, install deps | Aaryan | 20 min |
| Install vLLM, download Arch Router model, verify it serves on port 8001 | Aaryan | 30 min |
| Write `backend/config.py` -- model registry (OpenRouter model IDs), API key loading from env | Aaryan | 20 min |
| Create `frontend/` scaffold: `npx create-next-app`, add Tailwind, add shadcn/ui, verify runs | Pradyu | 30 min |
| Write `backend/models.py` with all Pydantic models | Danny | 30 min |
| Write `backend/database.py` -- SQLite init, create tables, basic CRUD helpers | Danny | 30 min |
| Create `.env.example`, sample contract files in `data/sample_contracts/` | Danny | 20 min |

**Checkpoint:** `git commit` -- "scaffold: backend FastAPI + frontend Next.js + Arch Router serving"

---

### PHASE 1: Core Backend Logic (Thursday 8:30 PM -- 11:30 PM) [3 hrs]

**Goal:** The three backend brain modules work: extraction, classification, routing. Customer CRUD exists. OpenAI-compatible proxy endpoint accepts requests.

| Task | Owner | Time |
|---|---|---|
| `backend/services/provider_registry.py` -- hardcoded model catalog with capabilities, costs, latency estimates, regions | Person A | 30 min |
| `backend/services/extractor.py` -- LLM call that takes contract text + custom instructions, returns structured CustomerProfile JSON | Person A | 60 min |
| `backend/services/classifier.py` -- classify prompt via Arch Router (vLLM on port 8001); define route policies for simple/medium/complex; fallback to keyword heuristic if vLLM is down | Person C | 45 min |
| `backend/services/router_engine.py` -- given CustomerProfile + classification + provider registry, filter invalid providers, score remaining, pick best, return decision with explanation | Person C | 60 min |
| `backend/routers/customers.py` -- GET /customers, GET /customers/{id}, POST /customers, DELETE /customers/{id} | Person D | 30 min |
| `backend/routers/extraction.py` -- POST /extract (upload files + custom instructions, calls extractor, saves profile) | Person D | 30 min |
| `backend/routers/proxy.py` -- POST /v1/{customer_id}/chat/completions (OpenAI-compatible: classifies prompt, routes, proxies to real provider, logs, returns response) | Person A | 45 min |
| `backend/routers/logs.py` -- GET /logs/{customer_id} (returns request log entries) | Person D | 15 min |
| Write fallback static profiles in `data/fallback_profiles/` | Person C | 15 min |

**Checkpoint:** `git commit` -- "core: extraction, routing, proxy endpoints functional"

**CRITICAL:** Test the proxy endpoint with `curl` before going to sleep. If this works, you have a demoable product even without a frontend.

---

### PHASE 2: Frontend -- Views A, B, C (Friday, morning/afternoon) [5 hrs]

**Goal:** The dashboard has three working views: intake, profile, and logs/metrics.

**Team split:** Two people on frontend, two people on backend hardening + beyond-MVP features.

**Frontend tasks:**

| Task | Owner | Time |
|---|---|---|
| `frontend/src/lib/api.ts` + `types.ts` -- API client and TypeScript types | Person B | 30 min |
| `Navbar.tsx` + `layout.tsx` -- navigation shell with project branding | Person B | 20 min |
| **View A -- Customer Intake** (`customers/new/page.tsx`): file upload form, custom instructions textarea, allowed/forbidden providers checkboxes, "Extract Profile" button, loading state, show result | Person B | 90 min |
| `FileUpload.tsx` component -- drag-and-drop or click-to-upload, shows file names | Person B | 30 min |
| **View B -- Customer Profile** (`customers/[id]/page.tsx`): display extracted profile with ConstraintBadges, routing preference table, warnings, edit fields | Person D | 90 min |
| `ProfileView.tsx`, `ConstraintBadges.tsx`, `RoutingTable.tsx` components | Person D | (included above) |
| **Customer List** (`customers/page.tsx`): cards for each customer, click to view profile | Person D | 30 min |
| `CustomerCard.tsx` -- shows name, use case, objective, constraint summary | Person D | 20 min |

**Backend hardening tasks (parallel):**

| Task | Owner | Time |
|---|---|---|
| Add error handling + fallback to extractor (if LLM fails, load fallback profile) | Person A | 30 min |
| Add cost estimation to routing decisions (lookup model pricing, estimate based on token count) | Person A | 30 min |
| Add latency measurement to proxy endpoint (time the actual provider call, store in log) | Person A | 20 min |
| Write second sample contract (`globex_claims.txt` with stricter privacy) | Person C | 20 min |
| Integration test: end-to-end curl script that uploads contract, extracts, sends prompts, checks logs | Person C | 30 min |

**Checkpoint:** `git commit` -- "frontend: intake, profile, and list views working"

---

### PHASE 3: Frontend View C + Playground + Polish (Friday, afternoon/evening) [5 hrs]

**Goal:** Runtime metrics view works. Prompt playground exists for live demo. Visual polish.

| Task | Owner | Time |
|---|---|---|
| **View C -- Request Logs** (`customers/[id]/logs/page.tsx`): table of requests with model, latency, cost, explanation | Person B | 60 min |
| `RequestLogTable.tsx` -- sortable table with route explanation column | Person B | 30 min |
| `MetricsCharts.tsx` -- simple bar charts: requests by model, avg latency by tier, cost savings vs always-premium | Person B | 60 min |
| **Playground** (`playground/page.tsx`): select customer, type prompt, send, see response + routing decision side-by-side | Person D | 90 min |
| Add summary stats endpoint: `GET /stats/{customer_id}` | Person A | 30 min |
| Polish: loading skeletons, error toasts, empty states, consistent spacing | Person B + D | 30 min |
| Add "Why this route?" popover/tooltip on log entries | Person D | 20 min |
| Seed database with 15-20 pre-generated request logs for demo | Person C | 30 min |
| Write `docs/demo-script.md` with exact steps, talking points, who says what | Person C | 30 min |
| Write `docs/personas.md` documenting the 3 personas | Person C | 20 min |
| Create/update `README.md` for GitHub submission | Person C | 20 min |

**Checkpoint:** `git commit` -- "feature-complete: all views, playground, metrics"

---

### PHASE 4: Beyond-MVP + Demo Prep (Saturday 10:00 AM -- 12:30 PM) [2.5 hrs]

**Goal:** Polish, rehearse, prepare fallbacks. Add one "beyond MVP" feature for the 3-point Development score.

**Beyond-MVP candidates (pick 1-2):**

| Feature | Effort | Impact |
|---|---|---|
| Side-by-side route comparison: send same prompt to cheap vs premium model, show latency/cost/quality diff | 60 min | HIGH -- very visual for demo |
| Cost savings dashboard: running total of "money saved by not always using premium" | 30 min | HIGH -- Assurant loves waste reduction |
| Provider health simulation: toggle a provider "unhealthy" and show automatic rerouting | 45 min | HIGH -- reliability story |
| Profile diff/edit: edit extracted profile fields inline, save overrides | 45 min | MEDIUM |

**Demo prep:**

| Task | Owner | Time |
|---|---|---|
| Rehearse full 5-minute demo at least twice | ALL | 30 min |
| Pre-load demo data: 2 customers with profiles, 20+ request logs each | Person C | 15 min |
| Test extraction with live LLM call -- verify it works or switch to fallback | Person A | 15 min |
| Prepare offline fallback: if API keys fail, have pre-recorded GIF/screenshots | Person C | 20 min |
| Final commit, push to GitHub, verify repo is public | Person A | 10 min |
| Time the presentation -- must be under 5 minutes | ALL | 15 min |

**Checkpoint:** `git commit` -- "release: final polish, demo data, beyond-MVP features"

---

## 5. Data Models (Pydantic -- `backend/models.py`)

```python
class CustomerConstraints(BaseModel):
    region: str = "any"                          # "EU-only", "US-only", "any"
    privacy_tier: str = "standard"               # "low", "standard", "high"
    forbidden_providers: list[str] = []
    allowed_providers: list[str] = []            # empty = all allowed

class CustomerPerformance(BaseModel):
    latency_target_ms: int = 3000
    cost_sensitivity: str = "medium"             # "low", "medium", "high"

class CustomerProfile(BaseModel):
    customer_id: str
    customer_name: str
    use_case: str
    objective: str                               # "low_latency", "high_quality", "low_cost"
    constraints: CustomerConstraints
    performance: CustomerPerformance
    routing_preferences: dict[str, list[str]]    # {"simple": [...], "medium": [...], "complex": [...]}
    warnings: list[str] = []
    created_at: str

class RequestLogEntry(BaseModel):
    id: int
    customer_id: str
    timestamp: str
    prompt_preview: str                          # first 100 chars
    classification: str                          # "simple", "medium", "complex"
    selected_provider: str
    selected_model: str
    reason: str
    latency_ms: int
    estimated_cost: float
    tokens_used: int

class RoutingDecision(BaseModel):
    selected_provider: str
    selected_model: str
    classification: str
    reason: str
    candidates_considered: list[str]
    candidates_eliminated: dict[str, str]        # model -> reason eliminated

class ExtractionRequest(BaseModel):
    customer_name: str
    contract_text: str
    custom_instructions: str = ""

class CustomerStats(BaseModel):
    total_requests: int
    avg_latency_ms: float
    total_cost: float
    cost_savings_vs_premium: float
    model_distribution: dict[str, int]
    requests_by_tier: dict[str, int]
```

---

## 6. Provider Registry (hardcoded for MVP)

```python
MODEL_CATALOG = {
    "claude-haiku": {
        "provider": "anthropic",
        "tier": "simple",
        "cost_per_1k_tokens": 0.00025,
        "avg_latency_ms": 300,
        "regions": ["US", "EU"],
        "max_context": 200000,
    },
    "gpt-4o-mini": {
        "provider": "openai",
        "tier": "simple",
        "cost_per_1k_tokens": 0.00015,
        "avg_latency_ms": 350,
        "regions": ["US", "EU"],
        "max_context": 128000,
    },
    "claude-sonnet": {
        "provider": "anthropic",
        "tier": "medium",
        "cost_per_1k_tokens": 0.003,
        "avg_latency_ms": 800,
        "regions": ["US", "EU"],
        "max_context": 200000,
    },
    "gpt-4o": {
        "provider": "openai",
        "tier": "medium",
        "cost_per_1k_tokens": 0.0025,
        "avg_latency_ms": 900,
        "regions": ["US", "EU"],
        "max_context": 128000,
    },
    "claude-opus": {
        "provider": "anthropic",
        "tier": "complex",
        "cost_per_1k_tokens": 0.015,
        "avg_latency_ms": 2000,
        "regions": ["US", "EU"],
        "max_context": 200000,
    },
}
```

---

## 7. Key Algorithm: Routing Engine (pseudocode)

```
function route(customer_profile, prompt, provider_registry):
    # Step 1: Classify prompt complexity via Arch Router
    # Arch Router receives route policies + user prompt, returns {"route": "simple|medium|complex"}
    complexity = arch_router_classify(prompt, route_policies)  # calls vLLM on port 8001
    # Fallback: if Arch Router is unavailable, use keyword + token count heuristic

    # Step 2: Get candidate models from customer preferences for this tier
    candidates = customer_profile.routing_preferences[complexity]

    # Step 3: Policy filter -- eliminate invalid candidates
    for each candidate in candidates:
        model_info = provider_registry[candidate]
        if model_info.provider in customer_profile.constraints.forbidden_providers:
            eliminate(candidate, "provider forbidden by policy")
        if customer_profile.constraints.allowed_providers is not empty:
            if model_info.provider not in customer_profile.constraints.allowed_providers:
                eliminate(candidate, "provider not in allowlist")
        if customer_profile.constraints.region != "any":
            if required_region not in model_info.regions:
                eliminate(candidate, "region not supported")

    # Step 4: Score remaining candidates
    for each remaining candidate:
        score = 0
        if customer_profile.objective == "low_latency":
            score += (1 / model_info.avg_latency_ms) * 1000
        if customer_profile.objective == "low_cost":
            score += (1 / model_info.cost_per_1k_tokens)
        if customer_profile.objective == "high_quality":
            score += tier_quality_score(model_info.tier)
        if model_info.avg_latency_ms <= customer_profile.performance.latency_target_ms:
            score += 10

    # Step 5: Select highest-scoring candidate
    best = max(remaining_candidates, key=score)

    # Step 6: Build explanation
    reason = f"{complexity} complexity; {best.provider}/{best.model} selected; "
    reason += f"meets latency target; est. cost ${estimated_cost:.4f}"

    return RoutingDecision(...)
```

---

## 8. Arch Router Classification (for `classifier.py`)

The classifier calls Arch Router via vLLM's OpenAI-compatible API on port 8001.

### Route Policies (passed at inference time -- no fine-tuning needed)
```json
[
  {
    "name": "simple",
    "description": "Simple factual questions, greetings, basic lookups, yes/no answers, FAQ-style queries, single-step tasks"
  },
  {
    "name": "medium",
    "description": "Multi-step reasoning, summarization of moderate-length text, data extraction, moderate analysis, comparison tasks"
  },
  {
    "name": "complex",
    "description": "Complex multi-document reasoning, deep analysis, legal/financial interpretation, creative writing, code generation, multi-constraint problem solving"
  }
]
```

### Calling Arch Router via vLLM
```python
import httpx

async def classify_prompt(prompt: str) -> str:
    """Classify prompt complexity via Arch Router served by vLLM."""
    route_policies = [...]  # as above

    arch_prompt = f"""You are a routing assistant. Given the route policies and user message, select the best route.

<route_policies>
{json.dumps(route_policies)}
</route_policies>

<conversation>
[{{"role": "user", "content": {json.dumps(prompt)}}}]
</conversation>

Respond with ONLY valid JSON: {{"route": "route_name"}}"""

    try:
        response = await httpx.AsyncClient().post(
            "http://localhost:8001/v1/chat/completions",
            json={
                "model": "katanemo/Arch-Router-1.5B",
                "messages": [{"role": "user", "content": arch_prompt}],
                "max_tokens": 20,
                "temperature": 0
            },
            timeout=5.0
        )
        result = response.json()["choices"][0]["message"]["content"]
        return json.loads(result)["route"]  # "simple" | "medium" | "complex"
    except Exception:
        return heuristic_classify(prompt)  # fallback
```

### Heuristic Fallback (if vLLM is unavailable)
```python
def heuristic_classify(prompt: str) -> str:
    tokens = len(prompt.split())
    complex_keywords = ["analyze", "compare", "evaluate", "multi", "reasoning", "legal", "compliance"]
    if tokens < 20 and not any(kw in prompt.lower() for kw in complex_keywords):
        return "simple"
    elif tokens > 100 or sum(1 for kw in complex_keywords if kw in prompt.lower()) >= 2:
        return "complex"
    return "medium"
```

---

## 9. Extraction Prompt (for `extractor.py`)

```
You are an AI deployment configuration specialist. Analyze the following
customer contract and supporting documents. Extract a structured AI service
profile.

<contract>
{contract_text}
</contract>

<custom_instructions>
{custom_instructions}
</custom_instructions>

Respond with ONLY valid JSON matching this exact schema:
{
  "customer_name": "...",
  "use_case": "...",
  "objective": "low_latency" | "high_quality" | "low_cost",
  "constraints": {
    "region": "EU-only" | "US-only" | "any",
    "privacy_tier": "low" | "standard" | "high",
    "forbidden_providers": [...],
    "allowed_providers": [...]
  },
  "performance": {
    "latency_target_ms": <number>,
    "cost_sensitivity": "low" | "medium" | "high"
  },
  "routing_preferences": {
    "simple": ["model1", "model2"],
    "medium": ["model1", "model2"],
    "complex": ["model1", "model2"]
  },
  "warnings": ["any concerns or ambiguities found in the contract"]
}

Available models: claude-haiku, gpt-4o-mini, claude-sonnet, gpt-4o, claude-opus

Rules:
- If the contract mentions GDPR, EU data residency, or European customers, set region to "EU-only"
- If the contract mentions PII, PHI, or sensitive data, set privacy_tier to "high"
- Match routing preferences to the objective and cost sensitivity
- List warnings for any ambiguous or missing information
```

---

## 10. Sample Contracts (for `data/sample_contracts/`)

### acme_support.txt
```
ACME Corp AI Services Agreement

This agreement governs the deployment of AI-powered customer support
services for ACME Corp's European customer base.

DATA HANDLING: All customer data must be processed within the European
Union in compliance with GDPR. No customer PII shall be transmitted to
servers outside the EU.

PROVIDERS: The customer approves the use of Anthropic and OpenAI models.
Use of DeepSeek or any China-based AI provider is strictly prohibited.

PERFORMANCE: Support responses must be delivered within 1 second for
standard queries. The system should prioritize response speed over
reasoning depth for routine inquiries.

COST: ACME Corp operates on a cost-sensitive basis. The service should
minimize inference costs while maintaining acceptable quality.

USE CASE: Automated customer support chatbot serving approximately
10,000 queries per day. Estimated 65% simple, 30% medium, 5% complex.
```

### globex_claims.txt
```
Globex Insurance Internal AI Platform Agreement

This agreement covers the deployment of AI assistance tools for Globex
Insurance claims processing team.

DATA HANDLING: All claims data is considered highly sensitive PII/PHI.
Processing may occur in US data centers only. Data must not leave
US jurisdiction.

PROVIDERS: Globex approves Anthropic, OpenAI, and Google as model
providers. No restrictions on specific providers beyond this list.

PERFORMANCE: Claims analysis accuracy is more important than speed.
Analysts may wait up to 5 seconds for a thorough response. The system
should prioritize reasoning quality for complex claims analysis.

COST: Globex has a premium SLA and is willing to pay for higher-quality
model tiers when warranted by query complexity.

USE CASE: Internal tool for 200 claims analysts. Estimated 30% simple
lookups, 40% medium analysis, 30% complex multi-document reasoning.
```

---

## 11. OpenAI-Compatible Proxy Endpoint Design

Endpoint: `POST /v1/{customer_id}/chat/completions`

**Request:**
```json
{
  "model": "auto",
  "messages": [
    {"role": "user", "content": "Summarize this customer complaint..."}
  ]
}
```

The `model` field is ignored -- the control plane decides the model. This is the key value: the calling app does not pick the model; the policy engine does.

**Response:** Standard OpenAI Chat Completion format, with an additional `x-routing-decision` header containing routing explanation JSON.

---

## 12. Team

| Person | Role |
|---|---|
| **Aaryan** | Lead |
| **Pradyu** | Team member |
| **Danny** | Team member |

**Build strategy:** Claude Code builds the full codebase. Team reviews, tests, and handles presentation/demo prep.

---

## 13. Critical Path

```
0. vLLM + Arch Router serving      -- classifier depends on this (port 8001)
1. backend/models.py              -- everything else imports these
2. backend/database.py            -- storage depends on models
3. backend/config.py              -- extraction + routing need API keys + registry
4. backend/services/extractor.py  -- core product feature
5. backend/services/classifier.py -- routing depends on this (calls Arch Router via vLLM)
6. backend/services/router_engine.py -- proxy depends on this
7. backend/routers/proxy.py       -- the core deliverable endpoint
8. frontend/src/lib/api.ts        -- all frontend views need this
9. View A (intake) + View B (profile) -- the demo story
```

If any item on this path breaks, the demo is at risk. Build and test these first.

---

## 14. Fallback Strategies

| Risk | Fallback |
|---|---|
| LLM extraction fails during live demo | Pre-load fallback profiles from `data/fallback_profiles/`. Show extraction as "this is what normally happens" with pre-recorded result. |
| API key rate-limited or down | Have both Anthropic and OpenAI keys. If one fails, route to the other. Keep a cached response for the exact demo prompts. |
| Frontend not finished | Demo via curl/httpie against the API. The proxy endpoint IS the product. Dashboard is sugar. |
| Charts/metrics don't render | Show raw JSON logs in a table. Numbers tell the story. |
| Arch Router / vLLM down | Classifier falls back to keyword + token count heuristic. Code both paths from day one. |
| Arch Router classification inaccurate | Tune route policy descriptions (they're just prompt text). If still bad, override with heuristic for demo prompts. |
| Team member drops out | Person A and C cover backend. Person B covers frontend alone. |
| SQLite corruption | Data is tiny. Wipe and re-seed from sample scripts. Keep seed data in version control. |

---

## 15. Demo Script (5 minutes)

**0:00 -- 0:30 | The Problem (Person D)**
"When an enterprise deploys AI services for different customers, someone manually reads contracts, figures out which models are allowed, what regions data can flow through, what latency and cost targets matter, and wires it all up by hand. That is slow, error-prone, and wasteful."

**0:30 -- 1:30 | Upload + Extract (Person A)**
- Open dashboard, click "New Customer"
- Upload ACME contract doc
- Add custom instruction: "Prioritize response speed"
- Click "Extract Profile"
- Show the structured profile: EU-only, high privacy, DeepSeek forbidden, latency target 1s, cost-sensitive

**1:30 -- 2:15 | Review Profile (Person A)**
- Show View B: full customer AI profile
- Point out routing preferences: simple -> haiku, medium -> sonnet, complex -> opus
- Point out warnings: "contract mentions GDPR; region locked to EU"
- Show the generated endpoint URL

**2:15 -- 3:30 | Live Routing Demo (Person C)**
- Switch to Playground
- Send SIMPLE prompt: "What is your return policy?"
  - Show: routed to claude-haiku, 280ms, $0.0001
- Send COMPLEX prompt: "Analyze this multi-paragraph customer complaint, identify liability exposure, and recommend resolution strategy"
  - Show: routed to claude-opus, 1800ms, $0.012
- Point out: same endpoint, same API format, different models chosen automatically

**3:30 -- 4:15 | Metrics + Value (Person B)**
- Show View C: request log table with explanations
- Show cost comparison: "If every request went to premium model, cost = X. Our routing saved Y%."
- Show model distribution chart

**4:15 -- 5:00 | Close (Person D)**
- "We reduced customer AI onboarding from hours to seconds"
- "We embedded contract constraints directly into routing policy"
- "We eliminated operational waste from over-provisioning expensive models"
- "Three personas benefit: the solutions engineer, the customer, and the ops team"
- "This is a contract-aware AI control plane for enterprise deployment."

---

## 16. Design Artifacts (for Planning score -- need 3+)

1. **System architecture diagram** (`docs/architecture.png`)
2. **Data flow diagram** -- request path from prompt through classification, policy filter, model selection, provider call, response
3. **Database schema** -- SQLite tables: `customers`, `request_logs`
4. **API specification** -- auto-generated from FastAPI `/docs`
5. **This PLAN.md** -- evidence of planning and execution strategy

---

## 17. Presentation Checklist

- [ ] Covers 3+ personas (Solutions Engineer, Enterprise Customer, Ops/Platform Team)
- [ ] No rambling -- each speaker has assigned section and time limit
- [ ] Group dynamic apparent -- multiple speakers, smooth transitions
- [ ] Key points covered: problem, solution, demo, value, Assurant alignment
- [ ] Everything fits within 5 minutes
- [ ] Working software demo (not slides)
- [ ] Mention sustainability: reducing computational waste, right-sizing model usage

---

## 18. Commands Cheat Sheet

```bash
# --- Setup ---
pip install vllm                                    # classification model server
cd backend && pip install -r requirements.txt       # backend deps
cd frontend && npm install                          # frontend deps

# --- Run (3 terminals) ---
vllm serve katanemo/Arch-Router-1.5B --dtype float16 --port 8001   # Terminal 1: classifier
cd backend && uvicorn main:app --reload --port 8000                 # Terminal 2: backend
cd frontend && npm run dev                                          # Terminal 3: frontend

# --- Test extraction ---
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "ACME", "contract_text": "...", "custom_instructions": ""}'

# --- Test proxy endpoint ---
curl -X POST http://localhost:8000/v1/acme-support/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "auto", "messages": [{"role": "user", "content": "What is your return policy?"}]}'

# --- View logs ---
curl http://localhost:8000/logs/acme-support

# --- View stats ---
curl http://localhost:8000/stats/acme-support
```

---

## 19. requirements.txt (backend)

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9
pydantic==2.9.0
openai==1.50.0
anthropic==0.34.0
httpx==0.28.1
python-dotenv==1.0.1
```

---

## 20. Definition of Done (MVP)

- [ ] POST /extract -- upload contract text, get back structured CustomerProfile
- [ ] GET /customers -- list all customer profiles
- [ ] GET /customers/{id} -- get single customer profile
- [ ] POST /v1/{customer_id}/chat/completions -- send prompt, get routed response
- [ ] GET /logs/{customer_id} -- get request history
- [ ] Frontend View A -- file upload + extraction form
- [ ] Frontend View B -- customer profile display with constraints and routing table
- [ ] Frontend View C -- request log table with routing explanations
- [ ] Frontend customer list with cards
- [ ] At least 2 sample customers loaded
- [ ] At least 2 demo prompts that produce different routing decisions
- [ ] Fallback profiles available if extraction fails

---

## 21. What NOT to Build

- No authentication / login system
- No real multi-tenant isolation
- No WebSocket streaming (unless time permits)
- No CI/CD pipeline
- No real provider health checks
- No vector search / RAG over contracts
- No automated testing suite (manual testing is fine)
- No mobile-responsive design (desktop demo only)

---

## 22. Additional Items from Team Discussion

### Research Assurant's actual customers
Create demo contracts modeled after realistic Assurant customer scenarios (insurance claims, device protection, warranty services). Research their real products for authenticity.

### Open WebUI as demo chat app
Deploy Open WebUI pointed at the customer-specific endpoint to show a real end-user chat experience. This simulates what an Assurant customer's users would actually interact with.

### Docker Compose for deployment
Provide a `docker-compose.yml` that spins up vLLM (Arch Router), FastAPI backend, Next.js frontend, and Open WebUI in one command. Judges can deploy with `docker compose up`.

### Public deployment for judges
Deploy the app publicly (e.g., on the demo machine with ngrok or a cloud VM) so judges can access it live. Include a sample contract document they can upload.

### Contract realism
Get input on realistic contract language and structure. Contracts should look real — include sections like "Data Processing Agreement", "Service Level Agreement", "Approved Vendors", "Regional Compliance" etc.
