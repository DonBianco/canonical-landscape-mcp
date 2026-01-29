#!/usr/bin/env python3
"""
Landscape MCP Server - Community Edition

DISCLAIMER: This is an UNOFFICIAL, COMMUNITY-DRIVEN project.
NOT endorsed, affiliated with, or supported by Canonical Ltd.

Created by a system administrator for personal/organizational use.
Provided "AS IS" without warranty of any kind.

Use at your own risk. See LICENSE file for full terms.
"""

import asyncio
import json
import os
from typing import Any
from landscape_api.base import API
from mcp.server import Server
from mcp.types import Tool, TextContent, Prompt, PromptArgument, GetPromptResult, PromptMessage, Resource, ResourceTemplate, AnyUrl

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URI = os.getenv("LANDSCAPE_API_URI", "Your URI")
API_KEY = os.getenv("LANDSCAPE_API_KEY", "Your API")
API_SECRET = os.getenv("LANDSCAPE_API_SECRET", "Your Secret")

app = Server(
    "landscape-api-smart",
    version="1.0.0",
    instructions="Landscape MCP Server provides comprehensive infrastructure management through tools (query/audit capabilities), resources (real-time data access), and prompts (guided analysis workflows). Use prompts for complex infrastructure analysis tasks, resources for read-only data context, and tools for specific queries and operations."
)

# Initialize API client
api_client = API(
    uri=API_URI,
    access_key=API_KEY,
    secret_key=API_SECRET,
    ssl_ca_file=None,
    json=True
)



# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_result(data) -> str:
    """Format result as JSON."""
    if not data:
        return "No data"
    return json.dumps(data, default=str)


def get_package_on_computer(hostname: str, package_name: str) -> dict:
    """Fast package lookup on specific computer."""
    try:
        # Step 1: Get computer ID by hostname
        computers = api_client.get_computers(query=hostname, limit=1)

        if not computers or not isinstance(computers, list):
            return {"error": f"Computer {hostname} not found"}

        computer = computers[0] if isinstance(computers, list) else computers
        computer_id = computer.get('id')

        if not computer_id:
            return {"error": f"Could not extract computer ID for {hostname}"}

        # Step 2: Query package with computer ID filter
        packages = api_client.get_packages(search=package_name, query=f"id:{computer_id}", limit=1)

        if not packages:
            return {
                "hostname": hostname,
                "package": package_name,
                "status": "not_installed"
            }

        pkg = packages[0] if isinstance(packages, list) else packages

        return {
            "hostname": hostname,
            "package": pkg.get('name', package_name),
            "version": pkg.get('version', 'unknown'),
            "summary": pkg.get('summary', '')
        }

    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


def get_activities_for_computer(hostname: str = "", query: str = "", limit: int = 3, offset: int = 0) -> dict:
    """Get activities/audit log for a specific computer by hostname.

    By default, returns only the last 3 activities for the specified computer.
    Uses efficient API filtering with computer:id:{computer_id} query parameter.
    """
    try:
        # If hostname is provided, get computer ID first and use API filter
        if hostname:
            computers_str = api_client.get_computers(query=hostname, limit=1)

            # Parse JSON response
            computers = json.loads(computers_str) if isinstance(computers_str, str) else computers_str

            if not computers or not isinstance(computers, list):
                return {"error": f"Computer {hostname} not found"}

            computer = computers[0]
            computer_id = computer.get('id')

            if not computer_id:
                return {"error": f"Could not extract computer ID for {hostname}"}

            # Build query with computer:id filter for efficient API-side filtering
            # This avoids fetching all activities - API will only return activities for this computer
            computer_query = f"computer:id:{computer_id}"

            # Append any additional query filters
            if query:
                computer_query = f"{computer_query} {query}"

            # Fetch only activities for this specific computer (API-side filtering)
            activities_str = api_client.get_activities(query=computer_query, limit=limit, offset=offset)

            # Parse JSON response
            activities = json.loads(activities_str) if isinstance(activities_str, str) else activities_str
            return activities

        else:
            # No hostname filter - return all activities
            activities_str = api_client.get_activities(query=query, limit=limit, offset=offset)
            activities = json.loads(activities_str) if isinstance(activities_str, str) else activities_str
            return activities

    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


# ============================================================================
# MCP SERVER - TOOLS
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List tools."""
    return [
        Tool(
            name="landscape_query_computers",
            description="Query computers by tag/hostname/status",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "tag:production or hostname or needs:reboot:true"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results"
                    }
                }
            }
        ),
        Tool(
            name="landscape_query_packages",
            description="Search packages",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Package name"
                    },
                    "query": {
                        "type": "string",
                        "description": "Filter (e.g., id:707)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results"
                    }
                },
                "required": ["search"]
            }
        ),
        Tool(
            name="landscape_query_alerts",
            description="Get alerts",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="landscape_query_offline",
            description="Get offline computers",
            inputSchema={
                "type": "object",
                "properties": {
                    "since_minutes": {
                        "type": "integer",
                        "description": "Offline minutes"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results"
                    }
                }
            }
        ),
        Tool(
            name="landscape_fast_package_lookup",
            description="Fast package lookup on computer",
            inputSchema={
                "type": "object",
                "properties": {
                    "hostname": {
                        "type": "string",
                        "description": "Hostname"
                    },
                    "package": {
                        "type": "string",
                        "description": "Package name"
                    }
                },
                "required": ["hostname", "package"]
            }
        ),
        Tool(
            name="landscape_query_activities",
            description="Get activities/audit log for computers. Returns last 3 activities by default. Uses efficient API-side filtering when hostname is provided.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hostname": {
                        "type": "string",
                        "description": "Hostname to filter activities (e.g., 'my-laptop'). When provided, only fetches activities for this specific computer."
                    },
                    "query": {
                        "type": "string",
                        "description": "Additional filter query (e.g., 'status:succeeded' or 'created-after:2026-01-20')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of activities to return (default 3)"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Starting offset for pagination (default 0)"
                    }
                }
            }
        ),
    ]


# ============================================================================
# ============================================================================
# MCP SERVER - TOOL EXECUTION
# ============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute tool calls."""
    try:
        if name == "landscape_query_computers":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 25)
            result = api_client.get_computers(query=query, limit=limit)
            output = format_result(result)
            return [TextContent(type="text", text=output)]

        elif name == "landscape_query_packages":
            search = arguments.get("search", "")
            query = arguments.get("query", "")
            limit = arguments.get("limit", 50)

            # Fallback: if query is provided but search isn't, use query as search
            if query and not search:
                search = query

            if not search:
                return [TextContent(type="text", text="Error: 'search' parameter is required")]
            # API requires query as first positional arg (can be empty string to search all computers)
            result = api_client.get_packages(query="tag:ALL", search=search, limit=limit)
            output = format_result(result)
            return [TextContent(type="text", text=output)]

        elif name == "landscape_query_alerts":
            result = api_client.get_alerts()
            output = format_result(result)
            return [TextContent(type="text", text=output)]

        elif name == "landscape_query_offline":
            since_minutes = arguments.get("since_minutes", 60)
            limit = arguments.get("limit", 25)
            result = api_client.get_not_pinging_computers(
                since_minutes=str(since_minutes),
                limit=str(limit)
            )
            output = format_result(result)
            return [TextContent(type="text", text=output)]

        elif name == "landscape_fast_package_lookup":
            hostname = arguments.get("hostname", "")
            package = arguments.get("package", "")

            if not hostname or not package:
                return [TextContent(type="text", text="Error: 'hostname' and 'package' parameters are required")]

            result = get_package_on_computer(hostname, package)
            output = format_result(result)
            return [TextContent(type="text", text=output)]

        elif name == "landscape_query_activities":
            hostname = arguments.get("hostname", "")
            query = arguments.get("query", "")
            limit = arguments.get("limit", 3)  # Default to 3 activities
            offset = arguments.get("offset", 0)
            result = get_activities_for_computer(hostname=hostname, query=query, limit=limit, offset=offset)
            output = format_result(result)
            return [TextContent(type="text", text=output)]

        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

    except Exception as e:
        error_msg = f"Error ({type(e).__name__}): {str(e)}"
        return [TextContent(type="text", text=error_msg)]


# ============================================================================
# MCP SERVER - PROMPTS
# ============================================================================

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available prompts for guided infrastructure analysis."""
    return [
        Prompt(
            name="system_health_check",
            description="Comprehensive infrastructure health analysis with recommendations",
            arguments=[
                PromptArgument(
                    name="environment",
                    description="Infrastructure environment filter (production/staging/development/all)",
                    required=False
                ),
                PromptArgument(
                    name="severity",
                    description="Alert severity filter (critical/warning/all)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="package_audit",
            description="Audit packages across infrastructure for security updates and compliance",
            arguments=[
                PromptArgument(
                    name="package_name",
                    description="Specific package name to audit, or 'all' for all packages",
                    required=False
                ),
                PromptArgument(
                    name="severity",
                    description="Filter by CVE severity level (critical/high/medium/all)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="incident_investigation",
            description="Investigate system incidents using activity logs and audit trails",
            arguments=[
                PromptArgument(
                    name="hostname",
                    description="Affected machine hostname to investigate",
                    required=False
                ),
                PromptArgument(
                    name="timeframe",
                    description="Hours to look back in activity logs (default: 24)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="capacity_planning",
            description="Analyze infrastructure capacity and growth trends for resource planning",
            arguments=[
                PromptArgument(
                    name="tag",
                    description="Infrastructure segment/tag to analyze (e.g., production, database-tier)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="compliance_report",
            description="Generate compliance status report for audits and documentation",
            arguments=[
                PromptArgument(
                    name="standard",
                    description="Compliance standard (SOC2/ISO27001/PCI-DSS/all)",
                    required=False
                )
            ]
        )
    ]


@app.get_prompt()
async def get_prompt(
    name: str,
    arguments: dict[str, str] | None = None
) -> GetPromptResult:
    """Get a specific prompt with context from Landscape infrastructure data."""
    args = arguments or {}

    if name == "system_health_check":
        environment = args.get("environment", "all")
        severity = args.get("severity", "all")

        # Fetch infrastructure data
        try:
            computers_data = api_client.get_computers(query="", limit=100) if environment == "all" else api_client.get_computers(query=f"tag:{environment}", limit=100)
            alerts_data = api_client.get_alerts()
            offline_data = api_client.get_not_pinging_computers(since_minutes="60", limit="25")

            computers_info = json.dumps(computers_data, default=str) if computers_data else "{}"
            alerts_info = json.dumps(alerts_data, default=str) if alerts_data else "{}"
            offline_info = json.dumps(offline_data, default=str) if offline_data else "{}"
        except Exception as e:
            computers_info = f"Error fetching data: {str(e)}"
            alerts_info = ""
            offline_info = ""

        prompt_text = f"""Analyze the health of the {environment} infrastructure and provide detailed recommendations.

Focus on these areas:
1. **Machines Needing Reboot**: Identify systems requiring kernel updates or service restarts
2. **Active Alerts**: Review current system alerts (filtering by {severity} severity if specified)
3. **Offline Systems**: Check for machines offline for more than 60 minutes
4. **Package Updates**: Assess overall patch/update status
5. **Infrastructure Overview**: Provide summary of total systems and their status

Current Infrastructure Data:
- Computers: {computers_info}
- Alerts: {alerts_info}
- Offline Systems: {offline_info}

Provide:
- Executive summary of infrastructure health
- Critical issues requiring immediate attention
- Medium-priority items for next maintenance window
- Long-term optimization recommendations
- Risk assessment and mitigation strategies"""

        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )

    elif name == "package_audit":
        package_name = args.get("package_name", "all")
        severity = args.get("severity", "all")

        try:
            search_term = "all" if package_name == "all" else package_name
            packages_data = api_client.get_packages(search=search_term, query="tag:ALL", limit=100)
            packages_info = json.dumps(packages_data, default=str) if packages_data else "{}"
        except Exception as e:
            packages_info = f"Error fetching packages: {str(e)}"

        prompt_text = f"""Conduct a comprehensive security audit of installed packages in the infrastructure.

Scope:
- Package: {package_name}
- CVE Severity: {severity}

Package Inventory Data:
{packages_info}

Analysis Tasks:
1. **Security Updates Available**: Identify packages with available security updates
2. **CVE Impact**: List any known CVEs affecting installed versions
3. **Deprecation Status**: Check for deprecated or EOL packages
4. **Compliance**: Verify package versions align with organizational standards
5. **Risk Assessment**: Evaluate risk of current package versions

Deliverables:
- List of packages needing security updates (by criticality)
- Estimated impact of upgrades
- Recommended remediation timeline
- Rollback considerations
- Testing recommendations before deployment"""

        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )

    elif name == "incident_investigation":
        hostname = args.get("hostname", "all systems")
        timeframe = args.get("timeframe", "24")

        try:
            if hostname != "all systems":
                activities_data = get_activities_for_computer(hostname=hostname, limit=50, offset=0)
            else:
                activities_data = api_client.get_activities(query="", limit=50, offset=0)
            activities_info = json.dumps(activities_data, default=str) if activities_data else "{}"
        except Exception as e:
            activities_info = f"Error fetching activities: {str(e)}"

        prompt_text = f"""Investigate system incident(s) using activity logs and audit trails.

Incident Scope:
- Target: {hostname}
- Timeframe: Last {timeframe} hours
- Activity Logs:
{activities_info}

Investigation Framework:
1. **Timeline Reconstruction**: Build chronological sequence of events
2. **Root Cause Analysis**: Identify what triggered the incident
3. **Impact Assessment**: Determine affected systems and scope
4. **Correlation Analysis**: Connect related events across systems
5. **Pattern Detection**: Identify if part of larger issue

Report Should Include:
- Detailed incident timeline with key events
- Root cause analysis with evidence
- Systems and services affected
- Data or security implications
- Corrective actions taken
- Preventive measures for future incidents
- Recommended monitoring/alerting improvements"""

        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )

    elif name == "capacity_planning":
        tag = args.get("tag", "all infrastructure")

        try:
            if tag != "all infrastructure":
                computers_data = api_client.get_computers(query=f"tag:{tag}", limit=100)
            else:
                computers_data = api_client.get_computers(query="", limit=100)
            computers_info = json.dumps(computers_data, default=str) if computers_data else "{}"
        except Exception as e:
            computers_info = f"Error fetching data: {str(e)}"

        prompt_text = f"""Analyze infrastructure capacity and forecast growth trends for resource planning.

Infrastructure Segment: {tag}

Current Resource Inventory:
{computers_info}

Analysis Areas:
1. **Current Utilization**: Assess current resource usage and capacity
2. **Growth Trends**: Analyze historical usage patterns (if available)
3. **Headroom Analysis**: Calculate available capacity for future workloads
4. **Scaling Recommendations**: Suggest when/how to add capacity
5. **Cost Optimization**: Identify cost-saving opportunities
6. **Technology Refresh**: Assess need for system upgrades

Capacity Report Should Provide:
- Current resource summary (CPUs, memory, storage, systems)
- Utilization metrics and trends
- Projected capacity needs for next 6, 12, and 24 months
- Recommended scaling strategy
- Timeline and cost estimates for expansion
- Risk assessment for capacity constraints
- Recommendations for load balancing or consolidation"""

        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )

    elif name == "compliance_report":
        standard = args.get("standard", "all")

        try:
            computers_data = api_client.get_computers(query="", limit=100)
            alerts_data = api_client.get_alerts()
            computers_info = json.dumps(computers_data, default=str) if computers_data else "{}"
            alerts_info = json.dumps(alerts_data, default=str) if alerts_data else "{}"
        except Exception as e:
            computers_info = f"Error fetching data: {str(e)}"
            alerts_info = ""

        prompt_text = f"""Generate compliance status report for audits and regulatory documentation.

Compliance Standard(s): {standard}

Infrastructure Baseline:
- Systems: {computers_info}
- Alerts/Issues: {alerts_info}

Compliance Evaluation:
1. **Patch Management**: Verify systems are current with security updates
2. **System Hardening**: Check for security baselines and hardening
3. **Vulnerability Status**: Assess current vulnerability posture
4. **Monitoring & Logging**: Verify adequate audit logging is enabled
5. **Access Control**: Review system access policies and configurations
6. **Documentation**: Ensure security policies and procedures are documented

Compliance Report Structure:
- Executive Summary
- Compliance Status (Compliant/Non-Compliant/Partial)
- Current State Assessment
- Identified Gaps (if any)
- Remediation Plan and Timeline
- Risk Mitigation Strategies
- Evidence and Documentation Trail
- Recommended Ongoing Monitoring"""

        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )

    else:
        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=f"Unknown prompt: {name}")
                )
            ]
        )


# ============================================================================
# MCP SERVER - RESOURCES
# ============================================================================

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available infrastructure resources."""
    return [
        Resource(
            uri=AnyUrl("landscape://infrastructure/summary"),
            name="Infrastructure Summary",
            description="Real-time overview of all managed systems, their status, and key metrics",
            mimeType="application/json"
        ),
        Resource(
            uri=AnyUrl("landscape://alerts/active"),
            name="Active Alerts",
            description="Current system alerts with severity levels and affected hosts",
            mimeType="application/json"
        ),
        Resource(
            uri=AnyUrl("landscape://computers/online"),
            name="Online Computers",
            description="List of all currently online managed systems",
            mimeType="application/json"
        ),
        Resource(
            uri=AnyUrl("landscape://computers/offline"),
            name="Offline Computers",
            description="List of systems currently offline (not pinging)",
            mimeType="application/json"
        ),
        Resource(
            uri=AnyUrl("landscape://activities/recent"),
            name="Recent Activities",
            description="Recent system activities and audit log entries (last 50 activities)",
            mimeType="application/json"
        ),
        Resource(
            uri=AnyUrl("landscape://packages/security-updates"),
            name="Security Updates Available",
            description="Packages with available security updates across infrastructure",
            mimeType="application/json"
        )
    ]


@app.list_resource_templates()
async def list_resource_templates() -> list[ResourceTemplate]:
    """List resource templates for dynamic resource URIs."""
    return [
        ResourceTemplate(
            uriTemplate="landscape://computers/{tag}",
            name="Computers by Tag",
            description="Filter computers by infrastructure tag (e.g., production, staging, database-tier)"
        ),
        ResourceTemplate(
            uriTemplate="landscape://activities/{hostname}",
            name="Machine Activity Log",
            description="Activity history for a specific machine"
        )
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read a specific resource by URI."""
    uri_str = str(uri)

    try:
        if uri_str == "landscape://infrastructure/summary":
            try:
                computers = api_client.get_computers(query="", limit=1000)
                alerts = api_client.get_alerts()
                offline = api_client.get_not_pinging_computers(since_minutes="60", limit="1000")

                computers_list = computers if isinstance(computers, list) else [computers] if computers else []
                alerts_list = alerts if isinstance(alerts, list) else [alerts] if alerts else []
                offline_list = offline if isinstance(offline, list) else [offline] if offline else []

                summary = {
                    "total_machines": len(computers_list),
                    "online_count": len(computers_list) - len(offline_list),
                    "offline_count": len(offline_list),
                    "active_alerts": len(alerts_list),
                    "critical_alerts": len([a for a in alerts_list if isinstance(a, dict) and a.get("type") == "critical"]),
                    "warning_alerts": len([a for a in alerts_list if isinstance(a, dict) and a.get("type") == "warning"]),
                    "last_updated": "current"
                }
                return json.dumps(summary, default=str, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        elif uri_str == "landscape://alerts/active":
            try:
                alerts = api_client.get_alerts()
                alerts_list = alerts if isinstance(alerts, list) else [alerts] if alerts else []
                return json.dumps({"alerts": alerts_list, "count": len(alerts_list)}, default=str, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        elif uri_str == "landscape://computers/online":
            try:
                computers = api_client.get_computers(query="", limit=1000)
                computers_list = computers if isinstance(computers, list) else [computers] if computers else []
                offline = api_client.get_not_pinging_computers(since_minutes="60", limit="1000")
                offline_ids = set()
                if offline:
                    offline_list = offline if isinstance(offline, list) else [offline]
                    offline_ids = {item.get("id") for item in offline_list if isinstance(item, dict)}

                online = [c for c in computers_list if isinstance(c, dict) and c.get("id") not in offline_ids]
                return json.dumps({"online_computers": online, "count": len(online)}, default=str, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        elif uri_str == "landscape://computers/offline":
            try:
                offline = api_client.get_not_pinging_computers(since_minutes="60", limit="1000")
                offline_list = offline if isinstance(offline, list) else [offline] if offline else []
                return json.dumps({"offline_computers": offline_list, "count": len(offline_list)}, default=str, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        elif uri_str == "landscape://activities/recent":
            try:
                activities = api_client.get_activities(query="", limit=50, offset=0)
                activities_list = activities if isinstance(activities, list) else [activities] if activities else []
                return json.dumps({"recent_activities": activities_list, "count": len(activities_list)}, default=str, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        elif uri_str == "landscape://packages/security-updates":
            try:
                # Note: This is a simplified implementation
                # In production, you'd want to cross-reference package vulnerabilities
                packages = api_client.get_packages(search="", query="tag:ALL", limit=1000)
                packages_list = packages if isinstance(packages, list) else [packages] if packages else []
                security_updates = [p for p in packages_list if isinstance(p, dict) and ("security" in str(p).lower() or "update" in str(p).lower())]
                return json.dumps({"security_updates": security_updates, "count": len(security_updates)}, default=str, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        elif uri_str.startswith("landscape://computers/"):
            tag = uri_str.replace("landscape://computers/", "")
            try:
                computers = api_client.get_computers(query=f"tag:{tag}", limit=1000)
                computers_list = computers if isinstance(computers, list) else [computers] if computers else []
                return json.dumps({"tag": tag, "computers": computers_list, "count": len(computers_list)}, default=str, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        elif uri_str.startswith("landscape://activities/"):
            hostname = uri_str.replace("landscape://activities/", "")
            try:
                activities = get_activities_for_computer(hostname=hostname, limit=50, offset=0)
                activities_list = activities if isinstance(activities, list) else [activities] if activities else []
                return json.dumps({"hostname": hostname, "activities": activities_list, "count": len(activities_list) if isinstance(activities_list, list) else 0}, default=str, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        else:
            return json.dumps({"error": f"Unknown resource URI: {uri_str}"}, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to read resource: {str(e)}"}, indent=2)


# ============================================================================
# SERVER STARTUP
# ============================================================================

def main():
    """Main entry point for the MCP server."""
    import sys
    from mcp.server.stdio import stdio_server

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
