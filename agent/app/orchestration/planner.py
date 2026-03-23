from __future__ import annotations

import json
from pathlib import Path

from app.llm.model_router import ModelTier, get_router
from app.orchestration.graph import GraphState

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "planner.md"


async def plan(state: GraphState) -> GraphState:
    """
    Generate a step-by-step plan for achieving the goal.
    Updates state.plan in-place.
    """
    system_prompt = _PROMPT_PATH.read_text() if _PROMPT_PATH.exists() else _FALLBACK_PROMPT

    context_summary = json.dumps(
        {
            "goal": state.goal,
            "semantic_memory": state.context.get("semantic", [])[:3],
            "procedural_memory": state.context.get("procedural", [])[:3],
        },
        indent=2,
    )

    router = get_router()
    raw = await router.chat(
        tier=ModelTier.STRONG,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_summary},
        ],
        response_format={"type": "json_object"},
    )

    try:
        data = json.loads(raw)
        state.plan = data.get("steps", [])
    except json.JSONDecodeError:
        state.plan = [raw]

    return state


_FALLBACK_PROMPT = """
You are a coding task planner.
Given a goal and context, produce a numbered list of concrete implementation steps.
Return JSON: {"steps": ["step 1", "step 2", ...]}
Be specific. Steps should be small and verifiable.
"""
