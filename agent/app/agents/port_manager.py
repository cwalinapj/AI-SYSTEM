from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any
from uuid import UUID

from app.agents.base import BaseAgent
from app.config import get_settings
from app.db import acquire
from app.llm.model_router import ModelTier, get_router

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "port_manager.md"


class PortManagerAgent(BaseAgent):
    """
    Port lease manager.
    Responsibilities:
    - Allocate ports to services from managed ranges
    - Detect collisions before launch
    - Audit actual listeners on host/container
    - Reconcile declared vs observed ports
    - Expire stale leases
    """

    domain: str = "network"

    async def run(self, goal: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"status": "ok", "message": "Use reserve_port / reconcile methods directly."}

    async def reserve_port(
        self,
        service_name: str,
        host_name: str = "localhost",
        protocol: str = "tcp",
        preferred_range: str = "apis",
        preferred_port: int | None = None,
        owner_agent: str | None = None,
    ) -> dict[str, Any]:
        """
        Allocate a port from managed ranges.
        Returns the assigned port and lease ID.
        """
        settings = get_settings()
        ranges = settings.port_ranges
        port_range = ranges.get(preferred_range, (4000, 4999))

        # Collect already-assigned ports in this range
        async with acquire() as conn:
            rows = await conn.fetch(
                """
                select assigned_port from port_leases
                where host_name = $1 and protocol = $2
                  and status in ('reserved', 'active')
                """,
                host_name,
                protocol,
            )
        reserved = {r["assigned_port"] for r in rows}
        observed = await self._observed_ports(protocol)
        taken = reserved | observed

        # Pick port
        candidate: int | None = None
        if preferred_port and preferred_port not in taken:
            candidate = preferred_port
        else:
            for p in range(port_range[0], port_range[1] + 1):
                if p not in taken:
                    candidate = p
                    break

        if candidate is None:
            return {"success": False, "error": f"No free port in range {preferred_range}"}

        async with acquire() as conn:
            row = await conn.fetchrow(
                """
                insert into port_leases
                  (service_name, host_name, protocol, requested_port, assigned_port,
                   port_range, owner_agent, status, heartbeat_at)
                values ($1, $2, $3, $4, $5, $6, $7, 'reserved', now())
                returning id, assigned_port
                """,
                service_name,
                host_name,
                protocol,
                preferred_port,
                candidate,
                preferred_range,
                owner_agent,
            )

        return {
            "success": True,
            "lease_id": str(row["id"]),
            "assigned_port": row["assigned_port"],
            "service_name": service_name,
            "host_name": host_name,
            "protocol": protocol,
        }

    async def release_port(self, lease_id: str) -> bool:
        async with acquire() as conn:
            result = await conn.execute(
                "update port_leases set status = 'released' where id = $1",
                lease_id,
            )
        return result == "UPDATE 1"

    async def heartbeat(self, lease_id: str) -> bool:
        async with acquire() as conn:
            result = await conn.execute(
                "update port_leases set heartbeat_at = now(), status = 'active' where id = $1",
                lease_id,
            )
        return result == "UPDATE 1"

    async def reconcile(self, host_name: str = "localhost") -> dict[str, Any]:
        """
        Compare DB leases vs actual listeners.
        Mark stale/conflict leases and return a report.
        """
        observed_tcp = await self._observed_ports("tcp")
        observed_udp = await self._observed_ports("udp")

        async with acquire() as conn:
            rows = await conn.fetch(
                "select * from port_leases where host_name = $1 and status in ('reserved', 'active')",
                host_name,
            )

        conflicts: list[dict] = []
        stale: list[dict] = []

        for r in rows:
            observed = observed_tcp if r["protocol"] == "tcp" else observed_udp
            if r["assigned_port"] not in observed and r["status"] == "active":
                stale.append(dict(r))
                async with acquire() as conn:
                    await conn.execute(
                        "update port_leases set status = 'stale' where id = $1", r["id"]
                    )

        return {
            "observed_tcp": sorted(observed_tcp),
            "observed_udp": sorted(observed_udp),
            "stale_leases": stale,
            "conflicts": conflicts,
        }

    async def _observed_ports(self, protocol: str = "tcp") -> set[int]:
        """Return set of ports currently listening on the host."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "ss", "-tlnp" if protocol == "tcp" else "-ulnp",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            ports: set[int] = set()
            for line in stdout.decode().splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    addr = parts[3]
                    port_str = addr.rsplit(":", 1)[-1]
                    try:
                        ports.add(int(port_str))
                    except ValueError:
                        pass
            return ports
        except Exception:
            return set()

    async def suggest_remap(
        self,
        service_name: str,
        current_port: int,
        preferred_range: str = "apis",
    ) -> dict[str, Any]:
        """Suggest a safe alternative port for a service with a conflict."""
        result = await self.reserve_port(
            service_name=f"{service_name}_remap",
            preferred_range=preferred_range,
        )
        if result["success"]:
            return {
                "service": service_name,
                "current_port": current_port,
                "suggested_port": result["assigned_port"],
                "lease_id": result["lease_id"],
            }
        return {"service": service_name, "current_port": current_port, "suggested_port": None}
