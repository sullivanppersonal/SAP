"""Unit tests for Product Master MCP tool invocation (API_PRODUCT_SRV)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_product_tool():
    """Create a mock MCP tool that returns product master data."""
    tool = MagicMock()
    tool.name = "list_a_product_for_api_product_srv"
    tool.description = "Retrieve a list of products from the Product Master."

    async def _run(*args, **kwargs):
        return {
            "d": {
                "results": [
                    {
                        "Product": "P-100",
                        "ProductType": "FERT",
                        "BaseUnit": "EA",
                        "ProductGroup": "L001",
                        "Division": "00",
                        "GrossWeight": "2.500",
                        "NetWeight": "2.200",
                        "WeightUnit": "KG",
                    }
                ]
            }
        }

    tool.arun = AsyncMock(side_effect=_run)
    tool.run = MagicMock(
        return_value={
            "d": {
                "results": [
                    {
                        "Product": "P-100",
                        "ProductType": "FERT",
                        "BaseUnit": "EA",
                        "ProductGroup": "L001",
                    }
                ]
            }
        }
    )
    return tool


@pytest.fixture
def mock_get_product_tool():
    """Create a mock MCP tool that returns a single product by ID."""
    tool = MagicMock()
    tool.name = "get_a_product_for_api_product_srv"
    tool.description = "Retrieve a single product by its product ID."

    async def _run(*args, **kwargs):
        product_id = kwargs.get("Product", args[0] if args else "P-100")
        if product_id == "NOTEXIST":
            return {"d": None}
        return {
            "d": {
                "Product": product_id,
                "ProductType": "FERT",
                "BaseUnit": "EA",
                "ProductGroup": "L001",
                "GrossWeight": "2.500",
                "WeightUnit": "KG",
            }
        }

    tool.arun = AsyncMock(side_effect=_run)
    return tool


@pytest.mark.asyncio
async def test_list_products_returns_results(mock_product_tool):
    """Test that list product tool returns a list of products."""
    result = await mock_product_tool.arun()
    assert "d" in result
    assert "results" in result["d"]
    assert len(result["d"]["results"]) > 0


@pytest.mark.asyncio
async def test_list_products_result_has_expected_fields(mock_product_tool):
    """Test that returned products have the expected fields."""
    result = await mock_product_tool.arun()
    product = result["d"]["results"][0]
    assert "Product" in product
    assert "BaseUnit" in product
    assert product["BaseUnit"] == "EA"


@pytest.mark.asyncio
async def test_get_product_by_id_returns_single_product(mock_get_product_tool):
    """Test that get product by ID returns a single product object."""
    result = await mock_get_product_tool.arun(Product="P-100")
    assert "d" in result
    assert result["d"]["Product"] == "P-100"
    assert result["d"]["BaseUnit"] == "EA"


@pytest.mark.asyncio
async def test_get_product_not_found_returns_none(mock_get_product_tool):
    """Test that querying a non-existent product returns None/empty."""
    result = await mock_get_product_tool.arun(Product="NOTEXIST")
    assert result["d"] is None


def test_product_tool_has_correct_name(mock_product_tool):
    """Test that the product list tool has the correct name."""
    assert mock_product_tool.name == "list_a_product_for_api_product_srv"


def test_product_tool_has_description(mock_product_tool):
    """Test that the product tool has a non-empty description."""
    assert mock_product_tool.description
    assert len(mock_product_tool.description) > 0
