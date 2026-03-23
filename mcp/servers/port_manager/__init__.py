"""Starter manifest for the port_manager MCP server."""

SERVER_NAME = "port_manager"
TOOLS = ['reserve_port(service, protocol, category, preferred_port?)', 'release_port(service, port)', 'heartbeat(service, port)', 'audit_ports()', 'suggest_remap(service)']
RESOURCES = ['ports://leases/active', 'ports://conflicts', 'ports://ranges']
PROMPTS = ['resolve a compose port conflict safely']
