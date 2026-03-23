"""Starter manifest for the luxonis MCP server."""

SERVER_NAME = "luxonis"
TOOLS = ['camera_inventory()', 'device_status()', 'run_calibration_playbook(name)']
RESOURCES = ['luxonis://inventory', 'luxonis://playbooks', 'luxonis://pipelines']
PROMPTS = ['debug a Luxonis camera deployment or calibration issue']
