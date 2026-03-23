"""Starter manifest for the docker MCP server."""

from mcp.servers.types import ToolSpec

SERVER_NAME = "docker"
TOOLS: list[ToolSpec] = [
    {
        "name": "inspect_containers",
        "parameters": [],
    },
    {
        "name": "list_mapped_ports",
        "parameters": [],
    },
    {
        "name": "run_validation_container",
        "parameters": ['image'],
    },
]
RESOURCES = ['docker://containers', 'docker://ports']
PROMPTS = ['investigate service health and port mappings']
