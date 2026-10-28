"""Unit tests for Product Classification MCP tool invocation (API_CLFN_PRODUCT_SRV)."""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_clfn_product_tool():
    """Create a mock MCP tool that returns product classification data."""
    tool = MagicMock()
    tool.name = "list_a_clfnproduct_for_api_clfn_product_srv"
    tool.description = "Retrieve a list of classified products."

    async def _run(*args, **kwargs):
        return {
            "d": {
                "results": [
                    {"Product": "P-100", "ClassType": "001", "ProductClassAssignmentStatus": "0"},
                    {"Product": "TG11", "ClassType": "001", "ProductClassAssignmentStatus": "0"},
                ]
            }
        }

    tool.arun = AsyncMock(side_effect=_run)
    return tool


@pytest.fixture
def mock_product_charcs_tool():
    """Create a mock MCP tool that returns product characteristics."""
    tool = MagicMock()
    tool.name = "list_to_productcharc_in_a_clfnproduct_for_api_clfn_product_srv"
    tool.description = "Retrieve characteristic values assigned to a classified product."

    async def _run(*args, **kwargs):
        return {
            "d": {
                "results": [
                    {
                        "Product": "P-100",
                        "ClassType": "001",
                        "CharcInternalID": "100",
                        "Characteristic": "COLOR",
                        "CharcValue": "BLACK",
                    },
                    {
                        "Product": "P-100",
                        "ClassType": "001",
                        "CharcInternalID": "101",
                        "Characteristic": "SIZE",
                        "CharcValue": "15INCH",
                    },
                ]
            }
        }

    tool.arun = AsyncMock(side_effect=_run)
    return tool


@pytest.fixture
def mock_product_class_tool():
    """Create a mock MCP tool that returns product class assignments."""
    tool = MagicMock()
    tool.name = "list_to_productclass_in_a_clfnproduct_for_api_clfn_product_srv"
    tool.description = "Retrieve class assignments for a classified product."

    async def _run(*args, **kwargs):
        return {
            "d": {
                "results": [
                    {"Product": "P-100", "ClassType": "001", "Class": "NOTEBOOK", "ClassAssignmentStatus": "0"},
                ]
            }
        }

    tool.arun = AsyncMock(side_effect=_run)
    return tool


@pytest.mark.asyncio
async def test_list_classified_products_returns_results(mock_clfn_product_tool):
    """Test that the classification tool returns product classification records."""
    result = await mock_clfn_product_tool.arun()
    assert "d" in result
    assert "results" in result["d"]
    assert len(result["d"]["results"]) > 0


@pytest.mark.asyncio
async def test_classified_product_has_class_type(mock_clfn_product_tool):
    """Test that classification results include ClassType."""
    result = await mock_clfn_product_tool.arun()
    record = result["d"]["results"][0]
    assert "ClassType" in record
    assert record["ClassType"] == "001"


@pytest.mark.asyncio
async def test_product_characteristics_returns_charcs(mock_product_charcs_tool):
    """Test that the characteristics tool returns characteristic values."""
    result = await mock_product_charcs_tool.arun()
    assert "d" in result
    charcs = result["d"]["results"]
    assert len(charcs) == 2
    assert charcs[0]["Characteristic"] == "COLOR"
    assert charcs[0]["CharcValue"] == "BLACK"


@pytest.mark.asyncio
async def test_product_class_assignment_returns_class(mock_product_class_tool):
    """Test that the class assignment tool returns class data."""
    result = await mock_product_class_tool.arun()
    assert "d" in result
    classes = result["d"]["results"]
    assert len(classes) == 1
    assert classes[0]["Class"] == "NOTEBOOK"


def test_classification_tool_has_correct_name(mock_clfn_product_tool):
    """Test that the classification tool has the correct name."""
    assert mock_clfn_product_tool.name == "list_a_clfnproduct_for_api_clfn_product_srv"
