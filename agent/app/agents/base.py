from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.memory.retriever import retrieve_context
from app.orchestration.graph import GraphState


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""

    domain: str = "general"
    namespace_prefix: str = "global"

    def __init__(self, project_id: UUID | None = None) -> None:
        self.project_id = project_id

    @abstractmethod
    async def run(self, goal: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute the agent's primary task and return a result dict."""
        ...

    async def load_context(self, goal: str) -> dict[str, Any]:
        """Load memory context relevant to the goal."""
        return await retrieve_context(
            goal=goal,
            project_id=self.project_id,
            expert_domain=self.domain,
        )

    def namespace(self, project_name: str = "") -> str:
        if project_name:
            return f"project/{project_name}/{self.domain}"
        return f"{self.namespace_prefix}/{self.domain}"
