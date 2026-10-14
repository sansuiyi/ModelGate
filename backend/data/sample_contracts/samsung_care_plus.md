# Samsung Electronics America — Care+ Warranty Intelligence Platform Agreement
## Contract ID: SEA-2026-3301
## Effective Date: March 1, 2026

## PARTIES
This agreement is entered between Assurant, Inc. (acting through its subsidiary
Technology Insurance Company, Inc.) ("Provider") and Samsung Electronics America,
Inc. ("Customer") for the deployment of AI-powered warranty intelligence and claims
support services under the Samsung Care+ device protection program.

## SECTION 1 — SERVICE DESCRIPTION
Provider shall deploy an AI-powered Warranty Intelligence Platform ("Platform") for
Samsung Electronics America's Samsung Care+ device protection program. The Platform
shall support the following functions:

### 1.1 Tier 1 — End-User Self-Service Assistant
    An AI-powered chatbot serving Samsung Care+ subscribers directly, handling:
    - Claim eligibility screening and deductible lookup
    - Guided device damage triage (physical damage, liquid damage, screen failure)
    - Galaxy AI feature malfunction classification and escalation routing
    - Repair vs. replace recommendation for enrolled devices
    - Appointment scheduling for Samsung-authorized repair centers

### 1.2 Tier 2 — Internal Agent Assist
    An AI-powered assistant for Samsung Care+ claims agents and technicians, handling:
    - AI-generated claim history summaries across multi-device enrollments
    - Device service record synthesis spanning up to 40 pages of documentation
    - Coverage and policy clarification for complex bundled plans
    - Escalation drafting for disputed claims

### 1.3 Galaxy AI Feature Support Routing
    A specialized classification layer that identifies when a customer query concerns
    Samsung Galaxy AI features (including but not limited to: Circle to Search,
    Live Translate, Call Summary, Now Brief, Generative Edit, Sketch to Image,
    Transcript Assist, Chat Assist, Interpreter Mode, and AI-powered camera features).
    Queries in this category shall be routed with elevated model capability
    requirements per Section 4.4.

## SECTION 2 — DATA HANDLING AND PRIVACY
2.1 All data processed under this agreement is classified as containing PII
    (device owner identity, contact details, billing information) and device-linked
    identifiers (IMEI numbers, serial numbers, Samsung Account IDs, repair history).

2.2 All PII and device-linked identifiers must be processed within US-based
    data centers only. No PII shall be transmitted to or stored on servers located
    outside the United States under any circumstances.

2.3 Non-PII aggregate telemetry and fully anonymized claim classification statistics
    (stripped of all device-linked identifiers) may be used for model performance
    evaluation within Assurant's internal systems only.

2.4 Provider shall not use Samsung customer data, device identifiers, Galaxy AI
    usage patterns, or Samsung Care+ claim records for the purpose of training,
    fine-tuning, or benchmarking any AI model without explicit prior written consent
    from Samsung Electronics America's legal and data governance team.

2.5 Conversation logs containing PII must be retained for a minimum of 3 years
    for warranty dispute resolution purposes and must be purged no later than 5 years
    from the date of creation unless a legal hold is in effect.

2.6 All data at rest must be encrypted using AES-256. All data in transit must
    use TLS 1.3 or higher. Encryption key management must remain under
    Assurant/Provider control and not be delegated to third-party AI providers.

2.7 Samsung Electronics America may request a data processing audit with 10 business
    days advance notice. Provider must produce routing logs showing which AI provider
    processed each request category within 5 business days of such a request.

## SECTION 3 — APPROVED AI PROVIDERS
3.1 Samsung Electronics America approves the following AI model providers for use
    under this agreement:
    - Anthropic (Claude model family)
    - OpenAI (GPT model family)
    - Google (Gemini model family)

3.2 The following providers are explicitly prohibited under this agreement. This
    prohibition is a hard constraint and may not be overridden at runtime:
    - DeepSeek (Hangzhou DeepSeek Artificial Intelligence Co., Ltd.)
    - Baidu (ERNIE / Wenxin model family)
    - Alibaba (Qwen / Tongyi model family)
    - Any AI model provider headquartered in the People's Republic of China or
      operating primary AI inference infrastructure within PRC jurisdiction.
    Basis: Samsung Electronics America's corporate IP protection policy and
    competitive sensitivity requirements. Samsung device telemetry and Galaxy AI
    usage data must not transit infrastructure operated by companies that are
    direct or indirect competitors in the global device AI market.

3.3 Provider may not add, substitute, or rotate AI providers without 30-day advance
    written notice to Samsung Electronics America's technology and legal review team.

3.4 Samsung Electronics America reserves the right to audit AI provider routing
    logs upon 5 business days' notice. Provider must retain per-request routing
    records (provider used, model tier, request classification) for a minimum of
    90 days.

## SECTION 4 — PERFORMANCE REQUIREMENTS
4.1 Tier 1 — End-User Self-Service Performance Targets
    4.1.1 Standard queries (eligibility checks, deductible lookup, claim status):
          Response delivery within 1500ms at the 95th percentile.
    4.1.2 Guided triage flows (damage assessment, repair routing):
          Response delivery within 3000ms at the 95th percentile.
    4.1.3 Galaxy AI feature malfunction queries (per Section 1.3):
          Response delivery within 4000ms at the 95th percentile.
          Speed may be traded for analytical depth in this category.

4.2 Tier 2 — Internal Agent Assist Performance Targets
    4.2.1 Single-document claim summaries:
          Response delivery within 3000ms at the 95th percentile.
    4.2.2 Multi-document claim synthesis (up to 40 pages):
          Response delivery within 8000ms at the 95th percentile.
    4.2.3 Quality and accuracy are the primary performance metrics for Tier 2.
          Agent satisfaction score must average 4.2/5.0 or above per quarterly review.

4.3 System Uptime SLA: 99.9% measured on a monthly rolling basis.
    Planned maintenance windows must not exceed 4 hours per calendar month and
    must be scheduled between 2:00 AM – 6:00 AM Pacific Time with 72-hour advance
    notice to Samsung Electronics America's operations team.

4.4 Galaxy AI Feature Query Routing Requirement
    Queries classified under Section 1.3 (Galaxy AI feature support) must be routed
    to a model tier with demonstrated strong technical domain knowledge and multi-step
    reasoning capability. Lightweight or economy-tier models are not permitted for
    this query class. Provider shall document model tier assignments for Galaxy AI
    queries in monthly performance reports.

4.5 Supported languages: English, Spanish, Korean.
    All three languages must be supported across both Tier 1 and Tier 2.

## SECTION 5 — COST AND BILLING
5.1 Samsung Electronics America operates under a tiered cost model reflecting the
    different value requirements of each service tier:
    - Tier 1 (End-User Self-Service): cost efficiency is a primary optimization
      target. The Platform should route simple queries to the most cost-effective
      compliant model tier without degrading response quality below acceptable
      thresholds.
    - Tier 2 (Internal Agent Assist): quality and analytical accuracy are primary.
      Cost is a secondary consideration. Premium model tiers should be used when
      query complexity warrants them.
    - Galaxy AI Feature Queries: treated as Tier 2 cost profile regardless of
      which surface they originate from.

5.2 Combined monthly AI inference budget: $40,000 blended across all tiers.

5.3 Provider shall deliver monthly cost attribution reports itemized by:
    - Service tier (Tier 1 / Tier 2 / Galaxy AI Feature)
    - AI provider and model tier used
    - Query complexity classification (simple / medium / complex)
    - Estimated cost per resolved interaction

5.4 Provider shall alert Samsung Electronics America's vendor operations team when
    projected monthly spend is expected to exceed 85% of the monthly budget cap,
    with a breakdown of which query category is driving the overage.

5.5 Cost optimization through intelligent downtiering is expected and required for
    Tier 1 simple queries. Provider shall not default to premium model tiers for
    routine eligibility and status checks.

## SECTION 6 — USE CASE SPECIFICATIONS
6.1 Tier 1 — End-User Self-Service
    Primary use cases:
    (a) Samsung Care+ claim eligibility and deductible lookup
    (b) Damage triage: cracked screen, liquid damage, mechanical failure, theft/loss
    (c) Repair appointment scheduling and certified repair center lookup
    (d) Galaxy AI feature malfunction reporting and escalation
    (e) Replacement device status tracking

    Expected daily volume: approximately 18,000 queries per day
    Estimated query distribution:
        - Simple queries (eligibility, status, deductible lookup): 50%
        - Medium queries (guided triage, repair scheduling, coverage questions): 35%
        - Complex queries (multi-device claims, Galaxy AI feature issues,
          escalation workflows): 15%

6.2 Tier 2 — Internal Agent Assist
    Primary use cases:
    (a) Claim history synthesis for agents handling customer escalations
    (b) Multi-document review for disputed or complex claims
    (c) Coverage policy clarification for bundled Samsung Care+ plans
    (d) Escalation draft preparation for legal or executive review

    User base: approximately 400 Samsung Care+ claims agents and senior technicians
    Expected daily volume: approximately 4,000 queries per day
    Estimated query distribution:
        - Simple queries (quick policy lookups, status confirmations): 20%
        - Medium queries (claim summaries, coverage analysis, plan comparison): 45%
        - Complex queries (multi-document review, dispute analysis,
          Galaxy AI technical escalations): 35%

6.3 Galaxy AI Feature Query Classification Note
    As of the effective date of this agreement, Galaxy AI features requiring
    specialized support routing include:
    - Circle to Search (visual search from any app)
    - Live Translate (real-time call and text translation, 20+ languages)
    - Call Summary and Transcript Assist (on-device AI transcription)
    - Generative Edit and Sketch to Image (AI-powered photo editing)
    - Now Brief and Now Bar (proactive AI context panel)
    - Interpreter Mode (live spoken language interpretation)
    - Chat Assist (AI-powered message drafting)
    - Multi-app AI task automation (cross-app voice command execution)

    Samsung Electronics America may update this feature list by written notice
    without requiring a full contract amendment. Provider must incorporate updated
    feature lists within 10 business days of receipt.

6.4 Multi-Language Requirements
    All three supported languages (English, Spanish, Korean) must be available
    across both service tiers. Korean language support is required due to the
    significant Korean-speaking Samsung Care+ subscriber base in the United States.
    Language detection should be automatic; users must not be required to declare
    their language preference manually.
