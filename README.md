# RustChain MCP Server

A Model Context Protocol (MCP) server that connects AI agents to RustChain blockchain operations.

## Features

| Tool | Description |
|------|-------------|
| `rustchain_health` | Check node health |
| `rustchain_balance` | Query wallet balance |
| `rustchain_miners` | List active miners |
| `rustchain_epoch` | Current epoch info |
| `rustchain_bounties` | List open bounties |

## Installation

### Quick Start

```bash
pip install rustchain-mcp
```

### Claude Code Configuration

Add to your `~/.claude/settings.json` or project `.mcp.json`:

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "uvx",
      "args": ["rustchain-mcp"]
    }
  }
}
```

Or with custom node URL:

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "uvx",
      "args": ["rustchain-mcp", "--node-url", "https://your-node.example.com"]
    }
  }
}
```

## Configuration

| Env Variable | Default | Description |
|--------------|---------|-------------|
| `RUSTCHAIN_NODE_URL` | `https://50.28.86.131` | RustChain node URL |
| `RUSTCHAIN_WALLET` | - | Default wallet ID for operations |
| `RUSTCHAIN_TIMEOUT` | `30` | Request timeout in seconds |

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run locally
python -m rustchain_mcp

# Run tests
pytest tests/
```

## Publishing

```bash
# PyPI
python -m build
twine upload dist/*

# npm (if using TypeScript port)
npm publish
```

## License

MIT
