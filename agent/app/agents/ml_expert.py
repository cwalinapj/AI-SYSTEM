from __future__ import annotations

from pathlib import Path
from typing import Any

from app.agents.generalist import GeneralistAgent

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "ml_expert.md"


class MLExpertAgent(GeneralistAgent):
    """
    Machine learning specialist agent.
    Focuses on training runs, dataset prep, evaluation,
    CUDA/PyTorch issues, and model packaging.
    """

    domain: str = "ml"

    async def run(self, goal: str, context: dict[str, Any] | None = None, repo_path: str = "/workspace") -> dict[str, Any]:
        context = context or await self.load_context(goal)
        context["domain_prompt"] = _PROMPT_PATH.read_text() if _PROMPT_PATH.exists() else ""
        return await super().run(goal=goal, context=context, repo_path=repo_path)
