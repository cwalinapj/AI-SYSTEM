from __future__ import annotations

from typing import Any
from uuid import UUID

from app.memory.store import search_memory


async def retrieve_context(
    goal: str,
    project_id: UUID | None = None,
    expert_domain: str = "general",
    top_k: int = 5,
) -> dict[str, list[dict[str, Any]]]:
    """
    Assemble working context for a task by fetching relevant memory across
    all three memory types plus domain-specific episodic history.
    """
    semantic = await search_memory(
        query=goal,
        project_id=project_id,
        memory_type="semantic",
        expert_domain=expert_domain,
        top_k=top_k,
    )
    episodic = await search_memory(
        query=goal,
        project_id=project_id,
        memory_type="episodic",
        expert_domain=expert_domain,
        top_k=top_k,
    )
    procedural = await search_memory(
        query=goal,
        project_id=project_id,
        memory_type="procedural",
        expert_domain=expert_domain,
        top_k=top_k,
    )
    return {
        "semantic": semantic,
        "episodic": episodic,
        "procedural": procedural,
    }
