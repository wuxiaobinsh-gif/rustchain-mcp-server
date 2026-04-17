"""Tests for RustChain MCP Server."""

import pytest
from rustchain_mcp import RustChainMCP


class TestRustChainMCP:
    """Test cases for the MCP server."""

    def test_init(self):
        """Test server initialization."""
        server = RustChainMCP()
        assert server.node_url == "https://50.28.86.131"
        assert len(server.tools) > 0

    def test_tools_list(self):
        """Test that all expected tools are registered."""
        server = RustChainMCP()
        expected_tools = [
            "rustchain_health",
            "rustchain_balance",
            "rustchain_miners",
            "rustchain_epoch",
            "rustchain_explorer",
            "rustchain_bounties",
        ]
        for tool in expected_tools:
            assert tool in server.tools

    def test_handle_initialize(self):
        """Test initialize request."""
        server = RustChainMCP()
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        response = server.handle_request(request)
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "serverInfo" in response["result"]

    def test_handle_tools_list(self):
        """Test tools/list request."""
        server = RustChainMCP()
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        response = server.handle_request(request)
        assert response["jsonrpc"] == "2.0"
        assert len(response["result"]["tools"]) == len(server.tools)

    def test_handle_unknown_method(self):
        """Test unknown method handling."""
        server = RustChainMCP()
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "unknown/method",
            "params": {}
        }
        response = server.handle_request(request)
        assert response["error"]["code"] == -32601

    def test_call_tool_unknown(self):
        """Test calling unknown tool."""
        server = RustChainMCP()
        result = server.call_tool("unknown_tool", {})
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
