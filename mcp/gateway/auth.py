"""Simple authorization helpers for MCP capability scoping."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentScope:
    """Represents the MCP servers an agent is permitted to use."""

    agent_name: str
    allowed_servers: frozenset[str]


def require_server_access(scope: AgentScope, server_name: str) -> None:
    """Raises when an agent is not allowed to access a server."""

    if server_name not in scope.allowed_servers:
        raise PermissionError(
            f"Agent '{scope.agent_name}' is not allowed to use MCP server '{server_name}'."
        )
