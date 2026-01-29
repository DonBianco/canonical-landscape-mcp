"""
Unit tests for Landscape MCP Server tools.

Tests all 6 tools:
- landscape_query_computers
- landscape_query_packages
- landscape_query_alerts
- landscape_query_offline
- landscape_fast_package_lookup
- landscape_query_activities
"""

import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock


class TestToolListing:
    """Tests for tool listing functionality."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_all_tools(self):
        """Test that all 6 tools are listed."""
        from landscape_mcp import list_tools

        tools = await list_tools()

        assert len(tools) == 6, "Should have 6 tools"
        tool_names = [tool.name for tool in tools]

        expected_tools = [
            "landscape_query_computers",
            "landscape_query_packages",
            "landscape_query_alerts",
            "landscape_query_offline",
            "landscape_fast_package_lookup",
            "landscape_query_activities"
        ]

        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Missing tool: {tool_name}"

    @pytest.mark.asyncio
    async def test_tool_has_description(self):
        """Test that each tool has a description."""
        from landscape_mcp import list_tools

        tools = await list_tools()

        for tool in tools:
            assert tool.description, f"Tool {tool.name} has no description"
            assert len(tool.description) > 10, f"Tool {tool.name} has short description"

    @pytest.mark.asyncio
    async def test_tool_has_input_schema(self):
        """Test that each tool has an input schema."""
        from landscape_mcp import list_tools

        tools = await list_tools()

        for tool in tools:
            assert tool.inputSchema, f"Tool {tool.name} has no input schema"
            assert "type" in tool.inputSchema, f"Tool {tool.name} schema missing 'type'"


class TestToolExecution:
    """Tests for tool execution."""

    @pytest.mark.asyncio
    async def test_query_computers_execution(self, mock_api_client):
        """Test query_computers tool execution."""
        from landscape_mcp import call_tool

        with patch('landscape_mcp.api_client', mock_api_client):
            result = await call_tool(
                "landscape_query_computers",
                {"query": "tag:production", "limit": 25}
            )

            assert len(result) > 0, "Should return result"
            assert result[0].type == "text", "Result should be text type"

            # Verify API was called correctly
            mock_api_client.get_computers.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_alerts_execution(self, mock_api_client):
        """Test query_alerts tool execution."""
        from landscape_mcp import call_tool

        with patch('landscape_mcp.api_client', mock_api_client):
            result = await call_tool("landscape_query_alerts", {})

            assert len(result) > 0, "Should return result"
            assert result[0].type == "text", "Result should be text type"

            # Verify API was called
            mock_api_client.get_alerts.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_offline_execution(self, mock_api_client):
        """Test query_offline tool execution."""
        from landscape_mcp import call_tool

        with patch('landscape_mcp.api_client', mock_api_client):
            result = await call_tool(
                "landscape_query_offline",
                {"since_minutes": 60, "limit": 25}
            )

            assert len(result) > 0, "Should return result"
            assert result[0].type == "text", "Result should be text type"

    @pytest.mark.asyncio
    async def test_query_packages_with_required_argument(self, mock_api_client):
        """Test query_packages tool requires search parameter."""
        from landscape_mcp import call_tool

        with patch('landscape_mcp.api_client', mock_api_client):
            result = await call_tool(
                "landscape_query_packages",
                {"search": "openssl", "limit": 50}
            )

            assert len(result) > 0, "Should return result"
            assert result[0].type == "text", "Result should be text type"

    @pytest.mark.asyncio
    async def test_fast_package_lookup(self, mock_api_client):
        """Test fast_package_lookup tool."""
        from landscape_mcp import call_tool

        with patch('landscape_mcp.api_client', mock_api_client):
            result = await call_tool(
                "landscape_fast_package_lookup",
                {"hostname": "prod-web-01", "package": "openssl"}
            )

            assert len(result) > 0, "Should return result"
            assert result[0].type == "text", "Result should be text type"

    @pytest.mark.asyncio
    async def test_query_activities_with_hostname(self, mock_api_client):
        """Test query_activities with hostname filter."""
        from landscape_mcp import call_tool

        with patch('landscape_mcp.api_client', mock_api_client):
            result = await call_tool(
                "landscape_query_activities",
                {"hostname": "prod-web-01", "limit": 10}
            )

            assert len(result) > 0, "Should return result"
            assert result[0].type == "text", "Result should be text type"

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(self):
        """Test that calling unknown tool returns error."""
        from landscape_mcp import call_tool

        result = await call_tool("unknown_tool", {})

        assert len(result) > 0, "Should return result"
        assert "Unknown tool" in result[0].text, "Should indicate unknown tool"


class TestToolErrorHandling:
    """Tests for error handling in tools."""

    @pytest.mark.asyncio
    async def test_api_error_is_handled(self, mock_api_client_error):
        """Test that API errors are handled gracefully."""
        from landscape_mcp import call_tool

        with patch('landscape_mcp.api_client', mock_api_client_error):
            result = await call_tool("landscape_query_computers", {"query": "", "limit": 25})

            assert len(result) > 0, "Should return result"
            assert "Error" in result[0].text, "Should indicate error occurred"

    @pytest.mark.asyncio
    async def test_missing_required_parameter(self):
        """Test tool with missing required parameter."""
        from landscape_mcp import call_tool

        result = await call_tool(
            "landscape_fast_package_lookup",
            {"hostname": "prod-web-01"}  # Missing 'package' parameter
        )

        assert "Error" in result[0].text, "Should indicate missing parameter"


class TestToolDataFormatting:
    """Tests for data formatting in tool results."""

    @pytest.mark.asyncio
    async def test_query_result_is_valid_json(self, mock_api_client):
        """Test that tool results are valid JSON."""
        from landscape_mcp import call_tool

        with patch('landscape_mcp.api_client', mock_api_client):
            result = await call_tool("landscape_query_computers", {"query": "", "limit": 25})

            # Extract text from result
            text = result[0].text

            # Try to parse as JSON
            try:
                parsed = json.loads(text)
                assert parsed is not None, "Result should be valid JSON"
            except json.JSONDecodeError:
                pytest.fail("Result should be valid JSON")
