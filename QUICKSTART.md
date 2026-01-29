# Quick Start Guide

Get started with Landscape MCP server in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- Access to a Canonical Landscape server
- Claude Code installed
- Landscape API credentials

## Installation (One Command)

```bash
git clone https://github.com/yourusername/landscape-mcp.git
cd landscape-mcp
./install.sh
```

That's it! The script will:
- Install UV package manager
- Create virtual environment
- Install all dependencies
- Configure your API credentials
- Set up Claude Code

## Get API Credentials

1. Log into Landscape web interface
2. Click your username (top right)
3. Go to "API access"
4. Generate new access key and secret

## Test the Installation

```bash
# Restart Claude Code
# Then check if MCP server is connected:
claude mcp list

# You should see:
# landscape: ... ✓ Connected
```

## Try It Out!

Open Claude Code and ask:

- "Show me all computers on Landscape"
- "Which machines need a reboot?"
- "Is nginx installed on my-server?"
- "List all offline computers"
- "Show me recent activities"

## Alternative: Manual Installation

If you prefer manual setup:

```bash
# 1. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone repository
git clone https://github.com/yourusername/landscape-mcp.git
cd landscape-mcp

# 3. Create venv and install
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 4. Configure credentials
export LANDSCAPE_API_URI="https://landscape.example.com/api/"
export LANDSCAPE_API_KEY="your-key"
export LANDSCAPE_API_SECRET="your-secret"

# 5. Add to Claude Code settings (~/.claude/settings.json)
{
  "mcpServers": {
    "landscape": {
      "command": "/full/path/to/.venv/bin/python",
      "args": ["/full/path/to/landscape_mcp.py"],
      "disabled": false
    }
  }
}

# 6. Restart Claude Code
```

## Optional: Install Dashboard

```bash
source .venv/bin/activate
uv pip install streamlit pandas plotly
streamlit run landscape_machines_dashboard.py
```

## Optional: HTTP Server

For remote deployment:

```bash
# Install dependencies
uv pip install -r requirements-http.txt

# Run server
python mcp_http.py

# Server runs on http://0.0.0.0:8000
```

## Troubleshooting

### MCP server not connecting?

```bash
# Check logs
tail -f ~/.claude/logs/landscape*.log

# Test server directly
python landscape_mcp.py
```

### Import errors?

```bash
# Reinstall dependencies
source .venv/bin/activate
uv pip install -r requirements.txt --force-reinstall
```

### API connection errors?

1. Verify credentials are correct
2. Check API URI ends with `/api/`
3. Test API access: `curl -u "KEY:SECRET" https://your-landscape.com/api/`

## Need Help?

- [Full Documentation](README.md)
- [Contributing Guide](CONTRIBUTING.md)
- [GitHub Issues](https://github.com/yourusername/landscape-mcp/issues)

## What's Next?

- Explore all available [MCP tools](README.md#-available-tools)
- Learn [query syntax](README.md#-query-syntax-reference)
- Try the [HTTP server](README.md#-http-server-deployable-on-vm)
- Check out [usage examples](README.md#-usage-examples)

---

**Enjoy using Landscape MCP!** 🚀
