"""
Unit tests for Landscape MCP Server prompts.

Tests all 5 prompts:
- system_health_check
- package_audit
- incident_investigation
- capacity_planning
- compliance_report
"""

import pytest
from mcp.types import PromptMessage, TextContent


class TestPromptListing:
    """Tests for prompt listing functionality."""

    @pytest.mark.asyncio
    async def test_list_prompts_returns_all_prompts(self):
        """Test that all 5 prompts are listed."""
        from landscape_mcp import list_prompts

        prompts = await list_prompts()

        assert len(prompts) == 5, "Should have 5 prompts"
        prompt_names = [prompt.name for prompt in prompts]

        expected_prompts = [
            "system_health_check",
            "package_audit",
            "incident_investigation",
            "capacity_planning",
            "compliance_report"
        ]

        for prompt_name in expected_prompts:
            assert prompt_name in prompt_names, f"Missing prompt: {prompt_name}"

    @pytest.mark.asyncio
    async def test_prompt_has_description(self):
        """Test that each prompt has a description."""
        from landscape_mcp import list_prompts

        prompts = await list_prompts()

        for prompt in prompts:
            assert prompt.description, f"Prompt {prompt.name} has no description"
            assert len(prompt.description) > 10, f"Prompt {prompt.name} has short description"

    @pytest.mark.asyncio
    async def test_prompt_has_arguments(self):
        """Test that prompts have defined arguments."""
        from landscape_mcp import list_prompts

        prompts = await list_prompts()

        for prompt in prompts:
            assert hasattr(prompt, "arguments"), f"Prompt {prompt.name} has no arguments attribute"
            # Some prompts may have optional arguments
            if prompt.arguments:
                for arg in prompt.arguments:
                    assert arg.name, f"Prompt {prompt.name} has unnamed argument"


class TestSystemHealthCheckPrompt:
    """Tests for system_health_check prompt."""

    @pytest.mark.asyncio
    async def test_system_health_check_without_arguments(self, mock_api_client):
        """Test system_health_check prompt without arguments."""
        from landscape_mcp import get_prompt

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await get_prompt("system_health_check", {})

            assert result, "Should return result"
            assert result.messages, "Should have messages"
            assert isinstance(result.messages[0], PromptMessage), "Should be PromptMessage"

    @pytest.mark.asyncio
    async def test_system_health_check_with_environment_argument(self, mock_api_client):
        """Test system_health_check prompt with environment argument."""
        from landscape_mcp import get_prompt

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await get_prompt(
                "system_health_check",
                {"environment": "production", "severity": "critical"}
            )

            assert result, "Should return result"
            assert result.messages, "Should have messages"

            # Check that prompt mentions key areas
            prompt_text = result.messages[0].content.text
            assert "reboot" in prompt_text.lower(), "Should mention reboot status"
            assert "alerts" in prompt_text.lower(), "Should mention alerts"

    @pytest.mark.asyncio
    async def test_prompt_returns_prompt_message_type(self, mock_api_client):
        """Test that prompt returns proper message type."""
        from landscape_mcp import get_prompt

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await get_prompt("system_health_check", {})

            assert result.messages[0].role == "user", "Message role should be 'user'"
            assert result.messages[0].content.type == "text", "Content type should be 'text'"


class TestPackageAuditPrompt:
    """Tests for package_audit prompt."""

    @pytest.mark.asyncio
    async def test_package_audit_prompt_with_package_name(self, mock_api_client):
        """Test package_audit prompt with specific package."""
        from landscape_mcp import get_prompt

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await get_prompt(
                "package_audit",
                {"package_name": "openssl", "severity": "critical"}
            )

            assert result, "Should return result"
            assert result.messages, "Should have messages"

            prompt_text = result.messages[0].content.text
            assert "security" in prompt_text.lower(), "Should mention security"


class TestIncidentInvestigationPrompt:
    """Tests for incident_investigation prompt."""

    @pytest.mark.asyncio
    async def test_incident_investigation_with_hostname(self, mock_api_client):
        """Test incident_investigation prompt with hostname."""
        from landscape_mcp import get_prompt

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await get_prompt(
                "incident_investigation",
                {"hostname": "prod-web-01", "timeframe": "24"}
            )

            assert result, "Should return result"
            assert result.messages, "Should have messages"

            prompt_text = result.messages[0].content.text
            assert "timeline" in prompt_text.lower() or "event" in prompt_text.lower(), "Should mention timeline/events"


class TestCapacityPlanningPrompt:
    """Tests for capacity_planning prompt."""

    @pytest.mark.asyncio
    async def test_capacity_planning_with_tag(self, mock_api_client):
        """Test capacity_planning prompt with infrastructure tag."""
        from landscape_mcp import get_prompt

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await get_prompt(
                "capacity_planning",
                {"tag": "production"}
            )

            assert result, "Should return result"
            assert result.messages, "Should have messages"

            prompt_text = result.messages[0].content.text
            assert "capacity" in prompt_text.lower() or "resource" in prompt_text.lower(), "Should mention capacity/resources"


class TestComplianceReportPrompt:
    """Tests for compliance_report prompt."""

    @pytest.mark.asyncio
    async def test_compliance_report_with_standard(self, mock_api_client):
        """Test compliance_report prompt with compliance standard."""
        from landscape_mcp import get_prompt

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client):
            result = await get_prompt(
                "compliance_report",
                {"standard": "SOC2"}
            )

            assert result, "Should return result"
            assert result.messages, "Should have messages"

            prompt_text = result.messages[0].content.text
            assert "compliance" in prompt_text.lower(), "Should mention compliance"


class TestPromptErrorHandling:
    """Tests for error handling in prompts."""

    @pytest.mark.asyncio
    async def test_unknown_prompt_returns_error(self):
        """Test that unknown prompt returns error message."""
        from landscape_mcp import get_prompt

        result = await get_prompt("unknown_prompt", {})

        assert result, "Should return result"
        assert result.messages, "Should have messages"
        assert "Unknown" in result.messages[0].content.text, "Should indicate unknown prompt"

    @pytest.mark.asyncio
    async def test_prompt_handles_api_errors_gracefully(self, mock_api_client_error):
        """Test that prompts handle API errors gracefully."""
        from landscape_mcp import get_prompt

        with pytest.mock.patch('landscape_mcp.api_client', mock_api_client_error):
            # Should not raise, but return result with error context
            result = await get_prompt("system_health_check", {})

            assert result, "Should return result even with API error"
            assert result.messages, "Should have messages"


# Import mock module for mocking patches
import pytest.mock
