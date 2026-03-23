"""Starter manifest for the github MCP server."""

SERVER_NAME = "github"
TOOLS = ['list_workflows()', 'get_failed_jobs()', 'read_pull_request(number)']
RESOURCES = ['github://repo/workflows', 'github://repo/pull-requests']
PROMPTS = ['summarize repository automation context for an agent']
