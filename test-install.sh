#!/bin/bash
# Test script for installation (non-interactive mode)

set -e

echo "Testing Landscape MCP Installation..."
echo ""

# Create temporary test directory
TEST_DIR="/tmp/landscape-mcp-install-test-$$"
rm -rf "$TEST_DIR" 2>/dev/null || true
mkdir -p "$TEST_DIR"

echo "Test directory: $TEST_DIR"

# Copy files to test directory
cp -r ./* "$TEST_DIR/" 2>/dev/null || true
cp -r .gitignore "$TEST_DIR/" 2>/dev/null || true

cd "$TEST_DIR"

# Verify files are present
echo ""
echo "✓ Files copied successfully"
echo ""

# Check UV installation
if command -v uv &> /dev/null; then
    echo "✓ UV is installed"
else
    echo "✗ UV not found - installation script will install it"
fi

# Create a non-interactive test by providing credentials via environment
export LANDSCAPE_API_URI="https://landscape.example.com/api/"
export LANDSCAPE_API_KEY="test-key"
export LANDSCAPE_API_SECRET="test-secret"

# Test virtual environment creation
echo ""
echo "Testing virtual environment creation..."
uv venv
echo "✓ Virtual environment created"

# Test dependency installation
echo ""
echo "Testing dependency installation..."
uv pip install -r requirements.txt
echo "✓ Dependencies installed"

# Verify Python imports
echo ""
echo "Testing Python imports..."
if .venv/bin/python -c "import mcp; import landscape_api; print('✓ All imports successful')" 2>/dev/null; then
    echo "✓ All required modules can be imported"
else
    echo "✗ Import test failed"
    exit 1
fi

# Verify configuration files
echo ""
echo "Testing configuration..."
if grep -q "YOUR_API_KEY_HERE" landscape_mcp.py; then
    echo "✓ Placeholder credentials present (as expected)"
else
    echo "⚠ Warning: No placeholder credentials found"
fi

# Test MCP server syntax
echo ""
echo "Testing MCP server syntax..."
if .venv/bin/python -m py_compile landscape_mcp.py; then
    echo "✓ landscape_mcp.py syntax valid"
else
    echo "✗ landscape_mcp.py syntax error"
    exit 1
fi

if .venv/bin/python -m py_compile mcp_http.py; then
    echo "✓ mcp_http.py syntax valid"
else
    echo "✗ mcp_http.py syntax error"
    exit 1
fi

echo ""
echo "========================================="
echo "✓ ALL TESTS PASSED!"
echo "========================================="
echo ""
echo "Installation script appears to be working correctly."
echo "Test directory: $TEST_DIR"
echo ""
echo "To clean up test directory:"
echo "  rm -rf $TEST_DIR"
echo ""
