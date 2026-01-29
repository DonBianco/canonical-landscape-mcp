#!/bin/bash
# ============================================================================
# Landscape MCP Server - Installation Script
# ============================================================================
# This script installs the Landscape MCP server and configures it for
# Claude Code using UV package manager.
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# ============================================================================
# INSTALLATION STEPS
# ============================================================================

print_header "Landscape MCP Server Installation"

# Step 1: Check if UV is installed
print_info "Checking for UV package manager..."
if ! command -v uv &> /dev/null; then
    print_warning "UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Source UV in current shell
    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v uv &> /dev/null; then
        print_error "Failed to install UV. Please install manually: https://docs.astral.sh/uv/"
        exit 1
    fi
    print_success "UV installed successfully"
else
    print_success "UV is already installed"
fi

# Step 2: Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_info "Installation directory: $SCRIPT_DIR"

# Step 3: Create virtual environment
print_info "Creating Python virtual environment..."
if [ -d ".venv" ]; then
    print_warning "Virtual environment already exists. Removing old one..."
    rm -rf .venv
fi

uv venv
print_success "Virtual environment created"

# Step 4: Install dependencies
print_info "Installing dependencies with UV..."
uv pip install -r requirements.txt
print_success "Dependencies installed"

# Step 5: Prompt for Landscape API credentials
print_header "Landscape API Configuration"

echo "Please provide your Landscape API credentials:"
echo "(You can find these in your Landscape web interface under API access)"
echo ""

read -p "Landscape API URI [https://landscape.example.com/api/]: " API_URI
API_URI=${API_URI:-https://landscape.example.com/api/}

read -p "Landscape API Key: " API_KEY
read -p "Landscape API Secret: " API_SECRET

if [ -z "$API_KEY" ] || [ -z "$API_SECRET" ]; then
    print_warning "API credentials not provided. You'll need to set them manually later."
    print_info "Edit landscape_mcp.py or set environment variables:"
    print_info "  - LANDSCAPE_API_URI"
    print_info "  - LANDSCAPE_API_KEY"
    print_info "  - LANDSCAPE_API_SECRET"
else
    # Update the credentials in landscape_mcp.py
    print_info "Updating credentials in landscape_mcp.py..."

    # Use sed to replace the default values
    sed -i.bak "s|API_URI = os.getenv(\"LANDSCAPE_API_URI\", \".*\")|API_URI = os.getenv(\"LANDSCAPE_API_URI\", \"$API_URI\")|" landscape_mcp.py
    sed -i.bak "s|API_KEY = os.getenv(\"LANDSCAPE_API_KEY\", \".*\")|API_KEY = os.getenv(\"LANDSCAPE_API_KEY\", \"$API_KEY\")|" landscape_mcp.py
    sed -i.bak "s|API_SECRET = os.getenv(\"LANDSCAPE_API_SECRET\", \".*\")|API_SECRET = os.getenv(\"LANDSCAPE_API_SECRET\", \"$API_SECRET\")|" landscape_mcp.py

    # Also update mcp_http.py
    sed -i.bak "s|API_URI = os.getenv(\"LANDSCAPE_API_URI\", \".*\")|API_URI = os.getenv(\"LANDSCAPE_API_URI\", \"$API_URI\")|" mcp_http.py
    sed -i.bak "s|API_KEY = os.getenv(\"LANDSCAPE_API_KEY\", \".*\")|API_KEY = os.getenv(\"LANDSCAPE_API_KEY\", \"$API_KEY\")|" mcp_http.py
    sed -i.bak "s|API_SECRET = os.getenv(\"LANDSCAPE_API_SECRET\", \".*\")|API_SECRET = os.getenv(\"LANDSCAPE_API_SECRET\", \"$API_SECRET\")|" mcp_http.py

    # Remove backup files
    rm -f landscape_mcp.py.bak mcp_http.py.bak

    print_success "Credentials configured"
fi

# Step 6: Configure Claude Code
print_header "Claude Code Configuration"

CLAUDE_CONFIG="$HOME/.claude.json"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
MCP_SCRIPT="$SCRIPT_DIR/landscape_mcp.py"

print_info "Configuring MCP server in Claude Code..."

# Check if .claude.json exists
if [ ! -f "$CLAUDE_CONFIG" ]; then
    print_info "Creating new .claude.json..."
    cat > "$CLAUDE_CONFIG" << EOF
{
  "mcpServers": {
    "landscape": {
      "command": "$VENV_PYTHON",
      "args": ["$MCP_SCRIPT"],
      "disabled": false
    }
  }
}
EOF
    print_success "Created $CLAUDE_CONFIG"
else
    print_info "Updating existing .claude.json..."

    # Check if jq is available for JSON manipulation
    if command -v jq &> /dev/null; then
        # Create backup
        cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.bak"

        # Add or update the landscape server in mcpServers
        jq --arg venv_python "$VENV_PYTHON" --arg mcp_script "$MCP_SCRIPT" \
           '.mcpServers.landscape = {
              "command": $venv_python,
              "args": [$mcp_script],
              "disabled": false
            }' "$CLAUDE_CONFIG" > "$CLAUDE_CONFIG.tmp" && mv "$CLAUDE_CONFIG.tmp" "$CLAUDE_CONFIG"

        print_success "Added landscape server to existing configuration"
    else
        # Fallback: manual instructions if jq is not available
        print_warning "jq not found. Please add this configuration manually to $CLAUDE_CONFIG:"
        echo ""
        echo 'Add under "mcpServers": {'
        echo '  "landscape": {'
        echo '    "command": "'$VENV_PYTHON'",'
        echo '    "args": ["'$MCP_SCRIPT'"],'
        echo '    "disabled": false'
        echo '  }'
        echo '}'
        echo ""
        print_info "Or install jq and run this script again: sudo apt install jq"
    fi
fi

# Step 7: Test the installation
print_header "Testing Installation"

print_info "Testing MCP server connection..."

# Test if Python can import the required modules
if .venv/bin/python -c "import mcp; import landscape_api" 2>/dev/null; then
    print_success "Python modules imported successfully"
else
    print_error "Failed to import required modules"
    exit 1
fi

# Step 8: Installation complete
print_header "Installation Complete!"

echo ""
print_success "Landscape MCP Server installed successfully!"
echo ""
print_info "Next steps:"
echo "  1. Restart Claude Code to load the MCP server"
echo "  2. The server configuration has been added to ~/.claude.json"
echo "  3. Look for 'landscape' server in Claude Code MCP servers"
echo ""
print_info "Usage examples in Claude Code:"
echo '  - "Show me all computers on Landscape"'
echo '  - "Which machines need a reboot?"'
echo '  - "Is nginx installed on my-server?"'
echo ""
print_info "Optional: Install dashboard dependencies:"
echo "  uv pip install streamlit pandas plotly"
echo "  streamlit run landscape_machines_dashboard.py"
echo ""
print_info "For HTTP server deployment:"
echo "  uv pip install -r requirements-http.txt"
echo "  python mcp_http.py"
echo ""
print_success "Enjoy using Landscape MCP! 🚀"
