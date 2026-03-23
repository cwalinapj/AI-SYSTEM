"""Minimal routing helpers for the MCP gateway layer."""

from dataclasses import dataclass
from pathlib import Path
from collections.abc import Collection
from typing import Mapping, TypedDict


REGISTRY_DIR = Path(__file__).resolve().parents[1] / "registry"
SERVERS_CONFIG = REGISTRY_DIR / "servers.yaml"
POLICIES_CONFIG = REGISTRY_DIR / "policies.yaml"


class ServerConfig(TypedDict):
    """Describes a single MCP server entry from the registry."""

    transport: str
    command: str
    args: list[str]
    enabled: bool
    tags: list[str]


@dataclass(frozen=True)
class GatewayConfig:
    """Holds the resolved registry paths for the MCP gateway."""

    servers_path: Path = SERVERS_CONFIG
    policies_path: Path = POLICIES_CONFIG


def allowed_servers(
    agent_name: str,
    server_registry: Mapping[str, ServerConfig],
    policy_registry: Mapping[str, Collection[str]],
) -> dict[str, ServerConfig]:
    """Filters the server registry to the servers allowed for an agent."""

    allowed = set(policy_registry.get(agent_name, ()))
    return {
        server_name: config
        for server_name, config in server_registry.items()
        if server_name in allowed
    }
