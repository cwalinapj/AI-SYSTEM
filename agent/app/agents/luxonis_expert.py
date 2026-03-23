from __future__ import annotations

from pathlib import Path
from typing import Any

from app.agents.generalist import GeneralistAgent
from app.llm.model_router import ModelTier, get_router

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "luxonis_expert.md"


class LuxonisExpertAgent(GeneralistAgent):
    """
    Luxonis / DepthAI specialist agent.
    Focuses on device connectivity, camera pipelines, sensor throughput,
    firmware compatibility, and deployment/debugging.
    """

    domain: str = "luxonis"

    async def run(self, goal: str, context: dict[str, Any] | None = None, repo_path: str = "/workspace") -> dict[str, Any]:
        context = context or await self.load_context(goal)
        # Inject domain system prompt into context
        context["domain_prompt"] = _PROMPT_PATH.read_text() if _PROMPT_PATH.exists() else ""
        return await super().run(goal=goal, context=context, repo_path=repo_path)
