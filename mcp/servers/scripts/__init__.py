"""Starter manifest for the scripts MCP server."""

SERVER_NAME = "scripts"
TOOLS = ['register_script(name, project, artifact_uri, metadata)', 'get_script(name, project, version?)', 'list_scripts(project, tags?)', 'promote_session_to_script(session_id)', 'validate_script(name, version)']
RESOURCES = ['scripts://project/{name}', 'scripts://project/{name}/latest']
PROMPTS = ['promote a repeated workflow into a validated script']
