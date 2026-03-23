"""Starter manifest for the filesystem MCP server."""

SERVER_NAME = "filesystem"
TOOLS = ['read_file(path)', 'list_directory(path)', 'write_file(path, content)']
RESOURCES = ['file://workspace/policies', 'file://workspace/layout']
PROMPTS = ['inspect project files within the allowed workspace root']
