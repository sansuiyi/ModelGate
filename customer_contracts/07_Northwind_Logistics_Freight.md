# Northwind Logistics — AI Freight Routing & Document Processing Agreement
## Contract ID: NW-2026-4421
## Effective Date: February 1, 2026

## PARTIES
This agreement is entered between Assurant, Inc. ("Provider") and Northwind Logistics
("Customer") for the deployment of AI-powered freight routing and shipping document
processing services.

## SECTION 1 — SERVICE DESCRIPTION
Provider shall deploy an AI assistant that handles:
- Shipping document classification and data extraction (bills of lading, invoices)
- Freight route optimization queries
- Customs compliance question answering
- Shipment tracking status resolution

## SECTION 2 — DATA HANDLING AND PRIVACY
2.1 Shipping data is classified as standard privacy tier.
2.2 All data must be processed within US-based data centers only.
2.3 Data retention for conversation logs shall not exceed 12 months.

## SECTION 3 — APPROVED AI PROVIDERS
3.1 The Customer approves the following providers:
    - Anthropic (Claude model family)
    - OpenAI (GPT model family)
    - Google (Gemini model family)
3.2 China-based providers (DeepSeek, Baidu, Alibaba) are strictly prohibited.

## SECTION 4 — PERFORMANCE REQUIREMENTS
4.1 Document classification must return within 1000ms.
4.2 Route optimization queries may take up to 5000ms.
4.3 The system should prioritize response speed (low_latency).

## SECTION 5 — COST AND BILLING
5.1 Customer is highly cost-sensitive for routine document classification.
5.2 Monthly AI inference budget cap: $8,000.

## SECTION 6 — USE CASE
6.1 Primary use case: freight document processing and routing
6.2 Expected volume: 15,000 queries per day
6.3 Distribution: simple 70%, medium 25%, complex 5%
