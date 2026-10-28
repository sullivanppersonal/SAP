# Product Master Data AI Agent for Sales Representatives

SAP S/4HANA Public Cloud Edition — Natural Language Product Query Agent

## Business challenge

Sales Representatives waste time switching between SAP S/4HANA screens to find basic product master data. They currently depend on back-office colleagues to retrieve product information, which slows down live customer conversations and reduces overall sales effectiveness. The goal is to give Sales Reps an AI-powered assistant they can ask directly in natural language to get instant, accurate product answers — without ever opening SAP.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time to find product information | 5 minutes | Under 30 seconds | 3 months | Product data lookup during sales interactions | user |

## Key Milestones

1. **Query Received** — Sales Rep submits a natural language question about a product (e.g. "What is the unit of measure for product X?")
2. **Product Identified** — Agent resolves the product from the question and queries SAP S/4HANA via the Product Master API
3. **Answer Returned** — Agent delivers a clear, structured answer with the relevant product details
4. **Follow-up Handled** — Sales Rep refines or continues the conversation (e.g. "What about product Y?")
5. **Session Complete** — Interaction concludes and Sales Rep has the information needed for their customer

## Business Architecture (RBA)

### End-to-End Process

Lead to Cash Standard B2B

### Process Hierarchy

```
Lead to Cash Standard B2B (E2E)
└── Plan to Optimize Marketing and Sales
    └── Plan prices and promotions (BPS-359_002)
        └── Plan and define sales prices
        └── Manage and access product master data
```

### Summary

Sales Reps querying product master data maps to the Lead to Cash Standard B2B process, specifically the "Plan prices and promotions" sub-process, where product planning, pricing, and definition capabilities are governed by SAP S/4HANA Cloud Public Edition.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Gap? | Notes / assumptions |
|------------------------|------------------------|------------|-------------------|--------------------|--------------------|------|---------------------|
| Query product basic details (name, description, UoM) | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:API_PRODUCT_SRV:v1` | — | — | — | No | API available; no pre-built MCP server, custom integration required |
| Query product with classification/attributes | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1` | — | — | — | No | API available; no pre-built MCP server |
| Product data (Cloud Edition v3) | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:CE_PRODUCT_0003:v3` | — | — | — | No | Latest CE product API, preferred for Public Cloud |
| Natural language querying interface for Sales Reps | No standard SAP product | — | — | — | — | Yes | Requires custom AI Agent to translate NL questions to API calls |

### Key findings

- SAP S/4HANA Cloud Public Edition provides the required product master data APIs (Product Master, Product Classification, CE Product v3)
- No pre-built MCP servers exist for these APIs — a custom MCP integration layer must be generated from the API specifications
- Several APIs returned as `unavailable` (Product Specification, Pricing Service) — these are excluded from scope
- The core gap is the absence of a natural language interface — this is the primary driver for a custom AI Agent
- The solution is self-contained within SAP S/4HANA Public Cloud; no additional SAP products are required
- No n8n workflow orchestration is needed — the agent handles reasoning and API calls autonomously

## Recommendations

### AI-Powered Product Query Agent for Sales Representatives

#### Executive Summary

Python AI agent that answers product questions via SAP APIs in real time.

#### Recommended Solution

A pro-code Python AI agent (A2A protocol) that allows Sales Representatives to ask questions about product master data in natural language. The agent connects to SAP S/4HANA Cloud Public Edition via the Product Master (A2X) API and the CE Product API, translates questions into API calls, and returns readable answers. The agent is instrumented with OpenTelemetry for observability and includes built-in prompt injection protection.

#### Problem Statement

Sales Representatives must navigate complex SAP S/4HANA screens or contact back-office colleagues to retrieve product information. This creates delays in customer conversations, increases dependency on support staff, and reduces sales efficiency.

#### Affected User Roles

- Sales Representatives (primary users)
- Back-office / product data team (reduced dependency)

#### Important factors

##### Eliminates screen-switching overhead
Sales Reps can ask product questions in plain language without logging into SAP or navigating multiple screens.

##### Reduces back-office dependency
Product lookups that previously required a colleague can be answered autonomously by the agent.

##### Instant responses during customer conversations
Sub-30-second response time enables Sales Reps to answer customer queries in real time.

#### Potential risks

##### API coverage for product data
Not all product attributes may be exposed via the available APIs (e.g. pricing specs marked unavailable). Scope is limited to basic product master data.

##### Data freshness
Agent responses reflect live SAP data — any master data quality issues in S/4HANA will surface in agent answers.

#### Recommended solution category

AI Agent

#### Intent fit
92%
