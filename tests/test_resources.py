"""
Unit tests for Landscape MCP Server resources.

Tests all 6 resource URIs and 2 resource templates:
- landscape://infrastructure/summary
- landscape://alerts/active
- landscape://computers/online
- landscape://computers/offline
- landscape://activities/recent
- landscape://packages/security-updates
- landscape://computers/{tag}
- landscape://activities/{hostname}
"""

import pytest
import json
from mcp.types import AnyUrl


class TestResourceListing:
    """Tests for resource listing functionality."""

    @pytest.mark.asyncio
    async def test_list_resources_returns_all_resources(self):
        """Test that all 6 resources are listed."""
        from landscape_mcp import list_resources

        resources = await list_resources()

        assert len(resources) == 6, f"Should have 6 resources, got {len(resources)}"
        resource_uris = [str(resource.uri) for resource in resources]

        expected_resources = [
            "landscape://infrastructure/summary",
            "landscape://alerts/active",
            "landscape://computers/online",
            "landscape://computers/offline",
            "landscape://activities/recent",
            "landscape://packages/security-updates"
        ]

        for resource_uri in expected_resources:
            assert resource_uri in resource_uris, f"Missing resource: {resource_uri}"

    @pytest.mark.asyncio
    async def test_list_resource_templates(self):
        """Test that resource templates are listed."""
        from landscape_mcp import list_resource_templates

        templates = await list_resource_templates()

        assert len(templates) == 2, f"Should have 2 templates, got {len(templates)}"
        template_uris = [template.uriTemplate for template in templates]

        expected_templates = [
            "landscape://computers/{tag}",
            "landscape://activities/{hostname}"
        ]

        for template_uri in expected_templates:
            assert template_uri in template_uris, f"Missing template: {template_uri}"

    @pytest.mark.asyncio
    async def test_resource_has_description(self):
        """Test that each resource has a description."""
        from landscape_mcp import list_resources

        resources = await list_resources()

        for resource in resources:
            assert resource.description, f"Resource {resource.uri} has no description"
            assert len(resource.description) > 5, f"Resource {resource.uri} has short description"

    @pytest.mark.asyncio
    async def test_resource_has_mime_type(self):
        """Test that each resource has a MIME type."""
        from landscape_mcp import list_resources

        resources = await list_resources()

        for resource in resources:
            assert resource.mimeType, f"Resource {resource.uri} has no MIME type"
            assert resource.mimeType == "application/json", "All resources should be JSON"


class TestInfrastructureSummaryResource:
    """Tests for infrastructure/summary resource."""

    @pytest.mark.asyncio
    async def test_infrastructure_summary_returns_json(self, mock_api_client):
        """Test that infrastructure summary resource returns valid JSON."""
        from landscape_mcp import read_resource

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await read_resource(AnyUrl("landscape://infrastructure/summary"))

            assert result, "Should return result"

            # Parse JSON
            data = json.loads(result)
            assert isinstance(data, dict), "Should return dict"

    @pytest.mark.asyncio
    async def test_infrastructure_summary_contains_key_metrics(self, mock_api_client):
        """Test that infrastructure summary contains key metrics."""
        from landscape_mcp import read_resource

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await read_resource(AnyUrl("landscape://infrastructure/summary"))

            data = json.loads(result)

            # Check for key metrics
            assert "total_machines" in data, "Should include total_machines"
            assert "online_count" in data, "Should include online_count"
            assert "offline_count" in data, "Should include offline_count"
            assert "active_alerts" in data, "Should include active_alerts"


class TestAlertsResource:
    """Tests for alerts/active resource."""

    @pytest.mark.asyncio
    async def test_active_alerts_returns_json(self, mock_api_client):
        """Test that active alerts resource returns valid JSON."""
        from landscape_mcp import read_resource

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await read_resource(AnyUrl("landscape://alerts/active"))

            assert result, "Should return result"

            data = json.loads(result)
            assert isinstance(data, dict), "Should return dict"

    @pytest.mark.asyncio
    async def test_active_alerts_includes_alerts_list(self, mock_api_client):
        """Test that active alerts includes the alerts list."""
        from landscape_mcp import read_resource

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await read_resource(AnyUrl("landscape://alerts/active"))

            data = json.loads(result)

            assert "alerts" in data, "Should include alerts list"
            assert "count" in data, "Should include count"
            assert isinstance(data["alerts"], list), "Alerts should be a list"


class TestComputersResource:
    """Tests for computers resources."""

    @pytest.mark.asyncio
    async def test_online_computers_resource(self, mock_api_client):
        """Test online computers resource."""
        from landscape_mcp import read_resource

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await read_resource(AnyUrl("landscape://computers/online"))

            data = json.loads(result)

            assert "online_computers" in data, "Should include online_computers"
            assert "count" in data, "Should include count"
            assert isinstance(data["online_computers"], list), "Should be a list"

    @pytest.mark.asyncio
    async def test_offline_computers_resource(self, mock_api_client):
        """Test offline computers resource."""
        from landscape_mcp import read_resource

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await read_resource(AnyUrl("landscape://computers/offline"))

            data = json.loads(result)

            assert "offline_computers" in data, "Should include offline_computers"
            assert "count" in data, "Should include count"
            assert isinstance(data["offline_computers"], list), "Should be a list"

    @pytest.mark.asyncio
    async def test_computers_by_tag_template(self, mock_api_client):
        """Test computers by tag resource template."""
        from landscape_mcp import read_resource

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await read_resource(AnyUrl("landscape://computers/production"))

            data = json.loads(result)

            assert "tag" in data, "Should include tag"
            assert data["tag"] == "production", "Tag should match requested value"
            assert "computers" in data, "Should include computers"
            assert "count" in data, "Should include count"


class TestActivitiesResource:
    """Tests for activities resources."""

    @pytest.mark.asyncio
    async def test_recent_activities_resource(self, mock_api_client):
        """Test recent activities resource."""
        from landscape_mcp import read_resource

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await read_resource(AnyUrl("landscape://activities/recent"))

            data = json.loads(result)

            assert "recent_activities" in data, "Should include recent_activities"
            assert "count" in data, "Should include count"
            assert isinstance(data["recent_activities"], list), "Should be a list"

    @pytest.mark.asyncio
    async def test_activities_by_hostname_template(self, mock_api_client):
        """Test activities by hostname resource template."""
        from landscape_mcp import read_resource

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await read_resource(AnyUrl("landscape://activities/prod-web-01"))

            data = json.loads(result)

            assert "hostname" in data, "Should include hostname"
            assert data["hostname"] == "prod-web-01", "Hostname should match"
            assert "activities" in data, "Should include activities"


class TestSecurityUpdatesResource:
    """Tests for security updates resource."""

    @pytest.mark.asyncio
    async def test_security_updates_resource(self, mock_api_client):
        """Test security updates available resource."""
        from landscape_mcp import read_resource

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await read_resource(AnyUrl("landscape://packages/security-updates"))

            data = json.loads(result)

            assert "security_updates" in data, "Should include security_updates"
            assert "count" in data, "Should include count"
            assert isinstance(data["security_updates"], list), "Should be a list"


class TestResourceErrorHandling:
    """Tests for error handling in resources."""

    @pytest.mark.asyncio
    async def test_unknown_resource_returns_error(self):
        """Test that unknown resource returns error."""
        from landscape_mcp import read_resource

        result = await read_resource(AnyUrl("landscape://unknown/resource"))

        data = json.loads(result)

        assert "error" in data, "Should include error message"
        assert "Unknown" in data["error"], "Should indicate unknown resource"

    @pytest.mark.asyncio
    async def test_resource_handles_api_errors(self, mock_api_client_error):
        """Test that resources handle API errors gracefully."""
        from landscape_mcp import read_resource

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client_error):
            result = await read_resource(AnyUrl("landscape://infrastructure/summary"))

            # Should return error in JSON, not raise exception
            data = json.loads(result)
            assert "error" in data, "Should have error field"


# Import mock module for patches
import pytest.mock
