"""
Pytest configuration and fixtures for Landscape MCP Server tests.

Provides mocks, fixtures, and test data for unit and integration tests.
"""

import json
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Any


# ============================================================================
# MOCK DATA
# ============================================================================

MOCK_COMPUTERS = [
    {
        "id": "1",
        "hostname": "prod-web-01",
        "tags": ["production", "web-tier"],
        "last_update": "2026-01-29T14:30:00Z",
        "online": True
    },
    {
        "id": "2",
        "hostname": "prod-db-01",
        "tags": ["production", "database-tier"],
        "last_update": "2026-01-29T14:30:00Z",
        "online": True
    },
    {
        "id": "3",
        "hostname": "staging-web-01",
        "tags": ["staging", "web-tier"],
        "last_update": "2026-01-29T10:00:00Z",
        "online": False
    }
]

MOCK_ALERTS = [
    {
        "id": "alert-1",
        "type": "critical",
        "message": "Database server response time critical",
        "hostname": "prod-db-01",
        "timestamp": "2026-01-29T14:00:00Z"
    },
    {
        "id": "alert-2",
        "type": "warning",
        "message": "Package updates available",
        "hostname": "prod-web-01",
        "timestamp": "2026-01-29T13:30:00Z"
    }
]

MOCK_OFFLINE_COMPUTERS = [
    {
        "id": "3",
        "hostname": "staging-web-01",
        "tags": ["staging", "web-tier"],
        "offline_minutes": 480
    }
]

MOCK_PACKAGES = [
    {
        "id": "pkg-1",
        "name": "openssl",
        "version": "3.0.0",
        "summary": "Secure Sockets Layer and cryptography libraries and tools",
        "available_version": "3.1.0"
    },
    {
        "id": "pkg-2",
        "name": "openssh-server",
        "version": "8.4p1",
        "summary": "Secure shell server, an rlogin/rsh replacement",
        "available_version": "9.0p1"
    }
]

MOCK_ACTIVITIES = [
    {
        "id": "activity-1",
        "timestamp": "2026-01-29T14:20:00Z",
        "hostname": "prod-web-01",
        "action": "security-update",
        "status": "succeeded",
        "message": "Installed 5 security updates"
    },
    {
        "id": "activity-2",
        "timestamp": "2026-01-29T14:00:00Z",
        "hostname": "prod-web-01",
        "action": "reboot",
        "status": "succeeded",
        "message": "System rebooted"
    }
]


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_api_client():
    """Create a mock Landscape API client."""
    client = MagicMock()

    # Configure mock responses
    client.get_computers.return_value = MOCK_COMPUTERS
    client.get_alerts.return_value = MOCK_ALERTS
    client.get_not_pinging_computers.return_value = MOCK_OFFLINE_COMPUTERS
    client.get_packages.return_value = MOCK_PACKAGES
    client.get_activities.return_value = MOCK_ACTIVITIES

    return client


@pytest.fixture
def mock_api_client_json():
    """Create a mock API client that returns JSON strings (as the real API does)."""
    client = MagicMock()

    # Configure mock responses to return JSON strings
    client.get_computers.return_value = json.dumps(MOCK_COMPUTERS)
    client.get_alerts.return_value = json.dumps(MOCK_ALERTS)
    client.get_not_pinging_computers.return_value = json.dumps(MOCK_OFFLINE_COMPUTERS)
    client.get_packages.return_value = json.dumps(MOCK_PACKAGES)
    client.get_activities.return_value = json.dumps(MOCK_ACTIVITIES)

    return client


@pytest.fixture
def mock_api_client_error():
    """Create a mock API client that raises errors."""
    client = MagicMock()

    # Configure error responses
    client.get_computers.side_effect = Exception("API connection failed")
    client.get_alerts.side_effect = Exception("API authentication failed")
    client.get_packages.side_effect = Exception("API error: 500")

    return client


@pytest.fixture
def mock_landscape_mcp_app():
    """Create a mock MCP app instance."""
    app = MagicMock()
    app.name = "landscape-api-smart"
    app.version = "1.0.0"

    return app


@pytest.fixture
def sample_tool_arguments() -> dict[str, Any]:
    """Sample arguments for tool calls."""
    return {
        "query_computers": {
            "query": "tag:production",
            "limit": 25
        },
        "query_packages": {
            "search": "openssl",
            "limit": 50
        },
        "query_alerts": {},
        "query_offline": {
            "since_minutes": 60,
            "limit": 25
        },
        "fast_package_lookup": {
            "hostname": "prod-web-01",
            "package": "openssl"
        },
        "query_activities": {
            "hostname": "prod-web-01",
            "limit": 10,
            "offset": 0
        }
    }


@pytest.fixture
def sample_prompt_arguments() -> dict[str, dict[str, str]]:
    """Sample arguments for prompt calls."""
    return {
        "system_health_check": {
            "environment": "production",
            "severity": "critical"
        },
        "package_audit": {
            "package_name": "openssl",
            "severity": "critical"
        },
        "incident_investigation": {
            "hostname": "prod-web-01",
            "timeframe": "24"
        },
        "capacity_planning": {
            "tag": "production"
        },
        "compliance_report": {
            "standard": "SOC2"
        }
    }


# ============================================================================
# ENVIRONMENT FIXTURES
# ============================================================================

@pytest.fixture
def mock_env_variables(monkeypatch):
    """Mock environment variables for Landscape API."""
    monkeypatch.setenv("LANDSCAPE_API_URI", "https://landscape.example.com/api/")
    monkeypatch.setenv("LANDSCAPE_API_KEY", "test-api-key")
    monkeypatch.setenv("LANDSCAPE_API_SECRET", "test-api-secret")


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as asynchronous"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@pytest.fixture
def format_result_json():
    """Helper to format results as JSON."""
    def _format(data) -> str:
        if not data:
            return "No data"
        return json.dumps(data, default=str)
    return _format
