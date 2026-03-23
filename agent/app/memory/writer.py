from __future__ import annotations

from typing import Any
from uuid import UUID

from app.memory.store import store_memory


async def write_memory(
    event: dict[str, Any],
    project_id: UUID | None = None,
    namespace: str = "global/user",
) -> str | None:
    """
    Persist a memory item if the memory judge decided it should be stored.
    Returns the UUID of the new memory item, or None if not stored.
    """
    if not event.get("store", False):
        return None

    return await store_memory(
        namespace=namespace,
        memory_type=event["memory_type"],
        title=event.get("summary", "")[:120],
        summary=event.get("summary", ""),
        content=event.get("content"),
        importance=event.get("importance", 3),
        tags=event.get("tags", []),
        source_kind=event.get("source_kind"),
        source_ref=event.get("source_ref"),
        expert_domain=event.get("expert_domain", "general"),
        project_id=project_id,
    )
