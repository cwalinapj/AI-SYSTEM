"""Starter manifest for the ml MCP server."""

SERVER_NAME = "ml"
TOOLS = ['list_datasets()', 'get_run_history()', 'launch_training_template(name)']
RESOURCES = ['ml://datasets', 'ml://runs', 'ml://reports']
PROMPTS = ['compare training runs and recommend a repeatable experiment']
