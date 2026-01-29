#!/bin/bash
# Test MCP server startup (without actual API connection)

set -e

echo "Testing Landscape MCP Server Startup..."
echo ""

# Set test credentials
export LANDSCAPE_API_URI="https://landscape.example.com/api/"
export LANDSCAPE_API_KEY="test-key-for-testing"
export LANDSCAPE_API_SECRET="test-secret-for-testing"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
    uv pip install -r requirements.txt
fi

echo "✓ Virtual environment ready"
echo ""

# Test 1: Check Python imports
echo "Test 1: Checking Python imports..."
if .venv/bin/python -c "
import sys
try:
    import mcp
    import landscape_api
    print('✓ All imports successful')
    sys.exit(0)
except ImportError as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)
" 2>&1; then
    echo "✓ Import test passed"
else
    echo "✗ Import test failed"
    exit 1
fi

echo ""

# Test 2: Check server initialization (syntax check)
echo "Test 2: Checking server initialization..."
if .venv/bin/python -c "
import sys
import os

# Set test environment variables
os.environ['LANDSCAPE_API_URI'] = 'https://landscape.example.com/api/'
os.environ['LANDSCAPE_API_KEY'] = 'test'
os.environ['LANDSCAPE_API_SECRET'] = 'test'

try:
    # Import the module (this will execute top-level code)
    import landscape_mcp
    print('✓ Server module loaded successfully')

    # Check if main function exists
    if hasattr(landscape_mcp, 'main'):
        print('✓ Main function exists')
    else:
        print('✗ Main function not found')
        sys.exit(1)

    sys.exit(0)
except Exception as e:
    print(f'✗ Server initialization failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" 2>&1; then
    echo "✓ Server initialization test passed"
else
    echo "✗ Server initialization test failed"
    exit 1
fi

echo ""

# Test 3: Check HTTP server module
echo "Test 3: Checking HTTP server module..."
if .venv/bin/python -c "
import sys
import os

os.environ['LANDSCAPE_API_URI'] = 'https://landscape.example.com/api/'
os.environ['LANDSCAPE_API_KEY'] = 'test'
os.environ['LANDSCAPE_API_SECRET'] = 'test'

try:
    import mcp_http
    print('✓ HTTP server module loaded successfully')

    if hasattr(mcp_http, 'main'):
        print('✓ Main function exists')
    else:
        print('✗ Main function not found')
        sys.exit(1)

    sys.exit(0)
except Exception as e:
    print(f'✗ HTTP server initialization failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" 2>&1; then
    echo "✓ HTTP server module test passed"
else
    echo "✗ HTTP server module test failed"
    exit 1
fi

echo ""
echo "========================================="
echo "✓ ALL MCP SERVER TESTS PASSED!"
echo "========================================="
echo ""
echo "The MCP server is ready to use."
echo ""
echo "To start the server:"
echo "  1. Configure your Landscape API credentials"
echo "  2. Run: python landscape_mcp.py (for stdio)"
echo "  3. Or: python mcp_http.py (for HTTP server)"
echo ""
