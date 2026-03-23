"""Starter manifest for the docker MCP server."""

SERVER_NAME = "docker"
TOOLS = ['inspect_containers()', 'list_mapped_ports()', 'run_validation_container(image)']
RESOURCES = ['docker://containers', 'docker://ports']
PROMPTS = ['investigate service health and port mappings']
