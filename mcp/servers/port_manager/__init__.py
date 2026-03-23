"""Starter manifest for the port_manager MCP server."""

from mcp.servers.types import ToolSpec

SERVER_NAME = "port_manager"
TOOLS: list[ToolSpec] = [
    {
        "name": "reserve_port",
        "parameters": ['service', 'protocol', 'category', 'preferred_port'],
    },
    {
        "name": "release_port",
        "parameters": ['service', 'port'],
    },
    {
        "name": "heartbeat",
        "parameters": ['service', 'port'],
    },
    {
        "name": "audit_ports",
        "parameters": [],
    },
    {
        "name": "suggest_remap",
        "parameters": ['service'],
    },
]
RESOURCES = ['ports://leases/active', 'ports://conflicts', 'ports://ranges']
PROMPTS = ['resolve a compose port conflict safely']

TOOL_NOTES = {
    "audit_ports": "Audits all active leased host ports and known container port mappings.",
}
