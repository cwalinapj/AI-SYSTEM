"""Starter manifest for the memory MCP server."""

SERVER_NAME = "memory"
TOOLS = ['search_memory(query, namespace, top_k)', 'write_memory(item)', 'get_recent_episodes(project, limit)', 'get_procedures(project, tags)', 'link_artifact(memory_id, artifact_uri)']
RESOURCES = ['memory://project/{name}/profile', 'memory://project/{name}/recent-incidents', 'memory://project/{name}/procedures']
PROMPTS = ['capture durable memory from a completed task']
