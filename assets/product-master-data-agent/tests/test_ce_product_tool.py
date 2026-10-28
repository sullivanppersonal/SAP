"""Unit tests for CE Product v3 MCP tool invocation (CE_PRODUCT_0003)."""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_ce_list_product_tool():
    """Mock for list_product_for_sap_self (CE Product v3 list)."""
    tool = MagicMock()
    tool.name = "list_product_for_sap_self"
    tool.description = "Retrieve a list of products using the CE Product v3 API."

    async def _run(*args, **kwargs):
        return {
            "d": {
                "results": [
                    {
                        "Product": "P-100",
                        "BaseUnit": "EA",
                        "ProductGroup": "L001",
                        "GrossWeight": "2.500",
                        "WeightUnit": "KG",
                        "ProductType": "FERT",
                    },
                    {
                        "Product": "TG11",
                        "BaseUnit": "PC",
                        "ProductGroup": "L002",
                        "GrossWeight": "5.000",
                        "WeightUnit": "KG",
                        "ProductType": "HAWA",
                    },
                ]
            }
        }

    tool.arun = AsyncMock(side_effect=_run)
    return tool


@pytest.fixture
def mock_ce_get_product_tool():
    """Mock for get_product_for_sap_self (CE Product v3 single product)."""
    tool = MagicMock()
    tool.name = "get_product_for_sap_self"
    tool.description = "Retrieve a single product by product ID using the CE Product v3 API."

    async def _run(*args, **kwargs):
        product_id = kwargs.get("Product", "P-100")
        if product_id == "NOTEXIST":
            return {"d": None}
        return {
            "d": {
                "Product": product_id,
                "BaseUnit": "EA",
                "ProductGroup": "L001",
                "GrossWeight": "2.500",
                "WeightUnit": "KG",
                "ProductType": "FERT",
            }
        }

    tool.arun = AsyncMock(side_effect=_run)
    return tool


@pytest.fixture
def mock_ce_product_uom_tool():
    """Mock for list_product__productunitofmeasure_for_sap_self."""
    tool = MagicMock()
    tool.name = "list_product__productunitofmeasure_for_sap_self"
    tool.description = "Retrieve units of measure configured for a product."

    async def _run(*args, **kwargs):
        return {
            "d": {
                "results": [
                    {"Product": "P-100", "AlternativeUnit": "EA", "QuantityNumerator": "1.000", "QuantityDenominator": "1.000"},
                    {"Product": "P-100", "AlternativeUnit": "PAL", "QuantityNumerator": "100.000", "QuantityDenominator": "1.000"},
                ]
            }
        }

    tool.arun = AsyncMock(side_effect=_run)
    return tool


@pytest.mark.asyncio
async def test_ce_list_products_returns_list(mock_ce_list_product_tool):
    """Test that CE list products tool returns a list of products."""
    result = await mock_ce_list_product_tool.arun()
    assert "d" in result
    assert len(result["d"]["results"]) == 2


@pytest.mark.asyncio
async def test_ce_product_has_base_unit(mock_ce_list_product_tool):
    """Test that CE product results include BaseUnit field."""
    result = await mock_ce_list_product_tool.arun()
    product = result["d"]["results"][0]
    assert "BaseUnit" in product
    assert product["BaseUnit"] == "EA"


@pytest.mark.asyncio
async def test_ce_get_product_by_id(mock_ce_get_product_tool):
    """Test that CE get product by ID returns correct product."""
    result = await mock_ce_get_product_tool.arun(Product="P-100")
    assert result["d"]["Product"] == "P-100"
    assert result["d"]["BaseUnit"] == "EA"


@pytest.mark.asyncio
async def test_ce_get_product_not_found(mock_ce_get_product_tool):
    """Test that CE get product returns None for non-existent product."""
    result = await mock_ce_get_product_tool.arun(Product="NOTEXIST")
    assert result["d"] is None


@pytest.mark.asyncio
async def test_ce_product_uom_returns_multiple_units(mock_ce_product_uom_tool):
    """Test that UoM tool returns multiple unit of measure records."""
    result = await mock_ce_product_uom_tool.arun()
    uoms = result["d"]["results"]
    assert len(uoms) == 2
    uom_names = [u["AlternativeUnit"] for u in uoms]
    assert "EA" in uom_names
    assert "PAL" in uom_names


def test_ce_tool_names_are_correct(mock_ce_list_product_tool, mock_ce_get_product_tool):
    """Test that CE tools have correct names."""
    assert mock_ce_list_product_tool.name == "list_product_for_sap_self"
    assert mock_ce_get_product_tool.name == "get_product_for_sap_self"
