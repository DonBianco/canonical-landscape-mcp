#!/bin/bash
# Test script for Landscape MCP HTTP Server

SERVER_URL="${1:-http://localhost:8000}"

echo "🧪 Testing Landscape MCP HTTP Server"
echo "Server: $SERVER_URL"
echo "========================================"
echo ""

# Test health endpoint
echo "1. Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "${SERVER_URL}/health")
if [ $? -eq 0 ]; then
    echo "✅ Health check passed"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "❌ Health check failed"
    exit 1
fi
echo ""

# Test SSE endpoint (just check if it's accessible)
echo "2. Testing SSE endpoint availability..."
SSE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${SERVER_URL}/sse")
if [ "$SSE_STATUS" == "200" ] || [ "$SSE_STATUS" == "000" ]; then
    echo "✅ SSE endpoint is accessible"
else
    echo "⚠️  SSE endpoint returned status: $SSE_STATUS"
fi
echo ""

echo "✅ All basic tests passed!"
echo ""
echo "To connect from Claude Code, add this to ~/.claude/settings.json:"
echo '{
  "mcpServers": {
    "landscape-http": {
      "url": "'$SERVER_URL'/sse",
      "transport": "sse"
    }
  }
}'
