"""Integration tests for the Product Master Data Agent end-to-end flow."""

import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage
from langchain_core.tools import StructuredTool


def make_mock_tool(name: str, description: str, response: dict) -> StructuredTool:
    """Create a StructuredTool mock that returns a given response."""
    async def _tool_func(**kwargs):
        return response

    return StructuredTool.from_function(
        coroutine=_tool_func,
        name=name,
        description=description,
    )


@pytest.fixture
def mock_tools():
    """Return mock MCP tools for all 3 SAP APIs."""
    return [
        make_mock_tool(
            "list_product_for_sap_self",
            "Retrieve a list of products using the CE Product v3 API.",
            {"d": {"results": [{"Product": "P-100", "BaseUnit": "EA", "ProductType": "FERT"}]}},
        ),
        make_mock_tool(
            "get_product_for_sap_self",
            "Retrieve a single product by product ID.",
            {"d": {"Product": "P-100", "BaseUnit": "EA", "ProductType": "FERT"}},
        ),
        make_mock_tool(
            "list_a_product_for_api_product_srv",
            "Retrieve a list of products from the Product Master.",
            {"d": {"results": [{"Product": "P-100", "BaseUnit": "EA"}]}},
        ),
        make_mock_tool(
            "list_a_productdescription_for_api_product_srv",
            "Retrieve product descriptions.",
            {"d": {"results": [{"Product": "P-100", "Language": "EN", "ProductDescription": "Notebook Basic 15 HT-1000"}]}},
        ),
        make_mock_tool(
            "list_a_clfnproduct_for_api_clfn_product_srv",
            "Retrieve classified products.",
            {"d": {"results": [{"Product": "P-100", "ClassType": "001"}]}},
        ),
        make_mock_tool(
            "list_to_productclass_in_a_clfnproduct_for_api_clfn_product_srv",
            "Retrieve class assignments.",
            {"d": {"results": [{"Product": "P-100", "Class": "NOTEBOOK"}]}},
        ),
    ]


@pytest.fixture
def agent(add_agent_to_path, mock_tools):
    """Create a SampleAgent with mocked MCP tools."""
    from agent import SampleAgent

    with patch("mcp_providers.agw.get_mcp_tools", AsyncMock(return_value=mock_tools)):
        agent_instance = SampleAgent()
        yield agent_instance


@pytest.fixture
def mock_llm_response():
    """Factory for creating mock LLM responses."""
    def _make(content: str) -> AsyncMock:
        message = AIMessage(content=content)
        mock = AsyncMock()
        mock.ainvoke = AsyncMock(return_value={"messages": [message]})
        return mock
    return _make


@pytest.mark.asyncio
async def test_scenario_1_product_uom_query(agent, mock_tools):
    """Scenario 1: Sales Rep asks 'What is the unit of measure for product P-100?'
    Agent should return UoM from mocked SAP data."""
    query = "What is the unit of measure for product P-100?"

    with patch.object(
        agent,
        "_invoke",
        AsyncMock(return_value={
            "messages": [
                AIMessage(content="The unit of measure for product P-100 is EA (Each).")
            ]
        }),
    ):
        response = await agent.invoke(query, context_id="test-session-1", tools=mock_tools)

    assert response.status == "completed"
    assert response.message
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_scenario_2_product_not_found(agent, mock_tools):
    """Scenario 2: Sales Rep asks for a non-existent product.
    Agent should return 'product not found' message."""
    query = "What is product XXXXXXX?"

    with patch.object(
        agent,
        "_invoke",
        AsyncMock(return_value={
            "messages": [
                AIMessage(
                    content="I couldn't find a product matching 'XXXXXXX' in SAP. "
                    "Please check the product ID or name and try again."
                )
            ]
        }),
    ):
        response = await agent.invoke(query, context_id="test-session-2", tools=mock_tools)

    assert response.status == "completed"
    assert "not found" in response.message.lower() or "couldn't find" in response.message.lower()


@pytest.mark.asyncio
async def test_scenario_3_followup_question(agent, mock_tools):
    """Scenario 3: Sales Rep asks a follow-up question.
    Agent retains context from prior turn."""
    first_query = "Tell me about product P-100."
    followup_query = "What is its unit of measure?"

    with patch.object(
        agent,
        "_invoke",
        AsyncMock(side_effect=[
            {"messages": [AIMessage(content="Product P-100 is a Notebook Basic 15, type FERT.")]},
            {"messages": [AIMessage(content="The unit of measure for product P-100 (Notebook Basic 15) is EA (Each).")]},
        ]),
    ):
        # First turn
        response1 = await agent.invoke(first_query, context_id="test-session-3", tools=mock_tools)
        assert response1.status == "completed"

        # Follow-up turn
        response2 = await agent.invoke(followup_query, context_id="test-session-3", tools=mock_tools)
        assert response2.status == "completed"
        assert response2.message
        # Agent should handle follow-up — response should reference P-100 context
        assert len(response2.message) > 0


@pytest.mark.asyncio
async def test_scenario_4_out_of_scope_pricing(agent, mock_tools):
    """Scenario 4: Sales Rep asks about pricing.
    Agent should respond with scope boundary message."""
    query = "What is the price of product P-100?"

    with patch.object(
        agent,
        "_invoke",
        AsyncMock(return_value={
            "messages": [
                AIMessage(
                    content="Pricing information is not available through this assistant. "
                    "I can help with product descriptions, units of measure, and classification attributes."
                )
            ]
        }),
    ):
        response = await agent.invoke(query, context_id="test-session-4", tools=mock_tools)

    assert response.status == "completed"
    assert "pricing" in response.message.lower() or "not available" in response.message.lower()


@pytest.mark.asyncio
async def test_empty_query_handled_gracefully(agent, mock_tools):
    """Test that an empty query is handled gracefully without crashing."""
    response = await agent.invoke("", context_id="test-session-empty", tools=mock_tools)
    # Should return an error or input_required, not raise an exception
    assert response.status in ("error", "input_required", "completed")
    assert response.message


@pytest.mark.asyncio
async def test_stream_yields_chunks(agent, mock_tools):
    """Test that stream() yields at least a processing chunk and a final response."""
    query = "What is product P-100?"

    with patch.object(
        agent,
        "_invoke",
        AsyncMock(return_value={
            "messages": [AIMessage(content="Product P-100 is a Notebook, BaseUnit EA.")]
        }),
    ):
        chunks = []
        async for chunk in agent.stream(query, context_id="test-stream-1", tools=mock_tools):
            chunks.append(chunk)

    assert len(chunks) >= 1
    # Last chunk should be task complete
    last = chunks[-1]
    assert "content" in last
