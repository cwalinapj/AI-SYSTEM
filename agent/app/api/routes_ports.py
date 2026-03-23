from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.agents.port_manager import PortManagerAgent
from app.db import acquire
from app.models import ReservePortRequest

router = APIRouter(prefix="/ports", tags=["ports"])

_manager = PortManagerAgent()


@router.post("/reserve", response_model=dict)
async def reserve_port(req: ReservePortRequest) -> dict[str, Any]:
    """Reserve a port lease for a service."""
    result = await _manager.reserve_port(
        service_name=req.service_name,
        host_name=req.host_name,
        protocol=req.protocol,
        preferred_range=req.preferred_range,
        preferred_port=req.preferred_port,
        owner_agent=req.owner_agent,
    )
    if not result.get("success"):
        raise HTTPException(status_code=409, detail=result.get("error", "Port allocation failed"))
    return result


@router.delete("/leases/{lease_id}", response_model=dict)
async def release_port(lease_id: str) -> dict[str, Any]:
    """Release a port lease."""
    released = await _manager.release_port(lease_id)
    if not released:
        raise HTTPException(status_code=404, detail="Lease not found")
    return {"released": True, "lease_id": lease_id}


@router.put("/leases/{lease_id}/heartbeat", response_model=dict)
async def heartbeat(lease_id: str) -> dict[str, Any]:
    """Update lease heartbeat to keep it active."""
    updated = await _manager.heartbeat(lease_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Lease not found")
    return {"updated": True, "lease_id": lease_id}


@router.post("/reconcile", response_model=dict)
async def reconcile(host_name: str = "localhost") -> dict[str, Any]:
    """Reconcile DB leases vs actual listeners."""
    return await _manager.reconcile(host_name=host_name)


@router.get("/leases", response_model=list)
async def list_leases(status: str | None = None) -> list[dict[str, Any]]:
    """List all port leases, optionally filtered by status."""
    async with acquire() as conn:
        if status:
            rows = await conn.fetch(
                "select * from port_leases where status = $1 order by created_at desc", status
            )
        else:
            rows = await conn.fetch("select * from port_leases order by created_at desc")
    return [dict(r) for r in rows]
