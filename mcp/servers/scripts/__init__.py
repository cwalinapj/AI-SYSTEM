"""Starter manifest for the scripts MCP server."""

from mcp.servers.types import ToolSpec

SERVER_NAME = "scripts"
TOOLS: list[ToolSpec] = [
    {
        "name": "register_script",
        "parameters": ['name', 'project', 'artifact_uri', 'metadata'],
    },
    {
        "name": "get_script",
        "parameters": ['name', 'project', 'version'],
    },
    {
        "name": "list_scripts",
        "parameters": ['project', 'tags'],
    },
    {
        "name": "promote_session_to_script",
        "parameters": ['session_id'],
    },
    {
        "name": "validate_script",
        "parameters": ['name', 'version'],
    },
]
RESOURCES = ['scripts://project/{name}', 'scripts://project/{name}/latest']
PROMPTS = ['promote a repeated workflow into a validated script']
