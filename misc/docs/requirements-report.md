# ModelGate Requirements Report

**Contract-Aware AI Control Plane**
KSU Social Good Hackathon 2026 -- Assurant Track

Generated: 2026-03-20
Sources: Team transcript (Mar 19 6:30 PM), Organizer presentations, Project spec (ASSURANT_CONTRACT_AWARE_AI_CONTROL_PLANE_SPEC.md)

---

## Table of Contents

1. [CORE -- Core Product Functionality](#core----core-product-functionality)
2. [CONTRACT -- Contract Extraction and Profile Generation](#contract----contract-extraction-and-profile-generation)
3. [CUSTOMER -- Customer Management](#customer----customer-management)
4. [ROUTING -- Model Routing Logic](#routing----model-routing-logic)
5. [MODEL -- Model Registry and Configuration](#model----model-registry-and-configuration)
6. [PROXY -- OpenAI-Compatible Proxy Endpoint](#proxy----openai-compatible-proxy-endpoint)
7. [UI-DASH -- Dashboard / Overview](#ui-dash----dashboard--overview)
8. [UI-CUSTOMER -- Customer Pages](#ui-customer----customer-pages)
9. [UI-LOGS -- Request Logs and Analytics](#ui-logs----request-logs-and-analytics)
10. [UI-PLAYGROUND -- Playground / Testing Interface](#ui-playground----playground--testing-interface)
11. [UI-MODELS -- Model Registry UI](#ui-models----model-registry-ui)
12. [FLOW -- End-to-End Workflow Steps](#flow----end-to-end-workflow-steps)
13. [API -- Backend API Endpoints](#api----backend-api-endpoints)
14. [DATA -- Data Models and Storage](#data----data-models-and-storage)
15. [DEMO -- Demo-Specific Requirements](#demo----demo-specific-requirements)

---

## CORE -- Core Product Functionality

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| CORE-01 | The system is a contract-aware onboarding and inference control plane for enterprise AI services, not a generic model router | Spec S5, S28 | MUST |
| CORE-02 | The system has two major phases: (A) customer onboarding / policy extraction and (B) runtime routing | Spec S4 | MUST |
| CORE-03 | The system accepts customer contract documents, policy documents, optional custom instructions, and provider availability as inputs | Spec S1 | MUST |
| CORE-04 | The system produces a structured customer AI profile, recommended routing/policy config, an OpenAI-compatible API endpoint, and a dashboard | Spec S1 | MUST |
| CORE-05 | Per-request routing happens at runtime based on customer profile + prompt complexity, not just once at setup time | Spec S6.4, Transcript Part 7 | MUST |
| CORE-06 | The product is a Docker-deployable system that uses agents/extractors + routing logic and exposes an OpenAI-compatible endpoint | Spec S6.2, Transcript Part 4 | MUST |
| CORE-07 | Assurant deploys our Docker image in their own environment/instance | Transcript Part 4, Part 7 | MUST |
| CORE-08 | The system must be framed as improving scalability, reliability, security, and operational efficiency (Assurant challenge criteria) | Spec S2, Organizer transcript | MUST |
| CORE-09 | Carbon-aware routing is dropped as the primary context; it can remain as an optional secondary metric | Spec S6.1, Transcript Part 3 | MUST |
| CORE-10 | The system should reduce manual onboarding work, embed contract constraints into routing, and create a cleaner/cheaper/safer AI deployment surface | Spec S17, S27 | MUST |
| CORE-11 | RL (reinforcement learning) is explicitly out of scope for MVP | Spec S6.8 | MUST |
| CORE-12 | Real autoscaling, GPU management, multi-cloud infra orchestration are explicitly out of scope | Spec S6.6, S18, S24 | MUST |
| CORE-13 | Vector search over documents is optional, not mandatory for the live demo | Spec S6.7, Transcript Part 6 | NICE |
| CORE-14 | The system standardizes the path from signed contract to deployed AI service | Spec S8 | MUST |
| CORE-15 | The architecture should clearly suggest where production features (DLP, legal compliance, secrets management) would slot in, even if not built | Spec S14 | SHOULD |

---

## CONTRACT -- Contract Extraction and Profile Generation

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| CONTRACT-01 | Accept upload of customer contract documents (PDF, text, etc.) | Spec S10 Step 1 | MUST |
| CONTRACT-02 | Accept upload of SLA documents | Spec S10 Step 1 | MUST |
| CONTRACT-03 | Accept upload of privacy/compliance documents | Spec S10 Step 1 | MUST |
| CONTRACT-04 | Accept upload of product/use-case notes | Spec S10 Step 1 | SHOULD |
| CONTRACT-05 | Accept optional custom instructions as free text (e.g., "Customer data must stay in the EU", "Favor low latency over best reasoning") | Spec S10 Step 1, Transcript Part 4-5 | MUST |
| CONTRACT-06 | The extraction layer must infer: customer name, use case, likely end-user interactions, latency expectations, privacy/region restrictions, preferred providers, cost sensitivity, request complexity distribution, forbidden providers/regions | Spec S10 Step 2 | MUST |
| CONTRACT-07 | MVP extraction approach: prompt a frontier model with the full document set to produce structured output | Spec S10 Step 2 | MUST |
| CONTRACT-08 | Extraction output must be structured JSON/YAML containing all profile fields | Spec S10 Step 2-3 | MUST |
| CONTRACT-09 | Extraction should produce an estimated prompt mix (simple %, medium %, complex %) | Spec S10 Step 2 | SHOULD |
| CONTRACT-10 | The extraction agent should analyze documents and form a fully functional context of the customer profile | Transcript Part 4 | MUST |
| CONTRACT-11 | If the agent cannot extract certain fields from documents, the user can manually input them via custom instructions | Transcript Part 5 | MUST |
| CONTRACT-12 | For the demo, documents should be short enough to fit within a single context window (no vector search needed) | Transcript Part 6, Spec S6.7 | MUST |
| CONTRACT-13 | Stretch goal: chunk docs and summarize into structured fields | Spec S10 Step 2 | NICE |
| CONTRACT-14 | Stretch goal: vector search + tool-using agent over large document sets | Spec S10 Step 2, Transcript Part 6 | NICE |
| CONTRACT-15 | The agent could optionally perform deep research on the customer company (website, public info) to supplement contract data | Transcript Part 5 | NICE |
| CONTRACT-16 | Extraction should detect and flag missing or conflicting constraints | Spec S10 Step 4 | SHOULD |
| CONTRACT-17 | The extracted profile should include warnings and confidence gaps | Spec S15 View B | SHOULD |
| CONTRACT-18 | The extraction output should include what the ideal model for their use case would be | Transcript Part 5 | MUST |
| CONTRACT-19 | The extraction should determine what sort of users would interact with the customer's platform | Transcript Part 5 | SHOULD |
| CONTRACT-20 | The extraction should determine what complexity of user queries the customer will face | Transcript Part 4-5 | MUST |

---

## CUSTOMER -- Customer Management

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| CUSTOMER-01 | Dashboard has an "Add Customer" button/flow to create a new customer profile | Spec S10 Step 1 | MUST |
| CUSTOMER-02 | Each customer has a unique customer ID | Spec S20 | MUST |
| CUSTOMER-03 | Customer profile contains: customer metadata, hard constraints, soft preferences, recommended provider/model tier preferences, prompt complexity expectations, runtime routing policies | Spec S10 Step 3 | MUST |
| CUSTOMER-04 | Customer profile is the durable configuration object that powers all routing for that customer | Spec S10 Step 3 | MUST |
| CUSTOMER-05 | The operator can review the extracted profile on a dashboard page before approval | Spec S10 Step 4 | MUST |
| CUSTOMER-06 | The operator can approve, edit, or override specific fields of the extracted profile | Spec S10 Step 4 | MUST |
| CUSTOMER-07 | Customer profiles should be isolated from each other (customer-specific config isolation) | Spec S14 | SHOULD |
| CUSTOMER-08 | Each customer gets their own OpenAI-compatible API endpoint after profile approval | Spec S10 Step 5 | MUST |
| CUSTOMER-09 | Each customer gets monitoring visibility in the dashboard | Spec S10 Step 5 | MUST |
| CUSTOMER-10 | Customer hard constraints include: region restrictions, privacy tier, forbidden providers, allowed providers | Spec S20 | MUST |
| CUSTOMER-11 | Customer performance profile includes: latency target (ms), cost sensitivity level | Spec S20 | MUST |
| CUSTOMER-12 | Customer routing preferences map complexity tiers (simple, medium, complex) to ordered model lists | Spec S20 | MUST |
| CUSTOMER-13 | Customer profile includes the use case type (e.g., support_chatbot, claims_analysis) | Spec S20 | MUST |
| CUSTOMER-14 | Customer profile includes the optimization objective (e.g., low_latency, quality, cost) | Spec S20, Transcript Part 5 | MUST |
| CUSTOMER-15 | The system should support multiple customers simultaneously | Transcript Part 5, Spec S13 | MUST |
| CUSTOMER-16 | Customer profiles are reusable configurations | Spec S13 | MUST |
| CUSTOMER-17 | Contract change/update handling is explicitly out of scope for the demo | Transcript Part 5 | MUST |

---

## ROUTING -- Model Routing Logic

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| ROUTING-01 | Routing uses two kinds of information: (1) static customer-specific context and (2) dynamic per-request context | Spec S11 | MUST |
| ROUTING-02 | Static context includes: use case type, privacy requirements, region restrictions, model/provider allowlist, latency target, cost preference, expected complexity profile | Spec S11.1 | MUST |
| ROUTING-03 | Dynamic context includes: actual prompt complexity, actual task type | Spec S11.2 | MUST |
| ROUTING-04 | Optional dynamic context: provider health/latency, budget state, urgency | Spec S11.2 | NICE |
| ROUTING-05 | The recommended MVP routing approach is hybrid: deterministic policy filtering first, then classification among valid choices | Spec S12 Option C | MUST |
| ROUTING-06 | Policy filter eliminates providers/models that violate hard constraints (region, forbidden providers, etc.) before any classification | Spec S12 | MUST |
| ROUTING-07 | Classification step picks the best remaining route from valid choices | Spec S12 | MUST |
| ROUTING-08 | Simple support request + low latency target should route to cheap/fast model | Spec S11 example rules | MUST |
| ROUTING-09 | Complex reasoning request + premium SLA should route to stronger model | Spec S11 example rules | MUST |
| ROUTING-10 | Contract requires EU-only processing should route only to EU-approved providers/models | Spec S11 example rules | MUST |
| ROUTING-11 | Provider forbidden by policy must never be routed to | Spec S11 example rules | MUST |
| ROUTING-12 | Prompt too complex for cheap tier should escalate to stronger model | Spec S11 example rules | MUST |
| ROUTING-13 | The routing model receives: customer AI profile, user prompt, model/provider registry | Spec S10 Step 6 | MUST |
| ROUTING-14 | The routing model outputs: target model/provider, log entry explaining the choice, response returned through the endpoint | Spec S10 Step 6 | MUST |
| ROUTING-15 | Each routing decision must include a short explanation of why that route was chosen | Spec S12 Option A, S10 Step 6 | MUST |
| ROUTING-16 | The classification model is fed the customer-specific profile alongside each user query to make per-request decisions | Transcript Part 7 | MUST |
| ROUTING-17 | A single instance of the classification model can serve all customers (customer data passed per request) | Transcript Part 7 | SHOULD |
| ROUTING-18 | The classification model should determine if a query is simple, medium, or complex | Transcript Part 3, Part 7 | MUST |
| ROUTING-19 | Routing should include fallback model selections if the primary choice is unavailable | Spec S10 Step 3 example profile | SHOULD |
| ROUTING-20 | For customers with higher preference for expensive models, the routing should prioritize accordingly | Transcript Part 4 | SHOULD |
| ROUTING-21 | MVP classification can be prompt-based (frontier model receives profile + prompt + candidates, outputs best route) | Spec S12 Option A | MUST |
| ROUTING-22 | Stretch: small fine-tuned classifier for routing decisions | Spec S12 Option B, Transcript Part 3 | NICE |
| ROUTING-23 | The routing layer must respect region-specific restrictions -- if a model is not available in a required region, it must not be selected | Transcript Part 4 | MUST |

---

## MODEL -- Model Registry and Configuration

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| MODEL-01 | The system maintains a provider/model registry of available and allowed providers and models | Spec S9 Part 1 | MUST |
| MODEL-02 | Assurant configures allowed providers during initial deployment (OpenAI, Anthropic, Google Gemini, DeepSeek, etc.) | Spec S10 Step 0, Transcript Part 4 | MUST |
| MODEL-03 | Each provider has a list of available models | Spec S10 Step 0 | MUST |
| MODEL-04 | The registry must capture what each model is best suited for (use cases, capabilities) | Transcript Part 4 | MUST |
| MODEL-05 | The registry should include model cost information (per-token pricing or tier) | Spec S20, Transcript Part 3 | MUST |
| MODEL-06 | The registry should include model latency characteristics | Spec S20, Transcript Part 3 | MUST |
| MODEL-07 | The registry should include model capability tier (e.g., fast/cheap, medium, powerful/expensive) | Spec S10 Step 3 | MUST |
| MODEL-08 | Provider API keys are configured at the deployment/org level | Spec S10 Step 0 | MUST |
| MODEL-09 | Optional org-level defaults or restrictions on providers/models | Spec S10 Step 0 | SHOULD |
| MODEL-10 | The system should support providers: OpenAI, Anthropic, Google Gemini at minimum | Transcript Part 4, Spec S10 | MUST |
| MODEL-11 | The system should optionally support: DeepSeek, Qwen, Kimi, Minimax | Transcript Part 7 | NICE |
| MODEL-12 | Providers can be blocked at the org level (e.g., "no Chinese models") | Transcript Part 7 | SHOULD |
| MODEL-13 | The system must map each provider to concrete model names (e.g., claude-haiku, gpt-4o-mini, claude-sonnet, claude-opus) | Spec S10 Step 3, S20 | MUST |
| MODEL-14 | Model capabilities should be pre-researched and documented for routing decisions | Transcript Part 4 | MUST |

---

## PROXY -- OpenAI-Compatible Proxy Endpoint

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| PROXY-01 | The system exposes an OpenAI-compatible API endpoint (Completions API / Chat Completions API) | Spec S6.5, S10 Step 5 | MUST |
| PROXY-02 | Each customer gets a unique, customer-specific endpoint URL | Spec S10 Step 5, Transcript Part 5 | MUST |
| PROXY-03 | Example endpoint format: `https://gateway.example.com/v1/{customer-id}/chat/completions` | Spec S10 Step 5 | MUST |
| PROXY-04 | Downstream product teams can point their existing app to this endpoint instead of calling a provider directly -- just change the URL | Spec S6.5, Transcript Part 3 | MUST |
| PROXY-05 | The endpoint should accept standard OpenAI Chat Completions request format (messages array, etc.) | Spec S6.5, Transcript Part 3 | MUST |
| PROXY-06 | The endpoint should return standard OpenAI Chat Completions response format | Spec S6.5 | MUST |
| PROXY-07 | Behind the scenes, the proxy performs: (1) classify request, (2) route to selected model/provider, (3) return response | Spec S10 Step 6 | MUST |
| PROXY-08 | The proxy must log each request: customer ID, prompt, classification, selected provider/model, reason, latency, estimated cost | Spec S20 request log entry | MUST |
| PROXY-09 | The endpoint handles authentication/identification of which customer is making the request | Spec S10 Step 5 | MUST |
| PROXY-10 | The proxy should add minimal latency overhead (team estimated <100ms acceptable) | Transcript Part 3 | SHOULD |
| PROXY-11 | The proxy must forward the request to the correct provider API using configured API keys | Spec S10 Step 6 | MUST |
| PROXY-12 | The proxy should support streaming responses if time permits | Implied by OpenAI compat | NICE |

---

## UI-DASH -- Dashboard / Overview

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| UI-DASH-01 | A web dashboard is mandatory for the MVP | Spec S6.9, S18 | MUST |
| UI-DASH-02 | The dashboard makes extracted decisions legible -- the system is not a black box | Spec S10 Step 4 | MUST |
| UI-DASH-03 | The dashboard should show an overview of all customers and their AI infrastructure status | Transcript Part 5 | MUST |
| UI-DASH-04 | The dashboard should use customer cards as a visual element | Spec S15 | SHOULD |
| UI-DASH-05 | The dashboard should use model tier badges | Spec S15 | SHOULD |
| UI-DASH-06 | The dashboard should use route explanation labels | Spec S15 | SHOULD |
| UI-DASH-07 | The dashboard should include latency/cost charts | Spec S15 | SHOULD |
| UI-DASH-08 | The dashboard should be built with Next.js or React | Spec S19 | MUST |
| UI-DASH-09 | The dashboard needs to be visually polished and flashy for the judges | Transcript Part 1, Part 2 | MUST |

---

## UI-CUSTOMER -- Customer Pages

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| UI-CUSTOMER-01 | Customer intake page: upload documents flow | Spec S15 View A | MUST |
| UI-CUSTOMER-02 | Customer intake page: add custom instructions text field | Spec S15 View A | MUST |
| UI-CUSTOMER-03 | Customer intake page: configure allowed providers for this customer | Spec S15 View A | SHOULD |
| UI-CUSTOMER-04 | Customer intake page: create customer profile button/action | Spec S15 View A | MUST |
| UI-CUSTOMER-05 | Customer AI profile page: display extracted requirements | Spec S15 View B | MUST |
| UI-CUSTOMER-06 | Customer AI profile page: display objective (speed / cost / quality) | Spec S15 View B | MUST |
| UI-CUSTOMER-07 | Customer AI profile page: display region/privacy constraints | Spec S15 View B | MUST |
| UI-CUSTOMER-08 | Customer AI profile page: display recommended model plan (which models for which tiers) | Spec S15 View B | MUST |
| UI-CUSTOMER-09 | Customer AI profile page: display estimated request mix (% simple, medium, complex) | Spec S15 View B | SHOULD |
| UI-CUSTOMER-10 | Customer AI profile page: display warnings / confidence gaps from extraction | Spec S15 View B | SHOULD |
| UI-CUSTOMER-11 | Customer AI profile page: display the generated OpenAI-compatible endpoint URL prominently | Spec S10 Step 5, Transcript Part 5-6 | MUST |
| UI-CUSTOMER-12 | Customer AI profile page: approve / edit / override extracted fields | Spec S10 Step 4 | MUST |
| UI-CUSTOMER-13 | Customer AI profile page: display estimated cost/latency tradeoffs | Spec S10 Step 4 | SHOULD |
| UI-CUSTOMER-14 | Customer AI profile page: display what model the customer will use the most | Transcript Part 5 | SHOULD |
| UI-CUSTOMER-15 | Customer AI profile page: display estimated requests per second / traffic expectations | Transcript Part 5 | NICE |
| UI-CUSTOMER-16 | Customer list page: show all onboarded customers | Spec S15 | MUST |
| UI-CUSTOMER-17 | Customer AI profile page: display what sort of users interact with the customer's platform | Transcript Part 5 | NICE |

---

## UI-LOGS -- Request Logs and Analytics

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| UI-LOGS-01 | Runtime request log view showing requests over time | Spec S15 View C | MUST |
| UI-LOGS-02 | Each log entry shows: route chosen per request | Spec S15 View C | MUST |
| UI-LOGS-03 | Each log entry shows: model/provider used | Spec S15 View C | MUST |
| UI-LOGS-04 | Each log entry shows: latency | Spec S15 View C | MUST |
| UI-LOGS-05 | Each log entry shows: tokens used / cost estimate | Spec S15 View C | MUST |
| UI-LOGS-06 | Each log entry shows: "why this route" explanation | Spec S15 View C | MUST |
| UI-LOGS-07 | Each log entry shows: prompt classification (simple/medium/complex) | Spec S20 request log entry | MUST |
| UI-LOGS-08 | Each log entry shows: the customer ID it belongs to | Spec S20 request log entry | MUST |
| UI-LOGS-09 | Log view should be filterable by customer | Spec S15 View C | SHOULD |
| UI-LOGS-10 | Analytics should show cost savings vs always using the premium/most expensive model | Spec S21, Transcript Part 6 | MUST |
| UI-LOGS-11 | Analytics should show average latency by route/model | Spec S21 | SHOULD |
| UI-LOGS-12 | Analytics should show policy compliance rate | Spec S21 | SHOULD |
| UI-LOGS-13 | Metrics: "Customer onboarding config generated in <30 seconds" style headline stats | Spec S21 | SHOULD |
| UI-LOGS-14 | Metrics: "X% cost reduction vs always-premium baseline" | Spec S21 | MUST |
| UI-LOGS-15 | Metrics: show that simple requests were routed to cheaper tier automatically | Spec S21 | MUST |
| UI-LOGS-16 | Metrics: show that region constraints were respected 100% | Spec S21 | SHOULD |
| UI-LOGS-17 | Dashboard should track how many tokens have been used so far per customer | Transcript Part 5 | SHOULD |
| UI-LOGS-18 | Dashboard should show average latency per customer | Transcript Part 5 | SHOULD |

---

## UI-PLAYGROUND -- Playground / Testing Interface

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| UI-PLAYGROUND-01 | A way to send test prompts through the customer endpoint and see results | Spec S17 Step 5, Transcript Part 6 | MUST |
| UI-PLAYGROUND-02 | Show side-by-side: a simple prompt routed to cheap model vs complex prompt routed to expensive model | Spec S17 Step 5 | MUST |
| UI-PLAYGROUND-03 | Show the routing explanation for each test prompt | Spec S17 Step 5 | MUST |
| UI-PLAYGROUND-04 | Show token/cost/latency comparison between test prompts | Spec S17 Step 5 | MUST |
| UI-PLAYGROUND-05 | Option: deploy a ChatGPT-style app (like Open WebUI) pointed at the customer endpoint to simulate real usage | Spec S19, Transcript Part 6 | NICE |
| UI-PLAYGROUND-06 | Provide sample prompts (pre-built simple and complex prompts) for testing | Spec S18, Transcript Part 7 | MUST |
| UI-PLAYGROUND-07 | The playground should show which model was selected for each prompt and why | Transcript Part 6 | MUST |

---

## UI-MODELS -- Model Registry UI

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| UI-MODELS-01 | A page/section to configure available providers | Spec S10 Step 0, Transcript Part 4 | MUST |
| UI-MODELS-02 | A page/section to configure available models per provider | Spec S10 Step 0 | MUST |
| UI-MODELS-03 | Display model capabilities, cost tier, latency characteristics | Spec S15, MODEL-05/06/07 | SHOULD |
| UI-MODELS-04 | Ability to block/allow specific providers at the org level | Transcript Part 7 | SHOULD |
| UI-MODELS-05 | Configure provider API keys | Spec S10 Step 0 | MUST |

---

## FLOW -- End-to-End Workflow Steps

This section describes the exact step-by-step user journey, which is critical for both implementation and the demo.

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| FLOW-01 | Step 0: Assurant deploys the system (Docker image). They configure provider API keys, provider/model allowlist, optional global policy defaults. Output: working control plane ready to onboard customers. | Spec S10 Step 0 | MUST |
| FLOW-02 | Step 1: User clicks "Add Customer" in the dashboard. They upload contract docs, SLA docs, privacy/compliance docs, product notes, and optional custom instructions. | Spec S10 Step 1 | MUST |
| FLOW-03 | Step 2: The extraction layer processes the uploaded documents. It infers customer name, use case, end-user interactions, latency expectations, privacy/region restrictions, preferred providers, cost sensitivity, request complexity distribution, forbidden providers. Outputs structured JSON/YAML. | Spec S10 Step 2 | MUST |
| FLOW-04 | Step 3: The extracted structure becomes a Customer AI Profile -- the durable configuration powering routing. Contains metadata, hard constraints, soft preferences, model tier preferences, complexity expectations, routing policies. | Spec S10 Step 3 | MUST |
| FLOW-05 | Step 4: The operator reviews the profile on a dashboard page showing: extracted requirements, recommended model/provider mappings, estimated request mix, cost/latency tradeoffs, warnings. The operator can approve, edit, or override fields. | Spec S10 Step 4 | MUST |
| FLOW-06 | Step 5: Once approved, the system creates a customer-specific routing config and exposes an OpenAI-compatible endpoint URL (e.g., `https://gateway.example.com/v1/acme-support/chat/completions`). The downstream product team now uses this URL. | Spec S10 Step 5 | MUST |
| FLOW-07 | Step 6: At runtime, user prompts come in through the endpoint. The routing layer receives the customer AI profile + user prompt + model registry. It classifies prompt complexity, filters by policy, selects the best model, logs the decision with explanation, and returns the response. | Spec S10 Step 6 | MUST |
| FLOW-08 | The complete path is: customer contract -> customer AI profile -> customer-specific routing endpoint -> per-request intelligent routing | Spec S24, Transcript Part 4 | MUST |
| FLOW-09 | From the Assurant operator's perspective: deploy Docker image -> configure providers -> upload customer docs -> review profile -> get endpoint URL -> customer is live | Transcript Part 4-5 | MUST |
| FLOW-10 | From the product team's perspective: receive endpoint URL -> replace their existing OpenAI URL with it -> everything else stays the same | Spec S6.5, Transcript Part 3 | MUST |
| FLOW-11 | Customer onboarding should feel like: "Input everything you have from the customer contract. Boom, you have a customer-ready AI profile." | Transcript Part 6 | MUST |

---

## API -- Backend API Endpoints

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| API-01 | POST endpoint to create a new customer (upload documents + custom instructions) | Spec S10 Step 1 | MUST |
| API-02 | POST endpoint to trigger document extraction/analysis for a customer | Spec S10 Step 2 | MUST |
| API-03 | GET endpoint to retrieve a customer's extracted AI profile | Spec S10 Step 3-4 | MUST |
| API-04 | PUT/PATCH endpoint to update/override fields in a customer profile | Spec S10 Step 4 | MUST |
| API-05 | POST endpoint to approve/finalize a customer profile and generate the endpoint | Spec S10 Step 5 | MUST |
| API-06 | OpenAI-compatible Chat Completions endpoint: `POST /v1/{customer-id}/chat/completions` | Spec S10 Step 5-6 | MUST |
| API-07 | GET endpoint to list all customers | Spec S15 | MUST |
| API-08 | GET endpoint to retrieve request logs for a customer | Spec S15 View C | MUST |
| API-09 | GET endpoint to retrieve analytics/metrics for a customer | Spec S15 View C, S21 | SHOULD |
| API-10 | CRUD endpoints for the model/provider registry | Spec S10 Step 0 | MUST |
| API-11 | GET endpoint to retrieve the generated endpoint URL for a customer | Spec S10 Step 5 | MUST |
| API-12 | Backend should be Python FastAPI or Node/Express | Spec S19 | MUST |
| API-13 | Backend should include the customer profile extraction pipeline | Spec S19 | MUST |
| API-14 | Backend should include the routing layer | Spec S19 | MUST |
| API-15 | GET endpoint for aggregate dashboard metrics (cost savings, request counts, etc.) | Spec S21 | SHOULD |

---

## DATA -- Data Models and Storage

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| DATA-01 | Customer Profile schema: `customer_id`, `use_case`, `objective`, `constraints` (region, privacy_tier, forbidden_providers, allowed_providers), `performance` (latency_target_ms, cost_sensitivity), `routing_preferences` (simple/medium/complex model lists) | Spec S20 | MUST |
| DATA-02 | Request Log Entry schema: `customer_id`, `prompt` (or summary), `classification` (simple/medium/complex), `selected_provider`, `selected_model`, `reason` (explanation), `latency_ms`, `estimated_cost` | Spec S20 | MUST |
| DATA-03 | Model/Provider Registry schema: provider name, API key reference, list of models, model capabilities/strengths, cost per token (or tier), latency characteristics, supported regions | Spec S9 Part 1, MODEL-* | MUST |
| DATA-04 | Storage: SQLite or JSON files for customer profiles | Spec S19 | MUST |
| DATA-05 | Storage: local filesystem for uploaded contract documents | Spec S19 | MUST |
| DATA-06 | Storage: simple request logs (could be SQLite, JSON, or in-memory) | Spec S19 | MUST |
| DATA-07 | Customer profile should include the routing_policy mapping: for each complexity tier (simple, medium, complex), a preferred model and fallback model | Spec S10 Step 3 example | MUST |
| DATA-08 | Customer profile should include the constraints block: max_latency_ms, cost_preference | Spec S10 Step 3 example | MUST |
| DATA-09 | Request log should capture timestamp for each request | Spec S15 View C (requests over time) | MUST |
| DATA-10 | Request log should capture token counts (input/output) for cost estimation | Spec S20, UI-LOGS-05 | SHOULD |

---

## DEMO -- Demo-Specific Requirements

| ID | Requirement | Source | Priority |
|----|------------|--------|----------|
| DEMO-01 | Demo must fit within 3-5 minutes | Transcript Part 6, Organizer presentation | MUST |
| DEMO-02 | Demo story structure: (1) show the pain, (2) show intake, (3) show extracted profile, (4) show generated endpoint, (5) show runtime routing with simple + complex prompts, (6) close with value | Spec S17, S27 | MUST |
| DEMO-03 | Opening pitch: "Assurant asked for something scalable, reliable, secure, and operationally efficient. We focused on one painful real problem: onboarding customer-specific AI services." | Spec S27 | MUST |
| DEMO-04 | Create a fake/sample contract mimicking one Assurant might have with a customer | Transcript Part 5-6 | MUST |
| DEMO-05 | Research Assurant's pre-existing customers and AI products for realistic demo data | Transcript Part 5 | SHOULD |
| DEMO-06 | Prepare a short (2-page) sample contract document for the demo to keep extraction fast | Transcript Part 6 | MUST |
| DEMO-07 | Prepare a set of simple test prompts and a set of complex test prompts | Transcript Part 7 | MUST |
| DEMO-08 | During demo, show different routes selected for simple vs complex prompts | Spec S17 Step 5, S27 | MUST |
| DEMO-09 | During demo, show explanation for each routing decision | Spec S17 Step 5, S27 | MUST |
| DEMO-10 | During demo, show token/cost/latency comparison between routes | Spec S17 Step 5, S27 | MUST |
| DEMO-11 | Have a fallback: pre-processed static contract/profile in case live extraction fails | Spec S25 Day 2 Final | MUST |
| DEMO-12 | Deploy the app and give judges access to try it themselves | Transcript Part 6 | SHOULD |
| DEMO-13 | Provide a sample document for judges to test with | Transcript Part 6 | SHOULD |
| DEMO-14 | Closing value statement: "We reduced manual onboarding work, embedded contract constraints into routing, and created a cleaner, cheaper, safer AI deployment surface." | Spec S27 | MUST |
| DEMO-15 | The 30-second pitch: "We built a contract-aware AI control plane for enterprise AI deployment. Instead of manually reading contracts, choosing models, and wiring up customer-specific AI behavior by hand, our system ingests customer documents, extracts SLA, privacy, and routing constraints, builds a customer AI profile, and generates an OpenAI-compatible endpoint for that customer." | Spec S26 | MUST |
| DEMO-16 | Show headline metrics: "Customer onboarding config generated in <30 seconds", "Simple requests routed to cheaper tier automatically", "EU-only constraints respected 100%", "X% cost reduction vs always-premium baseline" | Spec S21 | MUST |
| DEMO-17 | Rehearse the 5-minute demo before presenting | Spec S25 Day 2 Final | MUST |
| DEMO-18 | Use at least two example use cases during demo (e.g., customer support chatbot + claims analysis) to show different routing behaviors | Spec S16 | SHOULD |
| DEMO-19 | The system should be actually deployed and functional, not just mockups | Transcript Part 6 | MUST |
| DEMO-20 | Presentation slots are Saturday 1pm-4pm; build must be complete by then | Transcript Part 6, Organizer presentation | MUST |
| DEMO-21 | Team registration must be done by Friday noon | Organizer presentation | MUST |
| DEMO-22 | Frame the pitch as a policy-aware routing assistant/control plane, NOT a full compliance suite | Spec S23 Risk 5 | MUST |
| DEMO-23 | Do NOT frame as: a carbon router, a generic prompt router, a giant platform | Spec S28 | MUST |
| DEMO-24 | Frame as: "a contract-aware onboarding and inference control plane for enterprise AI services" | Spec S28 | MUST |

---

## Summary Statistics

| Category | Count | MUST | SHOULD | NICE |
|----------|-------|------|--------|------|
| CORE | 15 | 13 | 1 | 1 |
| CONTRACT | 20 | 12 | 4 | 4 |
| CUSTOMER | 17 | 13 | 3 | 1 |
| ROUTING | 23 | 17 | 5 | 1 |
| MODEL | 14 | 9 | 3 | 2 |
| PROXY | 12 | 10 | 1 | 1 |
| UI-DASH | 9 | 4 | 4 | 1 |
| UI-CUSTOMER | 17 | 10 | 5 | 2 |
| UI-LOGS | 18 | 8 | 8 | 2 |
| UI-PLAYGROUND | 7 | 5 | 0 | 2 |
| UI-MODELS | 5 | 3 | 2 | 0 |
| FLOW | 11 | 11 | 0 | 0 |
| API | 15 | 12 | 2 | 1 |
| DATA | 10 | 8 | 2 | 0 |
| DEMO | 24 | 17 | 5 | 2 |
| **TOTAL** | **217** | **152** | **45** | **20** |

---

## Key Architectural Decisions (from transcript and spec)

1. **Docker-deployable**: The product ships as a Docker image that Assurant deploys in their own environment.
2. **OpenAI-compatible endpoint is THE product**: Customers just swap their OpenAI URL. Everything else stays the same.
3. **Hybrid routing**: Deterministic policy filter first, then AI classification among remaining valid options.
4. **No carbon routing for Assurant**: Carbon is dropped as primary context. Sustainability story = operational efficiency, cost savings, not overprovisioning.
5. **Short contracts for demo**: No vector search needed. Full document fits in context window.
6. **No RL, no autoscaling, no GPU management**: Keep it narrow and practical.
7. **Dashboard is mandatory**: Judges need to see what was extracted, what was configured, and why routes were chosen.
8. **Per-request routing**: Routing happens on every API call, not just once at setup.
9. **Single classification model serves all customers**: Customer profile is passed per-request, so one model instance handles everything.
10. **Agents for extraction**: AI agents analyze contract documents and produce structured customer profiles automatically.
