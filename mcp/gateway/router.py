"""Minimal routing helpers for the MCP gateway layer."""

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


REGISTRY_DIR = Path(__file__).resolve().parents[1] / "registry"
SERVERS_CONFIG = REGISTRY_DIR / "servers.yaml"
POLICIES_CONFIG = REGISTRY_DIR / "policies.yaml"


@dataclass(frozen=True)
class GatewayConfig:
    """Holds the resolved registry paths for the MCP gateway."""

    servers_path: Path = SERVERS_CONFIG
    policies_path: Path = POLICIES_CONFIG


def allowed_servers(
    agent_name: str,
    server_registry: Mapping[str, object],
    policy_registry: Mapping[str, list[str]],
) -> dict[str, object]:
    """Filters the server registry to the servers allowed for an agent."""

    allowed = set(policy_registry.get(agent_name, ()))
    return {
        server_name: config
        for server_name, config in server_registry.items()
        if server_name in allowed
    }
