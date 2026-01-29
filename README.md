# 🖥️ Landscape MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.24.0-green.svg)](https://modelcontextprotocol.io/)
[![MCP Badge](https://lobehub.com/badge/mcp/donbianco-canonical-landscape-mcp)](https://lobehub.com/mcp/donbianco-canonical-landscape-mcp)
[![MCP 1.24.0](https://img.shields.io/badge/MCP-1.24.0-green.svg)](https://modelcontextprotocol.io/)
[![CI](https://github.com/DonBianco/canonical-landscape-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/DonBianco/canonical-landscape-mcp/actions/workflows/test.yml)
[![Tools: 6](https://img.shields.io/badge/Tools-6-blue.svg)]()
[![Prompts: 5](https://img.shields.io/badge/Prompts-5-purple.svg)]()
[![Resources: 8](https://img.shields.io/badge/Resources-8-orange.svg)]()

> **AI-powered Landscape  infrastructure management for system administrators**

## Overview

**Landscape MCP Server** is a lightweight tool that brings AI-powered infrastructure management to your fingertips. Built by a system administrator to simplify daily operations, this MCP (Model Context Protocol) server connects your Canonical Landscape infrastructure with Claude AI, enabling you to manage and query your Ubuntu/Debian fleet using natural language.

### Why This Tool?

As a system administrator managing hundreds of machines, manually navigating the Landscape web interface for every query became time-consuming. This tool was created to solve that problem by allowing AI to:

- **Query your infrastructure** using natural language instead of clicking through menus
- **Get instant answers** about machine status, packages, and alerts
- **Save time** on repetitive tasks like checking if packages are installed
- **Monitor activities** and audit logs without manual searching
- **Troubleshoot issues** with AI-assisted insights

### Real-World Example

Instead of logging into Landscape, navigating to computers, filtering by tags, and checking each machine manually, you can now simply ask Claude:

- "Show me all production servers that need a reboot"
- "Is nginx installed on web-server-01?"
- "Which machines haven't checked in for the last 2 hours?"
- "What alerts do we currently have?"

Claude will use this MCP server to query your Landscape infrastructure and provide instant answers.

### Key Features

- 🖥️ **Computer Queries** - Search by tags, hostnames, distribution, and status
- 📦 **Package Management** - Find installed packages across your fleet instantly
- 📊 **Activity Monitoring** - Track audit logs and system activities
- 🚨 **Alert Management** - Get notified about system issues
- ⚡ **Fast Lookups** - Check package installations on specific machines
- 🌐 **HTTP Server** - Deploy on a VM for remote access
- 📈 **Streamlit Dashboard** - Visualize your infrastructure

<<<<<<< HEAD
=======
### MCP Capabilities

This MCP server provides three types of capabilities for comprehensive infrastructure management:

#### 🔧 Tools (6 Total)
Execute actions and queries on your infrastructure:
- `landscape_query_computers` - Search computers by tag, hostname, or status
- `landscape_query_packages` - Find packages across your fleet
- `landscape_query_alerts` - Get current system alerts
- `landscape_query_offline` - List offline or not-pinging systems
- `landscape_fast_package_lookup` - Check package on specific machine
- `landscape_query_activities` - Access audit logs and activity history

#### 💡 Prompts (5 Guided Workflows)
Get AI-assisted analysis for common infrastructure tasks:
- **system_health_check** - Comprehensive infrastructure health analysis with recommendations
- **package_audit** - Security update and compliance audit across your fleet
- **incident_investigation** - Post-mortem analysis using activity logs
- **capacity_planning** - Analyze capacity and forecast growth trends
- **compliance_report** - Generate compliance status for audits

#### 📚 Resources (8 Data Sources)
Access real-time infrastructure data without executing actions:
- `landscape://infrastructure/summary` - Real-time infrastructure overview
- `landscape://alerts/active` - Current system alerts
- `landscape://computers/online` - All currently online systems
- `landscape://computers/offline` - All offline systems
- `landscape://activities/recent` - Recent system activities
- `landscape://packages/security-updates` - Available security updates
- `landscape://computers/{tag}` - Filter computers by infrastructure tag
- `landscape://activities/{hostname}` - Activity history for specific machine

>>>>>>> b8a758e (Update install.sh added resources prompts etc)
---

## 🎯 What is MCP?

**Model Context Protocol (MCP)** is an open protocol created by Anthropic that standardizes how applications provide context to Large Language Models (LLMs). This MCP server exposes your Landscape infrastructure data to Claude Code and other MCP-compatible clients, enabling AI-powered infrastructure management.

When you use Claude Code with this MCP server, Claude can:
- Query your infrastructure in natural language
- Provide insights about your systems
- Help troubleshoot issues
- Generate reports and summaries
- Answer questions about your fleet

---

## 🚀 Quick Start

### Automated Installation (Recommended)

The easiest way to install is using the automated installation script:

```bash
# Clone the repository
git clone https://github.com/yourusername/landscape-mcp.git
cd landscape-mcp

# Run the installation script
./install.sh
```

The script will:
1. Install UV package manager (if not already installed)
2. Create a Python virtual environment
3. Install all dependencies
4. Configure your Landscape API credentials
5. Set up Claude Code MCP server configuration
6. Test the installation

**That's it!** Restart Claude Code and start using the MCP server.

---

### Manual Installation

If you prefer to install manually:

#### Step 1: Get API Credentials

1. Log into your Landscape web interface
2. Click your username (top right corner)
3. Navigate to API access/credentials section
4. Generate access key and secret key

#### Step 2: Install Using UV

[UV](https://docs.astral.sh/uv/) is a fast Python package installer and resolver:

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone or navigate to the project directory
cd landscape-mcp

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Linux/Mac
# Or on Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

#### Step 3: Configure API Credentials

Edit `landscape_mcp.py` and update these lines with your credentials:

```python
API_URI = os.getenv("LANDSCAPE_API_URI", "https://landscape.example.com/api/")
API_KEY = os.getenv("LANDSCAPE_API_KEY", "YOUR_API_KEY_HERE")
API_SECRET = os.getenv("LANDSCAPE_API_SECRET", "YOUR_API_SECRET_HERE")
```

Or set environment variables:
```bash
export LANDSCAPE_API_URI="https://landscape.example.com/api/"
export LANDSCAPE_API_KEY="your-key"
export LANDSCAPE_API_SECRET="your-secret"
```

#### Step 4: Add to Claude Code

Edit `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "landscape": {
      "command": "/full/path/to/landscape-mcp/.venv/bin/python",
      "args": ["/full/path/to/landscape-mcp/landscape_mcp.py"],
      "disabled": false
    }
  }
}
```

#### Step 5: Verify Installation

```bash
# Restart Claude Code, then check:
claude mcp list
# Should show: landscape: ... ✓ Connected
```

---

## 💡 Usage Examples

Once the MCP server is configured in Claude Code, you can ask Claude questions like:

- "Show me all computers on Landscape"
- "Which machines need a reboot?"
- "Is nginx installed on my-server-01?"
- "Show me recent activities for computer my-laptop"
- "List all offline computers from the last hour"
- "What alerts do we have?"
- "Find all computers with tag:production"

Claude will use the appropriate MCP tools to query your Landscape infrastructure and provide answers.

---

## 📊 Available Tools

The MCP server provides these tools to Claude Code:

- **landscape_query_computers** — Query computers by tags, hostname, or status
- **landscape_query_packages** — Search for installed packages
- **landscape_query_activities** — Get audit logs and activity history
- **landscape_query_alerts** — Retrieve system alerts
- **landscape_query_offline** — Find computers that haven't checked in
- **landscape_fast_package_lookup** — Check if a specific package is installed on a machine

---

## 🔍 Query Syntax Reference

| Syntax | Example | Description |
|--------|---------|-------------|
| `tag:` | `tag:production` | Computers with specific tag |
| `hostname:` | `hostname:my-laptop` | Specific computer hostname |
| `distribution:` | `distribution:24.04` | Ubuntu/Debian version |
| `access-group:` | `access-group:global` | Access group filtering |
| `needs:reboot:` | `needs:reboot:true` | Machines needing reboot |
| Multiple tags | `tag:prod tag:secure` | AND logic (space-separated) |

---

## 🌐 HTTP Server (Deployable on VM)

The project includes an HTTP version (`mcp_http.py`) that can be deployed on a VM and accessed remotely via HTTP/SSE.

### Quick Start (HTTP Version)

```bash
# 1. Install dependencies
uv pip install -r requirements-http.txt

# 2. Run the server
python mcp_http.py

# 3. Test it
./test-http.sh http://localhost:8000
```

### Installing HTTP Server

```bash
# Install HTTP server dependencies
uv pip install -r requirements-http.txt

# Or install individually
uv pip install starlette "uvicorn[standard]" sse-starlette
```

### Running HTTP Server

```bash
# Run on localhost (development)
python mcp_http.py

# Or with custom host/port
MCP_HTTP_HOST=0.0.0.0 MCP_HTTP_PORT=8000 python mcp_http.py
```

Server endpoints:
- **SSE:** `http://your-server:8000/sse`
- **Messages:** `http://your-server:8000/messages` (POST)
- **Health:** `http://your-server:8000/health`

### Automated Deployment (Recommended)

Use the provided deployment script for easy setup:

```bash
# Transfer files to your VM
scp -r . user@your-vm:/tmp/landscape-mcp

# SSH to the VM
ssh user@your-vm

# Run deployment script
cd /tmp/landscape-mcp
./deploy-http.sh
```

The script will:
- Create service user and installation directory
- Install dependencies with UV
- Configure systemd service
- Start and enable the service

### Manual Deployment with Systemd

Create `/etc/systemd/system/landscape-mcp.service`:

```ini
[Unit]
Description=Landscape MCP HTTP Server
After=network.target

[Service]
Type=simple
User=landscape
WorkingDirectory=/opt/landscape-mcp
Environment="LANDSCAPE_API_URI=https://landscape.example.com/api/"
Environment="LANDSCAPE_API_KEY=your-key"
Environment="LANDSCAPE_API_SECRET=your-secret"
Environment="MCP_HTTP_HOST=0.0.0.0"
Environment="MCP_HTTP_PORT=8000"
ExecStart=/opt/landscape-mcp/.venv/bin/python /opt/landscape-mcp/mcp_http.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable landscape-mcp
sudo systemctl start landscape-mcp
sudo systemctl status landscape-mcp

# View logs
sudo journalctl -u landscape-mcp -f
```

### Connecting Claude Code to HTTP Server

Edit `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "landscape-http": {
      "url": "http://your-vm-ip:8000/sse",
      "transport": "sse"
    }
  }
}
```

---

## 📈 Streamlit Dashboard

The project includes a web-based dashboard for visualizing your infrastructure.

### Running the Dashboard

```bash
# Make sure you're in the virtual environment
source .venv/bin/activate

# Run the dashboard
streamlit run landscape_machines_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501` and provides:
- Real-time infrastructure overview
- Computer inventory with filters
- Distribution and tag analytics
- Annotation management
- Interactive visualizations

---

## 📋 Project Structure

```
landscape-mcp/
├── landscape_mcp.py                    # Main MCP server (stdio)
├── mcp_http.py                        # HTTP MCP server (deployable)
├── landscape_machines_dashboard.py     # Streamlit dashboard
├── install.sh                         # Automated installation script
├── requirements.txt                    # Core dependencies
├── requirements-http.txt              # HTTP server dependencies
├── setup.py                           # Python package setup
├── pyproject.toml                     # Python project config
├── README.md                          # This documentation
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # MIT License
└── .gitignore                         # Git ignore rules
```

### Core Dependencies

```
mcp==1.24.0                # MCP Server Framework
landscape-api-py3==0.9.0   # Landscape API wrapper
requests==2.32.5           # HTTP client
```

### Optional Dashboard Dependencies

```
streamlit                  # Web dashboard framework
pandas                     # Data manipulation
plotly                     # Interactive visualizations
```

---

## ⚙️ Configuration

The MCP server reads credentials from environment variables. You can configure them in multiple ways:

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LANDSCAPE_API_URI` | Your Landscape API endpoint | `https://landscape.example.com/api/` |
| `LANDSCAPE_API_KEY` | Your API access key | `your-access-key-here` |
| `LANDSCAPE_API_SECRET` | Your API secret key | `your-secret-key-here` |

### Setting Environment Variables

**Linux/macOS:**
```bash
export LANDSCAPE_API_URI="https://landscape.example.com/api/"
export LANDSCAPE_API_KEY="your-key"
export LANDSCAPE_API_SECRET="your-secret"
```

**Windows:**
```cmd
set LANDSCAPE_API_URI=https://landscape.example.com/api/
set LANDSCAPE_API_KEY=your-key
set LANDSCAPE_API_SECRET=your-secret
```

**Permanent (add to `~/.bashrc` or `~/.zshrc`):**
```bash
echo 'export LANDSCAPE_API_URI="https://landscape.example.com/api/"' >> ~/.bashrc
echo 'export LANDSCAPE_API_KEY="your-key"' >> ~/.bashrc
echo 'export LANDSCAPE_API_SECRET="your-secret"' >> ~/.bashrc
source ~/.bashrc
```

Alternatively, you can edit the default values in `landscape_mcp.py` (lines 15-17), but using environment variables is recommended for security.

---

## 🔐 Security

- **HTTPS Only** - All API communication uses HTTPS
- **API Credentials** - Stored in `landscape_mcp.py` or environment variables
- **No Data Persistence** - The MCP server doesn't store any infrastructure data
- **Read-Only Access** - The tools only query data, they don't modify your infrastructure

**Security Best Practices:**
1. Never commit API credentials to version control
2. Use environment variables for production deployments
3. Rotate API keys regularly
4. Restrict API key permissions in Landscape to read-only if possible

---

## 🛠️ Troubleshooting

### MCP Server Not Connecting

```bash
# Check if MCP server is recognized
claude mcp list

# View logs
tail -f ~/.claude/logs/landscape*.log

# Test the server directly
python landscape_mcp.py
```

### API Connection Errors

1. Verify your credentials in `landscape_mcp.py`
2. Ensure the API URI ends with `/api/`
3. Check network connectivity to your Landscape server
4. Verify API keys are valid and not expired

### Dashboard Not Starting

```bash
# Make sure streamlit is installed
uv pip install streamlit pandas plotly

# Run with verbose output
streamlit run landscape_machines_dashboard.py --logger.level=debug
```

### No Results from Queries

- Tag names are case-sensitive
- Check if your API key has appropriate permissions
- Verify the query syntax matches Landscape's query language

---

## 🤝 Contributing

Contributions are welcome! We appreciate:
- Bug reports and feature requests
- Documentation improvements
- Code contributions
- Testing and feedback

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📚 Resources

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) - Learn about MCP
- [Canonical Landscape](https://documentation.ubuntu.com/landscape/) - Official Landscape documentation
- [Claude Code](https://claude.ai/claude-code) - Claude's official CLI tool
- [UV Package Manager](https://docs.astral.sh/uv/) - Fast Python package installer

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## ⚠️ Important Disclaimers

### NOT AN OFFICIAL CANONICAL PRODUCT

This is an **UNOFFICIAL, COMMUNITY-DRIVEN** project:
- **NOT** developed, maintained, or supported by Canonical Ltd.
- **NOT** an official Canonical Landscape tool
- Canonical has **no involvement** in this project whatsoever
- "Canonical", "Landscape", and "Ubuntu" are trademarks of Canonical Ltd.

### COMMUNITY CONTRIBUTION

- Created by a system administrator for internal infrastructure management needs
- Shared publicly for community benefit
- Use at your own risk and discretion
- No warranties or guarantees provided

### NO OFFICIAL SUPPORT

- This project is provided **"AS IS"** without warranty of any kind
- Canonical will **NOT** provide support for this tool
- Issues and questions should be directed to this repository only
- The author/contributors are not liable for any damages or issues

### LIABILITY & LEGAL

**Disclaimer of Liability:**
This software is provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

**Trademark Notice:**
All product names, logos, and brands are property of their respective owners. Use of these names, logos, and brands does not imply endorsement. This project's use of trademarked names is solely for descriptive and identification purposes.

**User Acknowledgment:**
By using this software, users acknowledge that:
1. This is community software, not officially supported by Canonical
2. Use is entirely at the user's own risk
3. The authors make no guarantees about functionality, security, or suitability
4. Users are responsible for ensuring compliance with their organization's policies
5. This software should be tested thoroughly before production use

**For Official Canonical Support:**
For official Canonical Landscape support, documentation, and products, please visit:
- Official Website: https://ubuntu.com/landscape
- Official Support: https://ubuntu.com/support
<<<<<<< HEAD
- Official Documentation: https://documentation.ubuntu.com/landscape/
=======
- Official Documentation: https://ubuntu.com/landscape/docs

