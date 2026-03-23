from __future__ import annotations

import json
from pathlib import Path

from app.execution.git_ops import git_diff
from app.llm.model_router import ModelTier, get_router
from app.orchestration.graph import GraphState

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "coder.md"


async def code(state: GraphState) -> GraphState:
    """
    Generate and apply code changes for the current plan step.
    Produces a unified diff that is stored in state.diffs.
    """
    system_prompt = _PROMPT_PATH.read_text() if _PROMPT_PATH.exists() else _FALLBACK_PROMPT

    user_msg = json.dumps(
        {
            "goal": state.goal,
            "plan": state.plan,
            "repo_path": state.repo_path,
            "previous_diffs": state.diffs[-2:] if state.diffs else [],
            "last_error": state.last_error or None,
        },
        indent=2,
    )

    router = get_router()
    raw = await router.chat(
        tier=ModelTier.STRONG,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
    )

    state.code_changes.append(raw)
    return state


_FALLBACK_PROMPT = """
You are an expert software engineer.
Given a goal, plan, and context, produce the minimal code changes needed.
Respond with a unified diff (--- a/file +++ b/file format).
If no file changes are needed, explain what shell command to run instead.
"""
