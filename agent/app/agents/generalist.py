from __future__ import annotations

import uuid
from typing import Any
from uuid import UUID

from app.agents.base import BaseAgent
from app.memory.judge import judge
from app.memory.retriever import retrieve_context
from app.memory.writer import write_memory
from app.orchestration.coder import code
from app.orchestration.graph import GraphState
from app.orchestration.observer import observe
from app.orchestration.planner import plan
from app.orchestration.repair_loop import repair, should_repair


class GeneralistAgent(BaseAgent):
    """
    General-purpose coding agent.
    Implements the main loop: inspect → plan → code → test → repair → summarize.
    """

    domain: str = "general"

    async def run(
        self,
        goal: str,
        context: dict[str, Any] | None = None,
        repo_path: str = "/workspace",
    ) -> dict[str, Any]:
        session_id = str(uuid.uuid4())
        memory_context = context or await self.load_context(goal)

        state = GraphState(
            session_id=session_id,
            project_id=self.project_id or UUID(int=0),
            goal=goal,
            repo_path=repo_path,
            expert_domain=self.domain,
            context=memory_context,
        )

        # Plan
        state = await plan(state)

        # Code
        state = await code(state)

        # Repair loop (no actual test runner wired here; subclasses can override)
        while should_repair(state):
            state = await repair(state)

        # Memory judgment
        judgment = await judge(
            goal=goal,
            project=str(self.project_id),
            commands_run=state.commands_run,
            diffs=state.diffs,
            tests_passed=state.tests_passed,
            error_class=state.error_class,
            novel=state.repair_attempts == 0,
            content="\n".join(state.code_changes[-1:]),
        )
        state.memory_judgment = judgment

        # Persist memory if judge approves
        await write_memory(
            event={**judgment, "source_kind": "chat", "source_ref": session_id},
            project_id=self.project_id,
            namespace=self.namespace(),
        )

        return {
            "session_id": session_id,
            "goal": goal,
            "success": state.success,
            "plan": state.plan,
            "code_changes": state.code_changes,
            "diffs": state.diffs,
            "commands_run": state.commands_run,
            "tests_passed": state.tests_passed,
            "error_class": state.error_class,
            "memory_judgment": judgment,
            "summary": state.summary,
        }
