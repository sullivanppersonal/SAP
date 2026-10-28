---
name: product-query
description: Instructions for handling product master data queries from Sales Representatives, including ambiguity resolution, tool selection, and scope boundary enforcement.
---

# Product Query Handling

## When to Use This Skill

Load this skill when a Sales Representative asks any question about a product — including product descriptions, units of measure, classifications, attributes, or specifications.

## Step-by-Step Decision Tree

### Step 1: Extract the Product Identifier

1. Read the user's question carefully.
2. Look for a product identifier: a product ID (e.g. "P-100", "TG11", "MAT-001") or a product name/keyword (e.g. "blue widget", "industrial pump").
3. If a clear product ID is found → proceed to Step 3.
4. If only a keyword or name is found → proceed to Step 2.
5. If no product reference at all → ask: "Which product are you looking for? Please provide the product ID or name."

### Step 2: Resolve Ambiguous Product References

If the product reference is ambiguous (only a name or keyword, no ID):
1. Ask a clarifying question: "Could you please provide the product ID for [product name]? For example: P-100 or TG11."
2. Wait for the user to provide the product ID before proceeding.
3. Do NOT guess or assume a product ID — always confirm with the user.

### Step 3: Select the Appropriate MCP Tool

Based on what the user is asking for:

| User Question Type | MCP Tool to Use |
|--------------------|-----------------|
| Product name, description, unit of measure, base quantity | Use `API_PRODUCT_SRV` tools (e.g. list or read A_Product) |
| Product text / description in a specific language | Use `API_PRODUCT_SRV` tools for A_ProductDescription |
| Product classification category, class, or type | Use `API_CLFN_PRODUCT_SRV` tools (A_ClfnProduct, A_ClfnProductClass) |
| Product characteristic / attribute value | Use `API_CLFN_PRODUCT_SRV` tools (A_ClfnProductCharc) |
| General product lookup with latest CE API | Use `CE_PRODUCT_0003` tools (Product, ProductText) |

When in doubt between `API_PRODUCT_SRV` and `CE_PRODUCT_0003`, prefer `CE_PRODUCT_0003` as it is the latest Cloud Edition API.

### Step 4: Handle Tool Results

**If data is returned successfully:**
- Format the answer in plain language — do NOT use SAP field codes (e.g. say "Unit of Measure: Each" not "MEINS: EA")
- Present the most relevant fields clearly
- Emit: `M3.achieved: product data retrieved from SAP and answer delivered`

**If the product is not found (empty result or 404):**
- Respond: "I couldn't find a product matching '[product reference]' in SAP. Please check the product ID or name and try again."
- Emit: `M3.missed: SAP API returned no data or an error — fallback message delivered`

**If the tool returns an API error:**
- Respond: "I'm having trouble retrieving product data right now. Please try again in a moment."
- Do NOT expose technical error details or HTTP status codes.
- Emit: `M3.missed: SAP API returned no data or an error — fallback message delivered`

### Step 5: Handle Out-of-Scope Requests

If the user asks about:
- **Pricing / price conditions / sales prices** → respond: "Pricing information is not available through this assistant. I can help with product descriptions, units of measure, and classification attributes."
- **Stock levels / inventory / availability** → respond: "Stock and inventory information is not available through this assistant. I can help with product descriptions, units of measure, and classification attributes."
- **Purchase orders, deliveries, invoices** → respond: "That information is outside my scope. I specialise in product master data — descriptions, units of measure, and classification attributes."

### Step 6: Handle Follow-Up Questions

1. Retain the product context from the previous turn.
2. If the user asks "what about product Y?", treat it as a new product lookup for product Y.
3. If the user asks "what is its unit of measure?" without naming a product, use the product from the most recent successful lookup.
4. If session context is lost, ask: "Which product are you referring to?"
5. Emit: `M4.achieved: follow-up query processed with conversation context`

## Examples

**Example 1 — Direct product ID query:**
> User: "What is the unit of measure for product P-100?"
> Action: Call CE_PRODUCT_0003 → read Product(ProductID='P-100') → return BaseUnit field as plain text.

**Example 2 — Classification query:**
> User: "What classification does product TG11 belong to?"
> Action: Call API_CLFN_PRODUCT_SRV → read A_ClfnProduct(Product='TG11') → return class assignments.

**Example 3 — Ambiguous reference:**
> User: "Tell me about the industrial pump."
> Action: Ask "Could you please provide the product ID for the industrial pump? For example: P-100 or TG11."

**Example 4 — Out of scope:**
> User: "What is the price of product P-100?"
> Action: Respond with scope boundary message — do NOT call any pricing API.
