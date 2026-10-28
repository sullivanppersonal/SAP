# Specification: product-master-data-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read the project input (`product-requirements-document.md` and `intent.md`)
- [x] Bootstrap agent code in `assets/product-master-data-agent/` using instructions from the sap-agent-bootstrap section.
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

- [x] Evaluate whether runtime skills are needed for this agent
- [x] Create `assets/product-master-data-agent/app/skills/product-query/SKILL.md`

---

## Project-Specific Tasks

### Natural Language Product Query (R1)

- [x] Configure the agent system prompt in `assets/product-master-data-agent/app/agent.py`

### SAP S/4HANA Product Data Retrieval (R2)

- [x] Generate MCP translation files from the downloaded API specs (invoke `mcp-translation-file` skill)
- [x] Invoke `setup-solution` skill to create `solution.yaml` and all `asset.yaml` files
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module
- [x] Add all MCP server dependencies to `asset.yaml` under `requires`

### Product Classification and Attributes Query (R3)

- [x] Verify the `API_CLFN_PRODUCT_SRV` MCP tools cover classification and attribute retrieval
- [x] Add agent system prompt instruction to use the classification MCP tool

### Multi-Turn Conversation Support (R4)

- [x] Confirm the bootstrapped agent framework retains conversation context between turns
- [x] Add a system prompt instruction for follow-up handling
- [x] Validate multi-turn behaviour in the integration test

### Graceful Handling of Missing or Unavailable Data (R5)

- [x] Add agent system prompt instruction for not-found handling
- [x] Add agent system prompt instruction for out-of-scope queries (pricing, stock)
- [x] Add agent system prompt instruction for API errors

---

## Business Instrumentation

- [x] Implement business step instrumentation for all 5 milestones (M1–M5) with structured logging and OpenTelemetry spans
- [x] Extract business logic from `stream()` into a plain async helper `_run_agent()`
- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

- [x] Verify `specification/product-master-data-agent/api-specs/` contains all 3 downloaded EDMX files
- [x] Invoke `mcp-translation-file` skill for each EDMX spec — 3 MCP server translation files generated
- [x] Invoke `setup-solution` skill to create/register MCP server assets in `solution.yaml`
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` — no direct HTTP clients
- [x] Add MCP server entries to `asset.yaml` under `requires` for all 3 generated MCP servers
- [x] Generate `mcp-mock.json` using the `mcp-mock-config` skill

---

## Testing

- [x] `conftest.py` only sets `IBD_TESTING=true`
- [x] Write unit tests in `assets/product-master-data-agent/tests/`:
  - `test_product_lookup_tool.py`
  - `test_product_classification_tool.py`
  - `test_ce_product_tool.py`
- [x] Write one integration test `test_agent_flow.py` with 4 scenarios
- [x] Run `pytest` from `assets/product-master-data-agent/` — 125/125 passed
- [x] Coverage: 79% (above 70% threshold)
- [x] Run `pytest` again to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/product-master-data-agent/`
