#!/bin/bash
# Landscape MCP HTTP Server Deployment Script

set -e

echo "🚀 Landscape MCP HTTP Server Deployment"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Please do not run this script as root."
    echo "   Run it as a regular user, it will prompt for sudo when needed."
    exit 1
fi

# Configuration
INSTALL_DIR="${INSTALL_DIR:-/opt/landscape-mcp}"
SERVICE_USER="${SERVICE_USER:-landscape}"
HTTP_PORT="${HTTP_PORT:-8000}"

echo "Configuration:"
echo "  Install directory: $INSTALL_DIR"
echo "  Service user: $SERVICE_USER"
echo "  HTTP port: $HTTP_PORT"
echo ""

# Ask for confirmation
read -p "Continue with installation? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Create service user if it doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Creating service user: $SERVICE_USER"
    sudo useradd -r -s /bin/bash -d "$INSTALL_DIR" -m "$SERVICE_USER"
fi

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"

# Copy files
echo "Copying files..."
sudo cp -r . "$INSTALL_DIR/"
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Install UV if not present
if ! command -v uv &> /dev/null; then
    echo "Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install dependencies
echo "Installing dependencies..."
cd "$INSTALL_DIR"
sudo -u "$SERVICE_USER" bash -c "cd $INSTALL_DIR && uv venv && source .venv/bin/activate && uv pip install -r requirements-http.txt"

# Get API credentials
echo ""
echo "Please enter your Landscape API credentials:"
read -p "Landscape API URI (e.g., https://landscape.example.com/api/): " API_URI
read -p "API Key: " API_KEY
read -sp "API Secret: " API_SECRET
echo ""

# Create systemd service file
echo "Creating systemd service..."
sudo tee /etc/systemd/system/landscape-mcp.service > /dev/null <<EOF
[Unit]
Description=Landscape MCP HTTP Server
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment="LANDSCAPE_API_URI=$API_URI"
Environment="LANDSCAPE_API_KEY=$API_KEY"
Environment="LANDSCAPE_API_SECRET=$API_SECRET"
Environment="MCP_HTTP_HOST=0.0.0.0"
Environment="MCP_HTTP_PORT=$HTTP_PORT"
ExecStart=$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/mcp_http.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable and start service
echo "Enabling and starting service..."
sudo systemctl enable landscape-mcp
sudo systemctl start landscape-mcp

# Check status
echo ""
echo "✅ Installation complete!"
echo ""
echo "Service status:"
sudo systemctl status landscape-mcp --no-pager
echo ""
echo "📡 Server endpoints:"
echo "  SSE: http://$(hostname -I | awk '{print $1}'):$HTTP_PORT/sse"
echo "  Health: http://$(hostname -I | awk '{print $1}'):$HTTP_PORT/health"
echo ""
echo "📝 Useful commands:"
echo "  sudo systemctl status landscape-mcp    # Check status"
echo "  sudo systemctl restart landscape-mcp   # Restart service"
echo "  sudo journalctl -u landscape-mcp -f    # View logs"
echo ""
echo "🔧 Add to Claude Code settings.json:"
echo '{
  "mcpServers": {
    "landscape-http": {
      "url": "http://YOUR_SERVER_IP:'$HTTP_PORT'/sse",
      "transport": "sse"
    }
  }
}'
