#!/usr/bin/env python3
"""
RustChain MCP Server
A Model Context Protocol server for RustChain blockchain operations.
Uses JSON-RPC over stdio for communication.
"""

import sys
import json
import logging
from typing import Any, Optional

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_NODE_URL = "https://50.28.86.131"
DEFAULT_TIMEOUT = 30


class RustChainMCP:
    """MCP Server implementation for RustChain."""

    def __init__(self, node_url: str = DEFAULT_NODE_URL, timeout: int = DEFAULT_TIMEOUT):
        self.node_url = node_url
        self.timeout = timeout
        self.tools = {
            "rustchain_health": {
                "description": "Check RustChain node health status, version, and uptime",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "description": "No parameters required"
                }
            },
            "rustchain_balance": {
                "description": "Query RTC wallet balance for a given wallet ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "wallet_id": {
                            "type": "string",
                            "description": "The RustChain wallet/miner ID (e.g., 'Ivan-houzhiwen')"
                        }
                    },
                    "required": ["wallet_id"]
                }
            },
            "rustchain_miners": {
                "description": "List all active miners on the RustChain network",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "description": "No parameters required"
                }
            },
            "rustchain_epoch": {
                "description": "Get current epoch number, slot, and block height",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "description": "No parameters required"
                }
            },
            "rustchain_explorer": {
                "description": "Get block explorer statistics",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "description": "No parameters required"
                }
            },
            "rustchain_bounties": {
                "description": "List open bounties from the RustChain bounty board",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "Filter by label (e.g., 'easy', 'security')"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Max results (default: 20)"
                        }
                    }
                }
            }
        }

    def make_request(self, path: str) -> dict[str, Any]:
        """Make a request to the RustChain node."""
        url = f"{self.node_url}{path}"
        try:
            response = requests.get(url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a RustChain tool."""
        if name == "rustchain_health":
            return self.make_request("/health")

        elif name == "rustchain_balance":
            wallet_id = arguments.get("wallet_id")
            if not wallet_id:
                return {"error": "wallet_id is required"}
            return self.make_request(f"/wallet/balance?miner_id={wallet_id}")

        elif name == "rustchain_miners":
            return self.make_request("/api/miners")

        elif name == "rustchain_epoch":
            return self.make_request("/epoch")

        elif name == "rustchain_explorer":
            return self.make_request("/explorer")

        elif name == "rustchain_bounties":
            # Returns info about how to fetch bounties
            return {
                "message": "Use GitHub CLI to fetch bounties:",
                "command": "gh issue list --repo Scottcjn/rustchain-bounties --label bounty --state open",
                "github_api": "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues"
            }

        else:
            return {"error": f"Unknown tool: {name}"}

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle an MCP JSON-RPC request."""
        method = request.get("method", "")
        request_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "rustchain-mcp",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "tools/list":
            tools = []
            for name, spec in self.tools.items():
                tools.append({
                    "name": name,
                    "description": spec["description"],
                    "inputSchema": spec["inputSchema"]
                })
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools}
            }

        elif method == "tools/call":
            name = request.get("params", {}).get("name")
            arguments = request.get("params", {}).get("arguments", {})
            result = self.call_tool(name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }

        elif method == "notifications/initialized":
            # Client ready signal - no response needed
            return None

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }


def main():
    """Main entry point - read JSON-RPC from stdin, write to stdout."""
    import os
    import signal

    # Ignore broken pipe
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    node_url = os.environ.get("RUSTCHAIN_NODE_URL", DEFAULT_NODE_URL)
    timeout = int(os.environ.get("RUSTCHAIN_TIMEOUT", str(DEFAULT_TIMEOUT)))

    server = RustChainMCP(node_url=node_url, timeout=timeout)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = server.handle_request(request)
            if response is not None:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            print(json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"}
            }), flush=True)


if __name__ == "__main__":
    main()
