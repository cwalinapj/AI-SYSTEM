"""Starter manifest for the ml MCP server."""

from mcp.servers.types import ToolSpec

SERVER_NAME = "ml"
TOOLS: list[ToolSpec] = [
    {
        "name": "list_datasets",
        "parameters": [],
    },
    {
        "name": "get_run_history",
        "parameters": [],
    },
    {
        "name": "launch_training_template",
        "parameters": ['name'],
    },
]
RESOURCES = ['ml://datasets', 'ml://runs', 'ml://reports']
PROMPTS = ['compare training runs and recommend a repeatable experiment']
