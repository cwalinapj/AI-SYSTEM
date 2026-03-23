"""Starter manifest for the memory MCP server."""

from mcp.servers.types import ToolSpec

SERVER_NAME = "memory"
TOOLS: list[ToolSpec] = [
    {
        "name": "search_memory",
        "parameters": ['query', 'namespace', 'top_k'],
    },
    {
        "name": "write_memory",
        "parameters": ['item'],
    },
    {
        "name": "get_recent_episodes",
        "parameters": ['project', 'limit'],
    },
    {
        "name": "get_procedures",
        "parameters": ['project', 'tags'],
    },
    {
        "name": "link_artifact",
        "parameters": ['memory_id', 'artifact_uri'],
    },
]
RESOURCES = ['memory://project/{name}/profile', 'memory://project/{name}/recent-incidents', 'memory://project/{name}/procedures']
PROMPTS = ['capture durable memory from a completed task']
