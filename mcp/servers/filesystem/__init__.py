"""Starter manifest for the filesystem MCP server."""

from mcp.servers.types import ToolSpec

SERVER_NAME = "filesystem"
TOOLS: list[ToolSpec] = [
    {
        "name": "read_file",
        "parameters": ['path'],
    },
    {
        "name": "list_directory",
        "parameters": ['path'],
    },
    {
        "name": "write_file",
        "parameters": ['path', 'content'],
    },
]
RESOURCES = ['file://workspace/policies', 'file://workspace/layout']
PROMPTS = ['inspect project files within the allowed workspace root']
