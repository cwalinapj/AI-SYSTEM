from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.agents import DOMAIN_AGENT_MAP, get_agent_for_domain

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list)
async def list_agents() -> list[dict[str, Any]]:
    """List available agent domains."""
    return [
        {"domain": domain, "agent_class": cls.__name__}
        for domain, cls in DOMAIN_AGENT_MAP.items()
    ]


@router.post("/{domain}/run", response_model=dict)
async def run_agent(
    domain: str,
    goal: str,
    project_id: UUID | None = None,
    repo_path: str = "/workspace",
) -> dict[str, Any]:
    """Directly invoke an agent for a goal (synchronous; use /tasks for async)."""
    agent_class = get_agent_for_domain(domain)
    agent = agent_class(project_id=project_id)
    result = await agent.run(goal=goal, repo_path=repo_path)
    return result
