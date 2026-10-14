# ModelGate Audit Report

**Contract-Aware AI Control Plane**
KSU Social Good Hackathon 2026 -- Assurant Track

Audited: 2026-03-20
Auditor: Technical audit against requirements-report.md

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Detailed Audit by Category](#detailed-audit-by-category)
3. [Bug Report](#bug-report)
4. [Gap Analysis — Prioritized](#gap-analysis--prioritized)

---

## Executive Summary

Overall the codebase is substantially complete. The backend has solid coverage of the core routing, extraction, proxy, and logging flows. The frontend is polished with charts, badges, and dark-theme styling. Seed data and fallback profiles exist. The main gaps that would hurt a demo are: (1) no profile edit/approve step, (2) no copy-to-clipboard on the endpoint URL, (3) the endpoint URL is hardcoded to `localhost:8000` which breaks on any deployment, (4) the model registry enable/disable toggle doesn't actually affect routing, and (5) a real bug where `cost_per_1k_input` is referenced but doesn't exist in the catalog. No Dockerfile exists. No PUT/PATCH endpoint exists for editing customer profiles.

**Requirement coverage (MUST-priority only):**
- DONE: ~118 / 152
- PARTIAL: ~22 / 152
- MISSING: ~12 / 152

---

## Detailed Audit by Category

### CORE -- Core Product Functionality

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| CORE-01 | MUST | DONE | System is clearly framed as a contract-aware onboarding + inference control plane |
| CORE-02 | MUST | DONE | Two phases implemented: extraction/onboarding and runtime routing |
| CORE-03 | MUST | PARTIAL | Accepts contract text and custom instructions. Does NOT accept separate SLA, privacy, or product docs as distinct uploads -- single file only |
| CORE-04 | MUST | DONE | Produces structured profile, routing config, endpoint URL, and dashboard |
| CORE-05 | MUST | DONE | Per-request routing via classify_prompt + route() on every proxy call |
| CORE-06 | MUST | PARTIAL | System works and exposes OpenAI-compatible endpoint. However, no Dockerfile exists -- not Docker-deployable yet |
| CORE-07 | MUST | PARTIAL | No Dockerfile or docker-compose. Cannot deploy as Docker image |
| CORE-08 | MUST | DONE | Framing is correct throughout |
| CORE-09 | MUST | DONE | No carbon routing present |
| CORE-10 | MUST | DONE | Automated onboarding, contract-based routing |
| CORE-11 | MUST | DONE | No RL anywhere |
| CORE-12 | MUST | DONE | No autoscaling/GPU management |
| CORE-13 | NICE | DONE | Not implemented, not needed |
| CORE-14 | MUST | DONE | Clear path: contract -> profile -> endpoint |
| CORE-15 | SHOULD | PARTIAL | Architecture is clean but no explicit callouts for where DLP/compliance would slot in |

### CONTRACT -- Contract Extraction and Profile Generation

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| CONTRACT-01 | MUST | DONE | Upload via `/extract/upload` accepts files |
| CONTRACT-02 | MUST | PARTIAL | No separate SLA upload -- everything goes in one file |
| CONTRACT-03 | MUST | PARTIAL | No separate privacy doc upload -- single file |
| CONTRACT-04 | SHOULD | PARTIAL | No separate product notes field -- single file only |
| CONTRACT-05 | MUST | DONE | Custom instructions text field exists |
| CONTRACT-06 | MUST | DONE | Extraction prompt asks for all listed fields |
| CONTRACT-07 | MUST | DONE | Uses Claude Sonnet via OpenRouter to extract structured output |
| CONTRACT-08 | MUST | DONE | Output is structured JSON CustomerProfile |
| CONTRACT-09 | SHOULD | MISSING | No estimated prompt mix (% simple/medium/complex) in extraction output or profile |
| CONTRACT-10 | MUST | DONE | Agent analyzes documents and produces full profile |
| CONTRACT-11 | MUST | DONE | Custom instructions field supplements missing data |
| CONTRACT-12 | MUST | DONE | Short contracts used, no vector search |
| CONTRACT-13 | NICE | MISSING | Not implemented (expected) |
| CONTRACT-14 | NICE | MISSING | Not implemented (expected) |
| CONTRACT-15 | NICE | MISSING | Not implemented (expected) |
| CONTRACT-16 | SHOULD | DONE | Warnings field captures ambiguities |
| CONTRACT-17 | SHOULD | DONE | Warnings displayed in extraction result and profile pages |
| CONTRACT-18 | MUST | DONE | routing_preferences in extraction output maps tiers to models |
| CONTRACT-19 | SHOULD | MISSING | No "end-user interaction types" field in profile |
| CONTRACT-20 | MUST | PARTIAL | Classification happens at runtime, but extraction does not produce a predicted complexity distribution |

### CUSTOMER -- Customer Management

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| CUSTOMER-01 | MUST | DONE | "Onboard Customer" button exists on customers page and navbar |
| CUSTOMER-02 | MUST | DONE | Unique customer_id generated from name via slugify |
| CUSTOMER-03 | MUST | DONE | Profile contains metadata, constraints, preferences, routing_preferences |
| CUSTOMER-04 | MUST | DONE | Profile is the durable config powering routing |
| CUSTOMER-05 | MUST | MISSING | No review/approval step -- profile is auto-saved immediately on extraction. No "pending" vs "approved" state |
| CUSTOMER-06 | MUST | MISSING | No edit/override UI. No PUT/PATCH endpoint for customer profiles |
| CUSTOMER-07 | SHOULD | DONE | Profiles are isolated per customer_id |
| CUSTOMER-08 | MUST | DONE | Endpoint URL shown on customer profile page |
| CUSTOMER-09 | MUST | DONE | Stats and logs visible per customer |
| CUSTOMER-10 | MUST | DONE | Constraints include region, privacy_tier, forbidden_providers, allowed_providers |
| CUSTOMER-11 | MUST | DONE | Performance includes latency_target_ms, cost_sensitivity |
| CUSTOMER-12 | MUST | DONE | routing_preferences maps simple/medium/complex to model lists |
| CUSTOMER-13 | MUST | DONE | use_case field exists |
| CUSTOMER-14 | MUST | DONE | objective field exists |
| CUSTOMER-15 | MUST | DONE | Multiple customers supported simultaneously |
| CUSTOMER-16 | MUST | DONE | Profiles are reusable configurations |
| CUSTOMER-17 | MUST | DONE | Contract updates out of scope as expected |

### ROUTING -- Model Routing Logic

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| ROUTING-01 | MUST | DONE | Static profile + dynamic per-request classification |
| ROUTING-02 | MUST | DONE | Static context used in route() |
| ROUTING-03 | MUST | DONE | Dynamic prompt classification via classify_prompt() |
| ROUTING-04 | NICE | MISSING | No provider health/latency/budget checking at runtime |
| ROUTING-05 | MUST | DONE | Hybrid: policy filter then scoring/classification |
| ROUTING-06 | MUST | DONE | Policy filter eliminates forbidden/non-allowed providers and wrong regions |
| ROUTING-07 | MUST | DONE | _score_and_select picks best from valid candidates |
| ROUTING-08 | MUST | DONE | Simple queries route to cheap/fast models (gpt-4o-mini, claude-haiku) |
| ROUTING-09 | MUST | DONE | Complex queries route to stronger models |
| ROUTING-10 | MUST | DONE | Region filtering enforced in route() |
| ROUTING-11 | MUST | DONE | Forbidden providers filtered |
| ROUTING-12 | MUST | DONE | Tier escalation logic exists |
| ROUTING-13 | MUST | DONE | Route() receives profile + prompt + uses MODEL_CATALOG |
| ROUTING-14 | MUST | DONE | Returns RoutingDecision with model, provider, reason |
| ROUTING-15 | MUST | DONE | Reason string explains routing choice |
| ROUTING-16 | MUST | DONE | Customer profile passed per-request |
| ROUTING-17 | SHOULD | DONE | Single classifier model serves all customers |
| ROUTING-18 | MUST | DONE | Classifies as simple/medium/complex |
| ROUTING-19 | SHOULD | DONE | Fallback via tier escalation and catalog scan |
| ROUTING-20 | SHOULD | DONE | _score_and_select considers objective and cost sensitivity |
| ROUTING-21 | MUST | PARTIAL | Classification is heuristic-based (or local Arch-Router model), not frontier-model-based as spec describes. Works but less intelligent |
| ROUTING-22 | NICE | DONE | Uses Arch-Router-1.5B when available (small classification model) |
| ROUTING-23 | MUST | DONE | Region filtering respects region-specific restrictions |

### MODEL -- Model Registry and Configuration

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| MODEL-01 | MUST | DONE | MODEL_CATALOG with 7 models across 4 providers |
| MODEL-02 | MUST | PARTIAL | Providers are hardcoded in MODEL_CATALOG, not configurable at deployment |
| MODEL-03 | MUST | DONE | Each provider has models listed |
| MODEL-04 | MUST | DONE | Description field captures what each model is suited for |
| MODEL-05 | MUST | DONE | cost_per_m_input/output pricing exists |
| MODEL-06 | MUST | DONE | avg_latency_ms exists |
| MODEL-07 | MUST | DONE | tier field (simple/medium/complex) exists |
| MODEL-08 | MUST | PARTIAL | API key is a single OPENROUTER_API_KEY, not per-provider. Works via OpenRouter but not configurable per-provider in UI |
| MODEL-09 | SHOULD | PARTIAL | Global model enable/disable exists in DB, but router_engine does NOT check get_enabled_models() -- toggling has no effect on routing |
| MODEL-10 | MUST | DONE | OpenAI, Anthropic, Google all present |
| MODEL-11 | NICE | DONE | DeepSeek included |
| MODEL-12 | SHOULD | PARTIAL | Can disable models via UI toggle, but the toggle doesn't actually affect routing (see MODEL-09) |
| MODEL-13 | MUST | DONE | Concrete model names mapped (claude-haiku, gpt-4o-mini, etc.) |
| MODEL-14 | MUST | DONE | Model capabilities documented via description, tier, cost, latency |

### PROXY -- OpenAI-Compatible Proxy Endpoint

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| PROXY-01 | MUST | DONE | `/v1/{customer_id}/chat/completions` endpoint |
| PROXY-02 | MUST | DONE | Customer-specific endpoint URL using customer_id |
| PROXY-03 | MUST | DONE | Format matches spec |
| PROXY-04 | MUST | DONE | Standard request accepted, forwarded transparently |
| PROXY-05 | MUST | DONE | Accepts standard messages array |
| PROXY-06 | MUST | DONE | Returns OpenRouter/provider response directly |
| PROXY-07 | MUST | DONE | Classify -> Route -> Forward -> Return |
| PROXY-08 | MUST | DONE | Full log entry saved with all required fields |
| PROXY-09 | MUST | PARTIAL | Customer identified by URL path segment only -- no API key auth. Acceptable for demo |
| PROXY-10 | SHOULD | DONE | Classification is fast (heuristic or local model) |
| PROXY-11 | MUST | DONE | Forwards to OpenRouter with correct model ID |
| PROXY-12 | NICE | MISSING | No streaming support |

### UI-DASH -- Dashboard / Overview

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| UI-DASH-01 | MUST | DONE | Full web dashboard with Next.js |
| UI-DASH-02 | MUST | DONE | Extracted decisions are legible -- routing reasons shown |
| UI-DASH-03 | MUST | DONE | Customer overview with request counts and links |
| UI-DASH-04 | SHOULD | DONE | Customer cards on customers page |
| UI-DASH-05 | SHOULD | DONE | Tier badges (simple/medium/complex) throughout |
| UI-DASH-06 | SHOULD | DONE | Route explanation labels in logs and playground |
| UI-DASH-07 | SHOULD | DONE | Latency/cost charts on dashboard and customer pages |
| UI-DASH-08 | MUST | DONE | Built with Next.js |
| UI-DASH-09 | MUST | DONE | Polished dark theme with glow effects, animations, gradients |

### UI-CUSTOMER -- Customer Pages

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| UI-CUSTOMER-01 | MUST | DONE | File upload with drag-and-drop |
| UI-CUSTOMER-02 | MUST | DONE | Custom instructions text area |
| UI-CUSTOMER-03 | SHOULD | MISSING | No per-customer allowed provider configuration on intake page |
| UI-CUSTOMER-04 | MUST | DONE | "Extract Profile" button triggers extraction |
| UI-CUSTOMER-05 | MUST | DONE | Extracted requirements displayed in profile result card and profile page |
| UI-CUSTOMER-06 | MUST | DONE | Objective shown |
| UI-CUSTOMER-07 | MUST | DONE | Region/privacy constraints shown |
| UI-CUSTOMER-08 | MUST | DONE | Recommended model plan shown (routing_preferences) |
| UI-CUSTOMER-09 | SHOULD | MISSING | No estimated request mix (% simple/medium/complex) displayed |
| UI-CUSTOMER-10 | SHOULD | DONE | Warnings displayed with amber styling |
| UI-CUSTOMER-11 | MUST | PARTIAL | Endpoint URL is displayed on profile page but: (1) hardcoded to `localhost:8000`, (2) no copy-to-clipboard button |
| UI-CUSTOMER-12 | MUST | MISSING | No edit/override functionality on profile page. No approve button. Profile auto-saves on extraction |
| UI-CUSTOMER-13 | SHOULD | PARTIAL | Cost and latency by model charts exist, but no predicted tradeoff comparison before deployment |
| UI-CUSTOMER-14 | SHOULD | PARTIAL | Model distribution chart shows usage after requests, but no "most used model" prediction |
| UI-CUSTOMER-15 | NICE | MISSING | No estimated RPS or traffic expectations |
| UI-CUSTOMER-16 | MUST | DONE | Customer list page shows all customers |
| UI-CUSTOMER-17 | NICE | MISSING | No "user types" display |

### UI-LOGS -- Request Logs and Analytics

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| UI-LOGS-01 | MUST | DONE | Request log table with timeline chart |
| UI-LOGS-02 | MUST | DONE | Route chosen shown per request |
| UI-LOGS-03 | MUST | DONE | Model/provider shown |
| UI-LOGS-04 | MUST | DONE | Latency and TTFT shown |
| UI-LOGS-05 | MUST | DONE | Tokens used and cost estimate shown |
| UI-LOGS-06 | MUST | DONE | "Why this route" explanation in expandable row |
| UI-LOGS-07 | MUST | DONE | Classification badge (simple/medium/complex) |
| UI-LOGS-08 | MUST | DONE | Customer-scoped log view |
| UI-LOGS-09 | SHOULD | PARTIAL | Logs are customer-scoped by navigating to /customers/{id}/logs. There is also /logs for all, but no dropdown filter on the global view |
| UI-LOGS-10 | MUST | DONE | Cost savings vs premium shown on dashboard and customer profile (savings metric card) |
| UI-LOGS-11 | SHOULD | DONE | Avg latency by model chart on customer profile |
| UI-LOGS-12 | SHOULD | MISSING | No policy compliance rate metric |
| UI-LOGS-13 | SHOULD | MISSING | No "onboarding config generated in <30 seconds" headline stat |
| UI-LOGS-14 | MUST | DONE | Cost savings percentage shown on dashboard banner |
| UI-LOGS-15 | MUST | DONE | Tier distribution chart shows simple requests routed to cheaper models |
| UI-LOGS-16 | SHOULD | MISSING | No explicit "region constraints respected 100%" metric |
| UI-LOGS-17 | SHOULD | DONE | Token usage card on customer profile page |
| UI-LOGS-18 | SHOULD | DONE | Avg latency shown per customer |

### UI-PLAYGROUND -- Playground / Testing Interface

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| UI-PLAYGROUND-01 | MUST | DONE | Send test prompts through customer endpoint and see results |
| UI-PLAYGROUND-02 | MUST | PARTIAL | Results shown sequentially in history, not side-by-side comparison view |
| UI-PLAYGROUND-03 | MUST | DONE | Routing explanation shown for each prompt ("Why:" label) |
| UI-PLAYGROUND-04 | MUST | PARTIAL | Token/cost/latency shown per prompt, but no comparison table between prompts |
| UI-PLAYGROUND-05 | NICE | MISSING | No ChatGPT-style app |
| UI-PLAYGROUND-06 | MUST | DONE | Quick prompts provided (simple, medium, complex) |
| UI-PLAYGROUND-07 | MUST | DONE | Model selected and why shown in routing decision panel |

### UI-MODELS -- Model Registry UI

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| UI-MODELS-01 | MUST | DONE | Models page shows all providers |
| UI-MODELS-02 | MUST | DONE | Models listed per provider with enable/disable toggle |
| UI-MODELS-03 | SHOULD | DONE | Cost tier, latency, context size, regions, description all shown |
| UI-MODELS-04 | SHOULD | PARTIAL | Toggle exists but doesn't affect routing (router_engine doesn't check enabled state) |
| UI-MODELS-05 | MUST | PARTIAL | API key is configured via .env file (OPENROUTER_API_KEY), not via UI |

### FLOW -- End-to-End Workflow Steps

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| FLOW-01 | MUST | PARTIAL | No Docker image. Provider config is .env + hardcoded catalog. start.sh exists |
| FLOW-02 | MUST | DONE | "Onboard Customer" flow with upload + custom instructions |
| FLOW-03 | MUST | DONE | Extraction layer processes docs and outputs structured profile |
| FLOW-04 | MUST | DONE | Profile becomes the durable routing config |
| FLOW-05 | MUST | MISSING | No review/approve step. Profile is auto-saved immediately after extraction |
| FLOW-06 | MUST | PARTIAL | Endpoint URL generated and shown, but no explicit "approve" step creates it. URL is hardcoded to localhost |
| FLOW-07 | MUST | DONE | Runtime routing works: classify -> filter -> select -> log -> return |
| FLOW-08 | MUST | DONE | Full path implemented |
| FLOW-09 | MUST | PARTIAL | Missing Docker, missing profile review step |
| FLOW-10 | MUST | DONE | Product team just changes the URL |
| FLOW-11 | MUST | DONE | Upload contract, get profile -- the flow works |

### API -- Backend API Endpoints

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| API-01 | MUST | DONE | POST /extract/upload creates customer from file |
| API-02 | MUST | DONE | Extraction triggered as part of POST /extract/upload |
| API-03 | MUST | DONE | GET /customers/{id} returns profile |
| API-04 | MUST | MISSING | No PUT/PATCH endpoint for updating customer profiles |
| API-05 | MUST | MISSING | No explicit approve/finalize endpoint |
| API-06 | MUST | DONE | POST /v1/{customer_id}/chat/completions |
| API-07 | MUST | DONE | GET /customers lists all |
| API-08 | MUST | DONE | GET /logs/{customer_id} |
| API-09 | SHOULD | DONE | GET /stats/{customer_id} and GET /stats |
| API-10 | MUST | PARTIAL | GET /models and PUT /models/{name} exist, but no CREATE/DELETE and toggle doesn't affect routing |
| API-11 | MUST | PARTIAL | Endpoint URL is constructed client-side, not returned from an API endpoint. Hardcoded to localhost |
| API-12 | MUST | DONE | Python FastAPI backend |
| API-13 | MUST | DONE | Extraction pipeline in services/extractor.py |
| API-14 | MUST | DONE | Routing layer in services/router_engine.py |
| API-15 | SHOULD | DONE | GET /stats returns global dashboard metrics |

### DATA -- Data Models and Storage

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| DATA-01 | MUST | DONE | CustomerProfile schema matches spec |
| DATA-02 | MUST | DONE | RequestLogEntry schema matches spec with extras |
| DATA-03 | MUST | DONE | MODEL_CATALOG has provider, models, cost, latency, regions |
| DATA-04 | MUST | DONE | SQLite database |
| DATA-05 | MUST | PARTIAL | Upload endpoint reads file content but does not persist the file to filesystem |
| DATA-06 | MUST | DONE | Request logs in SQLite |
| DATA-07 | MUST | DONE | routing_preferences maps tiers to preferred + fallback models |
| DATA-08 | MUST | DONE | constraints block with latency_target_ms and cost_preference |
| DATA-09 | MUST | DONE | Timestamp captured |
| DATA-10 | SHOULD | DONE | input_tokens and output_tokens tracked |

### DEMO -- Demo-Specific Requirements

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| DEMO-01 | MUST | N/A | Process requirement, not code |
| DEMO-02 | MUST | PARTIAL | Flow works but missing the review/approve step |
| DEMO-03 | MUST | N/A | Pitch content, not code |
| DEMO-04 | MUST | DONE | Two sample contracts exist (ACME Support, Globex Claims) |
| DEMO-05 | SHOULD | DONE | ACME and Globex are realistic Assurant-style customer scenarios |
| DEMO-06 | MUST | DONE | Sample contracts are short (< 1 page each) |
| DEMO-07 | MUST | DONE | Quick prompts in playground (simple, medium, complex) |
| DEMO-08 | MUST | DONE | Different routes shown for different complexity prompts |
| DEMO-09 | MUST | DONE | Routing explanation shown in playground and logs |
| DEMO-10 | MUST | PARTIAL | Token/cost/latency shown per request, but no side-by-side comparison view |
| DEMO-11 | MUST | DONE | Fallback profiles exist for both demo customers |
| DEMO-12 | SHOULD | PARTIAL | start.sh exists but no Docker image for easy deployment |
| DEMO-13 | SHOULD | DONE | Sample contracts available for testing |
| DEMO-14 | MUST | N/A | Pitch content, not code |
| DEMO-15 | MUST | N/A | Pitch content, not code |
| DEMO-16 | MUST | PARTIAL | Cost savings shown. Missing: "onboarding in <30s", "region constraints 100%", "cost reduction %" as headline stats |
| DEMO-17 | MUST | N/A | Rehearsal, not code |
| DEMO-18 | SHOULD | DONE | Two use cases: customer support (ACME) and claims analysis (Globex) |
| DEMO-19 | MUST | DONE | System is functional, not mockups |
| DEMO-20 | MUST | N/A | Timeline, not code |
| DEMO-21 | MUST | N/A | Admin task, not code |
| DEMO-22 | MUST | DONE | Framed as policy-aware routing |
| DEMO-23 | MUST | DONE | No carbon/generic router framing |
| DEMO-24 | MUST | DONE | Correctly framed |

---

## Bug Report

### BUG-01: KeyError in router_engine._score_and_select() [CRITICAL]

**File:** `/home/cbak/programming/ksu-sg-hackathon/backend/services/router_engine.py` lines 127, 135

The scoring function references `info["cost_per_1k_input"]` but the MODEL_CATALOG uses `cost_per_m_input`. This will cause a **KeyError** at runtime when:
- Customer objective is `low_cost` (line 127)
- Customer cost_sensitivity is `high` (line 135)

This means routing for cost-optimized customers (like ACME Support with `cost_sensitivity: high`) will crash.

**Fix:** Change `cost_per_1k_input` to `cost_per_m_input` on both lines.

### BUG-02: Model Registry Toggle Has No Effect [IMPORTANT]

**File:** `/home/cbak/programming/ksu-sg-hackathon/backend/database.py` (defines `get_enabled_models()`)
**File:** `/home/cbak/programming/ksu-sg-hackathon/backend/services/router_engine.py` (never calls it)

The `get_enabled_models()` function is defined but never imported or called in the router engine. Toggling a model off in the UI does nothing -- the router will still select disabled models.

**Fix:** Import and use `get_enabled_models()` in `router_engine.route()` to filter candidates.

### BUG-03: Endpoint URL Hardcoded to localhost [IMPORTANT]

**File:** `/home/cbak/programming/ksu-sg-hackathon/frontend/src/app/customers/[id]/page.tsx` line 48

```typescript
const endpointUrl = `http://localhost:8000/v1/${profile.customer_id}/chat/completions`;
```

This breaks on any non-local deployment. Should dynamically detect the host, similar to how `api.ts` uses `window.location.hostname`.

---

## Gap Analysis -- Prioritized

### 1. CRITICAL GAPS -- Must Fix for Demo

These gaps block the core demo story or will cause runtime failures.

| # | Gap | Requirements | Impact | Effort |
|---|-----|-------------|--------|--------|
| C1 | **BUG: `cost_per_1k_input` KeyError** in router_engine.py | ROUTING-08, ROUTING-20 | Runtime crash for cost-optimized customers (ACME). Will fail during live demo | 5 min |
| C2 | **No profile edit/approve step** -- profile auto-saves on extraction with no review | CUSTOMER-05, CUSTOMER-06, FLOW-05, API-04, API-05 | Breaks the core demo narrative: "upload -> review -> approve -> deploy". Judges expect to see human-in-the-loop | 2-3 hrs |
| C3 | **No PUT/PATCH endpoint** for customer profiles | API-04 | Backend prerequisite for C2 | 30 min |
| C4 | **Endpoint URL hardcoded to localhost:8000** | UI-CUSTOMER-11, FLOW-06, API-11 | Shows wrong URL if deployed anywhere. Looks unprofessional | 15 min |
| C5 | **No copy-to-clipboard on endpoint URL** | UI-CUSTOMER-11 | The endpoint URL is THE product deliverable. Users need to copy it easily | 15 min |

### 2. IMPORTANT GAPS -- Should Fix

These significantly improve the demo quality and story completeness.

| # | Gap | Requirements | Impact | Effort |
|---|-----|-------------|--------|--------|
| I1 | **Model registry toggle doesn't affect routing** | MODEL-09, MODEL-12, UI-MODELS-04 | Judges will try toggling models off and see no effect. Breaks model governance story | 30 min |
| I2 | **No Dockerfile** | CORE-06, CORE-07, FLOW-01 | Can't demonstrate "deploy our Docker image" story. Limits judge access | 1-2 hrs |
| I3 | **No side-by-side comparison in playground** | UI-PLAYGROUND-02, UI-PLAYGROUND-04, DEMO-10 | Spec calls for side-by-side simple vs complex. Current sequential view is less impactful | 1-2 hrs |
| I4 | **Headline metrics missing** ("config in <30s", "region 100%", cost reduction %) | UI-LOGS-13, UI-LOGS-16, DEMO-16 | These are the "wow" numbers for the pitch. Currently only cost savings shown | 1 hr |
| I5 | **API key configuration only via .env** | UI-MODELS-05 | Judges can't configure providers via UI. Minor for demo if pre-configured | 1 hr |
| I6 | **No estimated prompt mix in profile** (% simple/medium/complex) | CONTRACT-09, UI-CUSTOMER-09 | Missing from extraction output. Would strengthen the "we understand your contract" story | 1 hr |
| I7 | **Uploaded contract file not persisted** to filesystem | DATA-05 | Contract text is extracted but the original file is discarded. No way to re-view it | 30 min |

### 3. MINOR GAPS -- Nice to Fix

Polish items that improve quality but aren't critical for the 5-minute demo.

| # | Gap | Requirements | Impact | Effort |
|---|-----|-------------|--------|--------|
| M1 | No per-customer allowed provider configuration on intake form | UI-CUSTOMER-03 | SHOULD priority -- extraction handles it via contract text |
| M2 | No policy compliance rate metric | UI-LOGS-12 | SHOULD priority -- could be computed from logs |
| M3 | No explicit "end-user interaction types" field | CONTRACT-19 | SHOULD priority -- covered implicitly by use_case |
| M4 | Playground results sequential, not side-by-side | UI-PLAYGROUND-02 | Already in I3 above |
| M5 | No global log filter dropdown (only per-customer logs) | UI-LOGS-09 | Minor UX gap |
| M6 | No streaming support | PROXY-12 | NICE priority |
| M7 | Separate document type uploads (SLA, privacy, product notes) | CONTRACT-02, CONTRACT-03, CONTRACT-04 | For demo, single file is sufficient |
| M8 | Predicted cost/latency tradeoffs before deployment | UI-CUSTOMER-13 | Would be impressive but not critical |

---

## Recommended Fix Priority Order

For maximum demo impact with limited time:

1. **C1** -- Fix `cost_per_1k_input` bug (5 minutes, prevents runtime crash)
2. **C4 + C5** -- Dynamic endpoint URL + copy button (30 minutes, makes THE product deliverable look professional)
3. **I1** -- Wire model registry toggle to routing (30 minutes, makes model governance actually work)
4. **C2 + C3** -- Add PUT endpoint + edit/approve UI (2-3 hours, completes the core demo narrative)
5. **I4** -- Add headline metrics banner (1 hour, strengthens the pitch)
6. **I3** -- Side-by-side playground comparison (1-2 hours, makes demo more visual)
7. **I2** -- Dockerfile (1-2 hours, enables judge access)

Total estimated time for items 1-5: ~4-5 hours
