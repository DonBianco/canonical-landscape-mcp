# Testing Guide - Landscape MCP Server

## Overview

This guide covers how to run tests, validate the MCP server, and verify quality improvements.

## Prerequisites

```bash
# Install dependencies
pip install -e ".[test]"

# For development with all tools
pip install -e ".[dev,test]"
```

## Running Tests

### Quick Test Run

```bash
# Run all tests with minimal output
pytest tests/ -v
```

### Full Test Run with Coverage

```bash
# Run tests with coverage report
pytest tests/ -v --cov=landscape_mcp --cov-report=term-missing --cov-report=html

# View HTML coverage report
open htmlcov/index.html  # macOS
firefox htmlcov/index.html  # Linux
```

### Run Specific Test Files

```bash
# Test tools only
pytest tests/test_tools.py -v

# Test prompts only
pytest tests/test_prompts.py -v

# Test resources only
pytest tests/test_resources.py -v
```

### Run Specific Test Classes

```bash
# Test tool listing only
pytest tests/test_tools.py::TestToolListing -v

# Test resource errors
pytest tests/test_resources.py::TestResourceErrorHandling -v
```

### Run with Different Markers

```bash
# Run only integration tests
pytest -m integration -v

# Run only fast tests (exclude slow)
pytest -m "not slow" -v

# Run only async tests
pytest -m asyncio -v
```

## Code Quality Checks

### Linting with Ruff

```bash
# Check code style
ruff check landscape_mcp.py

# Check with verbose output
ruff check . --show-settings

# Fix issues automatically (where possible)
ruff check . --fix
```

### Type Checking with Mypy

```bash
# Check types
mypy landscape_mcp.py

# Check with verbose output
mypy landscape_mcp.py -v

# Show all types
mypy landscape_mcp.py --show-column-numbers --pretty
```

### Security Check with Bandit

```bash
# Check for security issues
bandit -r . -ll

# Only report high/medium severity
bandit -r . -f csv

# Generate JSON report
bandit -r . -f json -o bandit-report.json
```

### Format Check with Black

```bash
# Check formatting
black --check landscape_mcp.py

# Auto-format code
black landscape_mcp.py

# Check with verbose output
black --check --diff landscape_mcp.py
```

## MCP Server Validation

### Module Import Test

```bash
# Verify module imports correctly
python3 -c "from landscape_mcp import app, list_tools, call_tool, list_prompts, get_prompt, list_resources, read_resource; print('✓ All MCP functions imported successfully')"
```

### Syntax Validation

```bash
# Check Python syntax
python3 -m py_compile landscape_mcp.py && echo "✓ Syntax valid"
```

### JSON Validation

```bash
# Validate glama.json
python3 -m json.tool glama.json > /dev/null && echo "✓ glama.json valid"
```

### TOML Validation

```bash
# Validate pyproject.toml
python3 -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))" && echo "✓ pyproject.toml valid"
```

## Continuous Integration

### Run Complete CI Pipeline Locally

```bash
# Run the same checks as GitHub Actions
./run_ci_locally.sh
```

Or manually:

```bash
# 1. Lint
ruff check .

# 2. Type check
mypy landscape_mcp.py --ignore-missing-imports

# 3. Security check
bandit -r . -ll

# 4. Run tests with coverage
pytest tests/ --cov=landscape_mcp --cov-report=xml

# 5. Validate MCP server
python3 -c "from landscape_mcp import app; print('✓ MCP server valid')"
```

## Performance Testing

### Memory Usage

```bash
# Check module memory footprint
python3 -c "
import sys
import landscape_mcp
print(f'Memory usage: {sys.getsizeof(landscape_mcp)} bytes')
"
```

### Import Time

```bash
# Measure import time
python3 -c "
import time
start = time.time()
import landscape_mcp
end = time.time()
print(f'Import time: {(end-start)*1000:.2f}ms')
"
```

## Test Coverage Goals

### Current Coverage
- **Target:** 80%+ code coverage
- **Status:** Configured in CI/CD

### Coverage by Component

```bash
# View coverage by file
pytest tests/ --cov=landscape_mcp --cov-report=term-missing

# Expected output shows:
# landscape_mcp.py  XX%   (functions tested)
```

## Troubleshooting

### Tests Fail with Import Error

```bash
# Reinstall package in development mode
pip install -e ".[test]"

# Or with explicit dependency resolution
pip install --force-reinstall -e ".[test]"
```

### Mock API Not Working

Check `tests/conftest.py`:
```python
# Ensure mock is being patched correctly
with patch('landscape_mcp.api_client', mock_api_client):
    # Test code
```

### Async Tests Failing

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio>=0.23.0

# Run with asyncio marker
pytest tests/test_prompts.py -v -m asyncio
```

### Type Checking Errors

```bash
# Ignore missing type stubs
mypy landscape_mcp.py --ignore-missing-imports

# Or update type stubs
mypy --install-types landscape_mcp.py
```

## Automated Testing

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Lint
ruff check landscape_mcp.py || { echo "Ruff check failed"; exit 1; }

# Type check
mypy landscape_mcp.py --ignore-missing-imports || { echo "Type check failed"; exit 1; }

# Tests
pytest tests/ -q || { echo "Tests failed"; exit 1; }

echo "✓ All checks passed"
```

Then make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### GitHub Actions

The CI/CD pipeline runs automatically on:
- Push to main/develop branches
- Pull requests

View results at: https://github.com/yourusername/landscape-mcp/actions

## Test Data

### Mock Data Location

See `tests/conftest.py` for:
- `MOCK_COMPUTERS` - Sample computer data
- `MOCK_ALERTS` - Sample alert data
- `MOCK_PACKAGES` - Sample package data
- `MOCK_ACTIVITIES` - Sample activity data
- `MOCK_OFFLINE_COMPUTERS` - Sample offline system data

### Adding New Test Data

```python
# In tests/conftest.py, add new constant:
MOCK_CUSTOM_DATA = [
    {"id": "1", "name": "example"},
    # ...
]

# Then use in fixture:
@pytest.fixture
def mock_custom_api():
    client = MagicMock()
    client.get_custom.return_value = MOCK_CUSTOM_DATA
    return client
```

## Test Reporting

### Generate Coverage Report

```bash
# HTML report
pytest tests/ --cov=landscape_mcp --cov-report=html
open htmlcov/index.html

# Terminal report with missing lines
pytest tests/ --cov=landscape_mcp --cov-report=term-missing

# JSON report for CI tools
pytest tests/ --cov=landscape_mcp --cov-report=json
```

### Generate Bandit Report

```bash
# JSON report
bandit -r . -f json -o security-report.json

# CSV report
bandit -r . -f csv -o security-report.csv
```

## Debugging Tests

### Run Single Test with Debugging

```bash
# Run with print statements
pytest tests/test_tools.py::TestToolListing::test_list_tools_returns_all_tools -v -s

# Run with Python debugger
pytest tests/test_tools.py -v --pdb

# Drop into debugger on failure
pytest tests/test_tools.py -v --pdb-on-failure
```

### Verbose Output

```bash
# Show all captured output
pytest tests/ -v -s

# Show debug information
pytest tests/ -v --setup-show
```

## Performance Profiling

### Profile Test Execution

```bash
# Use pytest-benchmark (if installed)
pip install pytest-benchmark

# Run with performance profiling
pytest tests/ -v --benchmark-only
```

### Memory Profiling

```bash
# Use memory_profiler
pip install memory-profiler

# Run with memory profiling
python -m memory_profiler landscape_mcp.py
```

## Continuous Testing

### Watch Mode

```bash
# Run tests on file changes (requires ptw)
pip install pytest-watch

# Watch and run tests
ptw tests/
```

## Best Practices

1. **Always run full test suite before committing**
   ```bash
   pytest tests/ && ruff check . && mypy landscape_mcp.py
   ```

2. **Use `pytest -v` for clear output**
   - Shows which tests passed/failed
   - Easy to identify specific failures

3. **Include `--cov-report=term-missing` for coverage**
   - Shows which lines aren't covered by tests
   - Helps identify gaps

4. **Run security checks regularly**
   ```bash
   bandit -r . -ll
   ```

5. **Keep test data realistic**
   - Use actual API response formats
   - Include edge cases (empty results, errors)

6. **Test error paths**
   - API failures
   - Missing parameters
   - Invalid input

## Quick Reference

```bash
# One-liner to run all quality checks
pytest tests/ -v --cov && ruff check . && mypy landscape_mcp.py --ignore-missing-imports && bandit -r . -ll
```

## Support

For test failures or issues:

1. Check test output carefully - often indicates the problem
2. Review the failing test code in `tests/`
3. Check `tests/conftest.py` for mock setup
4. Verify environment variables are set correctly
5. Ensure all dependencies installed: `pip install -e ".[test]"`

---

**Last Updated:** 2026-01-29
**Test Suite Version:** 1.0.0
**Python Versions Tested:** 3.10, 3.11, 3.12
