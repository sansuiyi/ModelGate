# Aurora Media Group — AI Content Moderation & Summarization Agreement
## Contract ID: AM-2026-2217
## Effective Date: April 1, 2026

## PARTIES
This agreement is entered between Assurant, Inc. ("Provider") and Aurora Media Group
("Customer") for AI-powered content moderation and news summarization services.

## SECTION 1 — SERVICE DESCRIPTION
Provider shall deploy an AI platform supporting:
- User-generated content moderation and toxicity detection
- News article summarization and headline generation
- Comment section sentiment analysis
- Automated content tagging and categorization

## SECTION 2 — DATA HANDLING AND PRIVACY
2.1 Content data is classified as standard privacy tier.
2.2 Data may be processed in US or EU data centers (region: any).
2.3 Retention of moderation logs shall not exceed 6 months.

## SECTION 3 — APPROVED AI PROVIDERS
3.1 Approved providers: Anthropic (Claude), OpenAI (GPT), Google (Gemini).
3.2 China-based providers are strictly prohibited.

## SECTION 4 — PERFORMANCE REQUIREMENTS
4.1 Content moderation must return within 800ms (low_latency priority).
4.2 News summarization may take up to 5000ms.
4.3 Moderation throughput is critical for live comment streams.

## SECTION 5 — COST AND BILLING
5.1 Cost sensitivity is high for moderation (bulk simple queries).
5.2 Monthly budget cap: $12,000.

## SECTION 6 — USE CASE
6.1 Primary use case: content moderation and summarization
6.2 Expected volume: 40,000 queries per day
6.3 Distribution: simple 65%, medium 30%, complex 5%
