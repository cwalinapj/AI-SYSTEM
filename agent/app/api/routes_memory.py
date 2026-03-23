from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.memory.store import search_memory, store_memory
from app.models import MemorySearchRequest

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/search", response_model=list)
async def search(req: MemorySearchRequest) -> list[dict[str, Any]]:
    """Semantic search over memory items."""
    return await search_memory(
        query=req.query,
        project_id=req.project_id,
        namespace=req.namespace,
        memory_type=req.memory_type,
        expert_domain=req.expert_domain,
        top_k=req.top_k,
    )


@router.post("", response_model=dict)
async def create_memory(
    namespace: str,
    memory_type: str,
    title: str,
    summary: str,
    content: str = "",
    importance: int = 3,
    expert_domain: str = "general",
    project_id: UUID | None = None,
) -> dict[str, Any]:
    """Manually store a memory item."""
    mem_id = await store_memory(
        namespace=namespace,
        memory_type=memory_type,
        title=title,
        summary=summary,
        content=content or None,
        importance=importance,
        expert_domain=expert_domain,
        project_id=project_id,
    )
    return {"id": mem_id}
