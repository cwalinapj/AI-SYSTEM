"""Shared typed structures for starter MCP server manifests."""

from typing import TypedDict


class ToolSpec(TypedDict):
    """Describes a single MCP tool exposed by a starter server."""

    name: str
    parameters: list[str]
