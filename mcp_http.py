#!/usr/bin/env python3
"""
Landscape MCP HTTP Server - Community Edition

DISCLAIMER: This is an UNOFFICIAL, COMMUNITY-DRIVEN project.
NOT endorsed, affiliated with, or supported by Canonical Ltd.

Created by a system administrator for personal/organizational use.
Provided "AS IS" without warranty of any kind.

Use at your own risk. See LICENSE file for full terms.
"""

import asyncio
import json
import os
from typing import Optional
from landscape_api.base import API
from mcp.server import Server
from mcp.types import Tool, TextContent

# For HTTP server
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
import uvicorn

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URI = os.getenv("LANDSCAPE_API_URI", "Your URI")
API_KEY = os.getenv("LANDSCAPE_API_KEY", "YOUR API")
API_SECRET = os.getenv("LANDSCAPE_API_SECRET", "YOUR SECRET")

# HTTP Server Configuration
HTTP_HOST = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("MCP_HTTP_PORT", "8000"))

# Initialize MCP Server
mcp_server = Server("landscape-api-http")

# Initialize Landscape API client
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
    """Get activities/audit log for a specific computer by hostname."""
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

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
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
# MCP SERVER - TOOL EXECUTION
# ============================================================================

@mcp_server.call_tool()
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
# HTTP SERVER SETUP
# ============================================================================

# Store active SSE connections
sse_connections = {}

async def handle_sse(request):
    """Handle SSE connection for MCP protocol."""
    from starlette.responses import StreamingResponse
    from sse_starlette import EventSourceResponse

    async def event_generator():
        """Generate SSE events."""
        # Create SSE transport
        transport = SseServerTransport("/messages")

        try:
            # Run MCP server with this transport
            async with transport:
                await mcp_server.run(
                    transport.read_stream,
                    transport.write_stream,
                    mcp_server.create_initialization_options()
                )
        except Exception as e:
            print(f"SSE error: {e}")
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())


async def handle_messages(request):
    """Handle POST messages endpoint."""
    try:
        body = await request.json()
        # Process MCP message
        # This is where we'd route the message to the appropriate handler
        return Response("", status_code=204)
    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status_code=500,
            media_type="application/json"
        )


async def health_check(request):
    """Health check endpoint."""
    return Response(
        json.dumps({
            "status": "healthy",
            "server": "landscape-mcp-http",
            "landscape_api": API_URI,
            "version": "1.0.0"
        }),
        media_type="application/json"
    )


async def root_handler(request):
    """Root endpoint with server info."""
    return Response(
        json.dumps({
            "name": "Landscape MCP HTTP Server",
            "version": "1.0.0",
            "endpoints": {
                "sse": "/sse",
                "messages": "/messages",
                "health": "/health"
            },
            "mcp_version": "1.24.0"
        }),
        media_type="application/json"
    )


# Create Starlette app
app = Starlette(
    routes=[
        Route("/", root_handler),
        Route("/sse", handle_sse),
        Route("/messages", handle_messages, methods=["POST"]),
        Route("/health", health_check),
    ]
)


# ============================================================================
# SERVER STARTUP
# ============================================================================

def main():
    """Start HTTP server."""
    print(f"🚀 Starting Landscape MCP HTTP Server")
    print(f"📡 Listening on http://{HTTP_HOST}:{HTTP_PORT}")
    print(f"🔗 SSE endpoint: http://{HTTP_HOST}:{HTTP_PORT}/sse")
    print(f"🔗 Messages endpoint: http://{HTTP_HOST}:{HTTP_PORT}/messages")
    print(f"💚 Health check: http://{HTTP_HOST}:{HTTP_PORT}/health")
    print(f"🏢 Landscape API: {API_URI}")
    print("")
    print("Press Ctrl+C to stop")

    uvicorn.run(
        app,
        host=HTTP_HOST,
        port=HTTP_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
