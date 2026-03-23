"""Starter manifest for the github MCP server."""

from mcp.servers.types import ToolSpec

SERVER_NAME = "github"
TOOLS: list[ToolSpec] = [
    {
        "name": "list_workflows",
        "parameters": [],
    },
    {
        "name": "get_failed_jobs",
        "parameters": [],
    },
    {
        "name": "read_pull_request",
        "parameters": ['number'],
    },
]
RESOURCES = ['github://repo/workflows', 'github://repo/pull-requests']
PROMPTS = ['summarize repository automation context for an agent']
