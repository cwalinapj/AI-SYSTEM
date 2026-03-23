"""Starter manifest for the luxonis MCP server."""

from mcp.servers.types import ToolSpec

SERVER_NAME = "luxonis"
TOOLS: list[ToolSpec] = [
    {
        "name": "camera_inventory",
        "parameters": [],
    },
    {
        "name": "device_status",
        "parameters": [],
    },
    {
        "name": "run_calibration_playbook",
        "parameters": ['name'],
    },
]
RESOURCES = ['luxonis://inventory', 'luxonis://playbooks', 'luxonis://pipelines']
PROMPTS = ['debug a Luxonis camera deployment or calibration issue']
