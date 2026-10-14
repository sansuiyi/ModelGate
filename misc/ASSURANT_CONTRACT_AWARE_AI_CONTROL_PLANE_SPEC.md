# ASSURANT_CONTRACT_AWARE_AI_CONTROL_PLANE_SPEC.md

## Working Title
**Contract-Aware AI Control Plane**

Alternate names:
- **SLAware AI Gateway**
- **ContractRouter**
- **ModelOps Onboarding Layer**
- **Customer-Aware AI Gateway**
- **Inference Policy Engine**

---

## 1. Executive Summary

This project is an **Assurant-track AI infrastructure product** focused on one painful enterprise problem:

> When a new customer needs an AI-powered experience, someone has to figure out what models to use, what constraints apply, what regions are allowed, what latency/cost/privacy requirements matter, and how to expose that setup cleanly to the product team.

Today, that process is manual, slow, error-prone, and expensive.

This project automates that workflow.

The system accepts:
- customer contract documents
- policy documents
- optional custom instructions / hard constraints
- provider availability and model catalog

It then produces:
- a structured **customer AI profile**
- recommended routing and policy configuration
- an **OpenAI-compatible API endpoint** for that customer
- a dashboard showing what was inferred, what was configured, and how requests are being routed

At runtime, the system does **per-request routing** based on:
- the customer’s extracted SLA / policy / privacy requirements
- the user’s actual prompt complexity
- model/provider capabilities
- optional runtime signals like latency/cost/provider health

This is **not** just “a model router.”
It is a **contract-aware onboarding and inference control plane** for AI applications.

That makes it a much better Assurant fit than a raw prompt router or carbon-aware LLM router.

---

## 2. Why This Fits Assurant

From the Assurant challenge clarification, the track wants something that improves:
- **scalability**
- **reliability**
- **security**
- **operational efficiency / reduced waste**

They also explicitly mentioned examples like:
- Datadog-style observability
- Azure / AWS / GCP scaling
- security testing
- performance testing
- performance optimization
- right-sizing instead of overprovisioning

This project matches that well because it improves AI systems by:
- reducing manual configuration and onboarding work
- routing to the right model instead of blindly using the most expensive one
- respecting privacy / region constraints automatically
- improving operational efficiency by matching model choice to use case
- giving teams a clean, controlled, OpenAI-compatible deployment surface

### Assurant framing
This should be pitched as:
> an AI onboarding and reliability layer that helps organizations deploy customer-specific AI services faster, safer, and more efficiently.

Not as:
- an academic routing paper
- a carbon optimizer
- a generic “AI platform”
- a dashboard for everything

---

## 3. Core Insight

The most valuable part of enterprise AI deployment is often **not inference itself**.
It is the messy layer before inference:
- what does this customer actually need?
- what constraints are hidden in their contracts?
- what model providers are even allowed?
- what region restrictions apply?
- what performance expectations exist?
- what counts as success for this customer?

The insight is:
> **AI model selection should be driven by customer contracts and operational constraints, not just prompt complexity.**

And once that customer profile exists, runtime routing can become much smarter and more reliable.

---

## 4. Product Definition

This project is a **customer-onboarding + request-routing control plane** for AI-powered services.

It has two major phases:

### Phase A — Customer onboarding / policy extraction
Input:
- contract documents
- SLA documents
- privacy / region requirements
- optional custom instructions

Output:
- structured customer AI profile
- recommended routing/policy config
- customer-specific deployment config

### Phase B — Runtime routing
Input:
- user prompt
- customer AI profile
- available models/providers
- optional runtime metrics

Output:
- selected provider/model/route
- optional explanation/log
- response returned through an OpenAI-compatible endpoint

---

## 5. The Real Differentiation

This project must **not** be framed as “another Arch-Router clone.”

### Arch-Router style routing asks:
> Which model should answer this query?

### This system asks:
> Given this customer’s contract, SLA, privacy constraints, allowed regions, expected users, and this specific user request — what is the best safe, compliant, cost-effective model path to use right now?

That is a much more enterprise-native and Assurant-native story.

### Key differentiation points
1. **Contract-aware**
   - customer-specific constraints are first-class
2. **Policy-aware**
   - SLA / region / latency / privacy / provider rules matter
3. **Onboarding-aware**
   - helps configure AI services faster from real docs
4. **Runtime-aware**
   - routes each prompt dynamically, not just once at setup
5. **Operationally efficient**
   - avoids blindly using the largest model for every request

---

## 6. Key Decisions We Reached

This section captures the important decisions from the team discussion.

### 6.1 We are dropping carbon as the primary routing context for Assurant
Carbon-aware routing was interesting, but it does **not** fit Assurant as cleanly as operational context.

For the Assurant version, the main context is:
- SLA requirements
- privacy / region restrictions
- latency expectations
- customer use case
- likely prompt complexity
- allowed providers/models
- runtime performance/cost considerations

Carbon can remain an optional secondary metric, but it should **not** be the core pitch.

### 6.2 The product is a framework/control plane, not just a model
The final direction is not “fine-tune a new model and that is the product.”

The product is:
- a Docker-deployable system
- that uses agents/extractors + routing logic
- and exposes an OpenAI-compatible endpoint

### 6.3 Onboarding is part of the value
The team repeatedly converged on the idea that a big part of the pain is:
- reading contracts
- figuring out model/provider constraints
- mapping customer needs to AI configuration

So onboarding is not just a pre-processing detail — it is part of the product value.

### 6.4 Runtime routing still matters
The routing does **not** happen only once during onboarding.

The final understanding was:
- customer contract + docs produce a **customer profile**
- at runtime, each user prompt is classified against that customer profile
- routing decisions happen **per request**

### 6.5 The system should expose an OpenAI-compatible API
This was a key simplification.

Instead of forcing a product team to rewrite their app, they should be able to:
- replace their existing OpenAI URL / model layer
- point to the new control plane endpoint
- keep their application flow mostly intact

### 6.6 The MVP should avoid trying to solve real autoscaling infrastructure
The team identified this as too risky.

We should **not** try to build:
- real multi-cloud infra orchestration
- actual GPU autoscaling
- real Datadog replacement
- real production-grade failover across data centers

Instead, focus on:
- contract-aware config extraction
- customer profile generation
- per-request routing
- dashboard + explanation + metrics

### 6.7 Vector search is optional, not mandatory for the live demo
The team discussed vectorizing long contracts.
That is useful for the real product.

But for the hackathon MVP:
- if demo contracts are short enough, we can keep it simpler
- if needed, vector search can be used for larger doc sets
- the live demo should prioritize speed and reliability

### 6.8 Reinforcement learning is out of scope
RL was mentioned and immediately recognized as too much for the timeline.

For the MVP, stick to one of:
- rules + heuristics
- prompt-based extraction/classification
- small fine-tuned classifier if time permits

### 6.9 The dashboard is mandatory
The team correctly identified that the judges need to **see**:
- what was extracted
- what configuration was produced
- why a route was chosen
- what cost/latency differences exist

Without a dashboard, the system will be harder to trust and demo.

---

## 7. User Personas

Even though this is a B2B-ish system, we still need persona clarity for the pitch.

### Persona 1 — AI Solutions Engineer at Assurant
**Goal:** onboard a new customer AI use case quickly and safely.

**Pain points:**
- too many contract details to manually interpret
- unclear provider/model choice
- risk of violating customer constraints
- time wasted setting up each customer

**Value:**
- faster onboarding
- safer policy setup
- less manual reading/config work

### Persona 2 — Enterprise Customer / Product Team
**Goal:** launch an AI-powered experience without worrying about model/provider complexity.

**Pain points:**
- no internal LLM infra expertise
- unclear which model to use
- fear of privacy/compliance mistakes
- performance/cost uncertainty

**Value:**
- customer-specific endpoint ready faster
- better model fit for use case
- lower cost and clearer constraints

### Persona 3 — Operations / Platform Team
**Goal:** maintain visibility and control across deployed customer AI services.

**Pain points:**
- fragmented model usage
- poor observability
- expensive default routing
- hard to compare customer configs

**Value:**
- standardized deployment surface
- dashboard visibility
- policy-aware routing
- less waste

---

## 8. Problem Statement

When organizations deploy AI features for different customers, the path from signed contract to deployed service is messy.

Teams must manually decide:
- which models to use
- which providers are allowed
- which regions can process data
- what latency and cost profile to optimize for
- how to route simple vs complex requests
- how to expose the final endpoint cleanly to product teams

This leads to several problems:
- slow onboarding
- inconsistent architecture decisions
- avoidable privacy/compliance risk
- overuse of expensive models
- operational waste
- poor visibility into why a setup was chosen

The project solves this by creating a control plane that translates customer documents into deployable AI configuration.

---

## 9. Solution Overview

The system consists of five major parts:

1. **Provider/Model Registry**
   - what providers/models are available and allowed
2. **Customer Ingestion Layer**
   - upload contracts/docs/custom instructions
3. **Customer Profile Extractor**
   - agent/extractor creates structured requirements
4. **Runtime Routing Layer**
   - routes each user request based on profile + prompt
5. **Dashboard + Endpoint Layer**
   - shows what happened and exposes customer-specific API access

---

## 10. End-to-End Workflow

## Step 0 — Assurant deploys the framework
Assurant (or the hypothetical enterprise user) deploys the system via:
- Docker image / compose stack
- local or cloud environment

At this stage they configure:
- allowed providers (OpenAI, Anthropic, Gemini, etc.)
- available models per provider
- optional org-level defaults or restrictions

### Inputs at this stage
- provider API keys
- provider/model allowlist
- optional global policy defaults

### Output
- working control plane ready to onboard customers

---

## Step 1 — Create a new customer profile
A user in the dashboard clicks:
- **Add Customer**

They upload:
- customer contract docs
- SLA docs
- privacy/compliance docs
- product/use-case notes
- optional custom instructions

### Example custom instructions
- “Customer data must stay in the EU.”
- “Favor low latency over best reasoning.”
- “Only use non-Chinese providers.”
- “This use case is customer support, not deep research.”

---

## Step 2 — Document analysis / extraction
The extraction layer processes the uploaded material.

Its job is to infer:
- customer name / use case
- likely end-user interactions
- latency expectations
- privacy / region restrictions
- preferred providers if implied
- cost sensitivity
- request complexity distribution
- any forbidden providers or deployment regions

### Implementation notes
MVP options:
1. **Simplest:** prompt a frontier model with the full document set
2. **Better:** chunk docs and summarize into structured fields
3. **Stretch:** vector search + tool-using agent over large doc set

### Structured output example
```json
{
  "customer_name": "Acme Support",
  "use_case": "customer support assistant",
  "preferred_objective": "low_latency",
  "data_region": "EU-only",
  "privacy_tier": "high",
  "allowed_providers": ["anthropic", "openai"],
  "forbidden_providers": ["deepseek"],
  "estimated_prompt_mix": {
    "simple": 0.65,
    "medium": 0.30,
    "complex": 0.05
  },
  "latency_target_ms": 1000,
  "cost_sensitivity": "high"
}
```

---

## Step 3 — Customer AI profile generation
The extracted structure becomes a **Customer AI Profile**.

This is the durable configuration object that powers routing.

### What it contains
- customer metadata
- hard constraints
- soft preferences
- recommended provider/model tier preferences
- prompt complexity expectations
- runtime routing policies

### Example profile
```yaml
customer: Acme Support
objective: low_latency_support
region: eu-only
privacy: high
allowed_providers:
  - anthropic
  - openai
forbidden_providers:
  - deepseek
routing_policy:
  simple:
    preferred: claude-haiku
    fallback: gpt-4o-mini
  medium:
    preferred: claude-sonnet
    fallback: gpt-4o-mini
  complex:
    preferred: claude-opus
    fallback: claude-sonnet
constraints:
  max_latency_ms: 1000
  cost_preference: minimize_when_possible
```

---

## Step 4 — Dashboard review / approval
The operator sees a dashboard page showing:
- extracted requirements
- recommended model/provider mappings
- estimated request mix
- estimated cost/latency tradeoffs
- warnings about missing/conflicting constraints

This is the point where the human can:
- approve
- edit
- override specific fields

### Important principle
The system is not a black box that silently deploys everything.
The dashboard should make the extracted decisions legible.

---

## Step 5 — Customer endpoint creation
Once approved, the system creates a customer-specific routing config and exposes:
- an OpenAI-compatible endpoint
- customer-specific auth/config
- monitoring visibility in the dashboard

### Example output
```text
https://gateway.example.com/v1/acme-support/chat/completions
```

The downstream product team can now point their app to that endpoint instead of directly calling one provider.

---

## Step 6 — Runtime request routing
At runtime, a user prompt comes in.

The routing layer receives:
- customer AI profile
- user prompt
- model/provider registry
- optional live runtime metrics

It decides:
- which provider/model to use
- whether a fallback is needed
- which route best satisfies policy + prompt complexity

### Runtime routing inputs
- prompt complexity
- customer objective (speed vs intelligence vs cost)
- allowed regions/providers
- latency target
- optional live provider health
- optional cost budget / org preference

### Runtime routing outputs
- target model/provider
- log entry explaining choice
- final response returned to app

---

## 11. Routing Logic

The runtime classifier should route based on two kinds of information:

### 11.1 Static / customer-specific context
- use case type
- privacy requirements
- region restrictions
- model/provider allowlist
- latency target
- cost preference
- expected complexity profile

### 11.2 Dynamic / per-request context
- actual prompt complexity
- actual task type
- optional provider health/latency
- optional budget state
- optional urgency

### Example decision rules
- Simple support request + low latency target → cheap/fast model
- Complex reasoning request + high-value customer + premium SLA → stronger model
- Contract requires EU-only processing → only EU-approved route candidates
- Provider forbidden by policy → never route there
- Prompt likely too complex for cheap tier → escalate to stronger model

---

## 12. What the “Router” Actually Is

The team discussed a classification model a lot. For the MVP, this should stay pragmatic.

### MVP implementation options
#### Option A — Prompt-based classifier (fastest)
A frontier model receives:
- customer profile
- user prompt
- candidate models

It outputs:
- best route
- short explanation

#### Option B — Small custom classifier (stronger hackathon story)
A small local model or fine-tuned classifier predicts:
- route tier
- recommended provider/model

Based on:
- prompt complexity
- customer profile features

#### Option C — Hybrid (recommended)
- use deterministic policy filtering first
- use a classifier only among valid choices

### Recommended MVP path
**Hybrid**:
1. policy filter eliminates invalid providers/models
2. small classification step picks best remaining route

This is easier to explain and safer to demo.

---

## 13. Why This Is Scalable

The team explicitly worried about scalability. The scoped answer is:

### What is scalable in the MVP
- customer profiles are reusable configs
- runtime routing can be a single lightweight service
- endpoint shape is standardized
- provider choices are abstracted behind one API layer

### What we are not claiming
We are **not** claiming:
- full multi-cloud autoscaling solved
- data center placement solved
- perfect token prediction / KV-cache prediction solved
- global infra orchestration solved

The scalability story is:
> the control plane standardizes onboarding and model selection across many customers, reducing manual overhead and making AI deployment more repeatable.

---

## 14. Security and Privacy Story

This is important for Assurant.

### Security/privacy features in scope
- region restrictions as first-class constraints
- provider allowlists/forbidden lists
- hard policy boundaries around customer data
- customer-specific profile and config isolation

### Example privacy controls
- “EU-only processing”
- “do not use provider X”
- “do not send to external reasoning provider”
- “support only low-retention providers”

### Out of scope for MVP
- real DLP
- legal compliance verification
- automatic contract redlining
- production-grade secrets management platform

But the architecture should clearly suggest where those would slot in.

---

## 15. Dashboard Requirements

The dashboard should have three major views.

## View A — Customer Intake
- upload documents
- add custom instructions
- configure allowed providers
- create customer profile

## View B — Customer AI Profile
- extracted requirements
- objective (speed / cost / quality)
- region/privacy constraints
- recommended model plan
- estimated request mix
- warnings / confidence gaps

## View C — Runtime Metrics / Request Log
- requests over time
- route chosen per request
- model/provider used
- latency
- tokens/cost estimate
- maybe “why this route” explanation

### Nice visual elements
- customer cards
- model tier badges
- route explanation labels
- latency/cost charts

---

## 16. Example Use Cases

### Use Case 1 — Customer Support Assistant
**Customer need:**
A support chatbot serving many users with mostly simple requests.

**Constraints:**
- low latency matters most
- moderate privacy needs
- cost-sensitive

**Expected routing behavior:**
- most prompts go to cheap/fast model
- rare escalations go to stronger model

**Value:**
- avoids wasting premium model calls on trivial support traffic

---

### Use Case 2 — Internal Claims Analysis Assistant
**Customer need:**
An internal assistant helping workers analyze more complex claim summaries.

**Constraints:**
- higher reasoning quality required
- privacy requirements stricter
- latency less important than correctness

**Expected routing behavior:**
- medium and complex prompts go to stronger model
- simple prompts still use cheaper tier when possible

**Value:**
- balances quality and cost without violating data handling rules

---

### Use Case 3 — Region-Locked Enterprise Customer
**Customer need:**
An AI assistant for a customer whose data cannot leave a region.

**Constraints:**
- strict region-only processing
- specific providers disallowed
- contractual penalties if violated

**Expected routing behavior:**
- routing only considers region-valid providers/models
- stronger model chosen only when still compliant

**Value:**
- compliance and privacy become embedded in routing, not left to human memory

---

### Use Case 4 — Premium SLA Customer
**Customer need:**
A customer contract says high-priority requests must stay within a specific latency SLO.

**Constraints:**
- speed matters most
- premium path allowed
- customer willing to pay more

**Expected routing behavior:**
- priority requests route to faster/premium models
- less urgent requests can still route down-tier

**Value:**
- system maps contractual SLO into real model behavior

---

## 17. Demo Plan

The team spent a lot of time worrying about demo complexity. The MVP demo should stay disciplined.

## Demo story
### Step 1 — Show the pain
“Today, onboarding a new AI customer means someone manually reads contracts, figures out restrictions, chooses providers, chooses models, and wires everything up by hand.”

### Step 2 — Show intake
Upload a sample contract + optional custom constraints.

### Step 3 — Show extracted profile
Display:
- use case
- region restrictions
- latency target
- allowed providers
- recommended model plan

### Step 4 — Show generated endpoint
Display the customer-specific OpenAI-style endpoint.

### Step 5 — Show runtime routing
Send:
- one simple prompt
- one complex prompt

Then show:
- different routes selected
- explanation for each
- token/cost/latency comparison

### Step 6 — Close with the value
“We reduced manual onboarding work, embedded contract constraints into routing, and created a cleaner, cheaper, safer AI deployment surface.”

---

## 18. What the MVP Should Actually Build

## Must-have
- web dashboard
- document upload/intake page
- customer profile extraction
- customer profile review page
- customer-specific OpenAI-compatible endpoint
- runtime route selection for simple vs complex prompts
- runtime request log

## Nice-to-have
- vector search over larger customer docs
- provider health input
- advanced policy overrides
- rich cost estimates
- side-by-side route comparison

## Avoid for hackathon
- real multi-cloud scaling
- real GPU management
- real autoscaling infra
- real contract-change diffing
- RL training
- production-grade auth/tenanting

---

## 19. Suggested Technical Architecture

## Frontend
- Next.js or React dashboard
- upload flow
- customer profile screens
- metrics/logging screens

## Backend
- Python FastAPI or Node/Express
- customer profile extraction pipeline
- routing layer
- OpenAI-compatible proxy endpoint

## Storage
- sqlite or JSON for customer profiles
- local files for uploaded contracts
- simple request logs

## Extraction layer
- LLM call / agent for document interpretation
- optional vector search for long docs

## Routing layer
- policy filter + classifier
- model/provider registry
- request logging

## Optional demo app
- Open WebUI or a very simple chat UI pointing at the endpoint

---

## 20. Proposed Data Structures

## Customer profile
```json
{
  "customer_id": "acme-support",
  "use_case": "support_chatbot",
  "objective": "low_latency",
  "constraints": {
    "region": "EU-only",
    "privacy_tier": "high",
    "forbidden_providers": ["deepseek"],
    "allowed_providers": ["anthropic", "openai"]
  },
  "performance": {
    "latency_target_ms": 1000,
    "cost_sensitivity": "high"
  },
  "routing_preferences": {
    "simple": ["claude-haiku", "gpt-4o-mini"],
    "medium": ["claude-sonnet", "gpt-4o-mini"],
    "complex": ["claude-opus", "claude-sonnet"]
  }
}
```

## Request log entry
```json
{
  "customer_id": "acme-support",
  "prompt": "Summarize this customer complaint",
  "classification": "medium",
  "selected_provider": "anthropic",
  "selected_model": "claude-sonnet",
  "reason": "medium complexity; fits latency target; provider allowed",
  "latency_ms": 720,
  "estimated_cost": 0.0032
}
```

---

## 21. Evaluation Metrics

This project needs proof.

### Core demo metrics
- customer setup time
- route correctness on sample prompts
- estimated cost difference vs always using premium model
- average latency by route
- policy compliance rate

### Strong headline metrics
- “Customer onboarding config generated in <30 seconds”
- “Simple requests routed to cheaper tier automatically”
- “EU-only constraints respected 100% in demo”
- “X% cost reduction vs always-premium baseline”

---

## 22. Comparison to Existing Systems

### What already exists
Yes, pieces of this already exist:
- model routers
- provider gateways
- policy engines
- contract readers
- vector search

### Why this still matters
The novelty is in the combination:
- **customer contract ingestion**
- **AI profile generation**
- **OpenAI-compatible deployment surface**
- **runtime per-request routing using customer-specific constraints**

This is not a generic load balancer.
It is a **contract-aware AI onboarding and routing workflow**.

---

## 23. Risks

### Risk 1 — Feels too close to “yet another model router”
**Mitigation:** emphasize contract-aware onboarding + policy-aware deployment, not just query complexity routing.

### Risk 2 — Too much implementation surface
**Mitigation:** keep the MVP narrow. One extraction flow, one routing flow, one dashboard, one endpoint.

### Risk 3 — Document processing becomes slow in demo
**Mitigation:** use a shorter mock contract for the live demo. Preprocess if needed. Keep vector search optional.

### Risk 4 — Hard to show value without an app layer
**Mitigation:** add a minimal chat UI or Open WebUI pointed at the generated endpoint.

### Risk 5 — Overclaiming compliance/security
**Mitigation:** frame this as a policy-aware routing assistant/control plane, not a full compliance suite.

---

## 24. Scope Cuts We Explicitly Accept

To keep this hackathon-realistic, we are explicitly **not** building:
- real autoscaling engine
- real data center optimization engine
- exact token/KV cache predictor
- full contract lifecycle manager
- perfect provider benchmarking system
- full enterprise tenant management
- real SLA enforcement infrastructure with penalties

We are building the smartest narrow slice:
> from customer contract to customer-specific AI profile to customer-specific routing endpoint.

---

## 25. MVP Build Plan

## Day 1 / Phase 1
- define provider/model registry
- build upload form
- define customer profile schema
- build extraction flow
- generate customer profile output

## Day 1 / Phase 2
- build dashboard profile view
- build simple routing logic
- build OpenAI-compatible endpoint wrapper

## Day 2 / Phase 3
- add runtime log view
- add sample prompts
- integrate simple demo chat UI
- polish metrics and explanation text

## Day 2 / Final
- rehearse 5-minute demo
- create fallback static contract/profile if extraction fails live
- tighten visuals and story

---

## 26. 30-Second Pitch

> We built a contract-aware AI control plane for enterprise AI deployment. Instead of manually reading contracts, choosing models, and wiring up customer-specific AI behavior by hand, our system ingests customer documents, extracts SLA, privacy, and routing constraints, builds a customer AI profile, and generates an OpenAI-compatible endpoint for that customer. At runtime, it routes each request using both the customer’s requirements and the prompt’s complexity — so AI services are faster to onboard, more compliant, and more operationally efficient.

---

## 27. Demo Script

### Opening
“Assurant asked for something scalable, reliable, secure, and operationally efficient. We focused on one painful real problem: onboarding customer-specific AI services.”

### Problem
“Today, someone has to manually read contracts, infer restrictions, choose the right providers and models, and wire everything together.”

### Solution
“We automate that path from customer documents to deployable AI endpoint.”

### Show intake
Upload contract docs and optional custom instructions.

### Show extracted profile
Display:
- region restrictions
- latency target
- allowed providers
- cost preference
- recommended route plan

### Show endpoint
Display generated OpenAI-compatible endpoint.

### Show runtime behavior
Send one simple prompt and one complex prompt.
Show:
- different routes
- explanation
- estimated latency/cost differences

### Close
“This reduces onboarding effort, improves consistency, and prevents wasteful/default premium model usage.”

---

## 28. Final Recommendation

This is the best Assurant-shaped version of the team’s routing idea **if we keep it narrow and practical**.

The winning framing is:
- not a carbon router
- not a generic prompt router
- not a giant platform

It is:
> **a contract-aware onboarding and inference control plane for enterprise AI services**

That preserves the strongest ideas from the discussion:
- customer docs in
- policy extraction
- customer AI profile
- provider/model selection
- per-request routing
- OpenAI-compatible endpoint
- dashboard visibility

while avoiding the rabbit holes that would kill the demo.

---

## 29. Source Notes

This spec incorporates:
- the Assurant challenge framing from the event presentation
- the transcript discussion recorded on **Mar 19 at 6:30 PM**
- earlier ideation and narrowing decisions made during hackathon planning

Key preserved team decisions:
- drop carbon as the primary Assurant context
- make onboarding and policy extraction part of the product
- expose an OpenAI-compatible endpoint
- support per-request routing at runtime
- use a dashboard to make the system legible
- keep the MVP narrow enough to survive a 5-minute demo
