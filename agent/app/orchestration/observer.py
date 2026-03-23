from __future__ import annotations

import json
from pathlib import Path

from app.llm.model_router import ModelTier, get_router
from app.orchestration.graph import GraphState

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "observer.md"


async def observe(state: GraphState) -> GraphState:
    """
    Inspect test/execution output and classify errors.
    Updates state.error_class and state.last_error.
    """
    system_prompt = _PROMPT_PATH.read_text() if _PROMPT_PATH.exists() else _FALLBACK_PROMPT

    user_msg = json.dumps(
        {
            "goal": state.goal,
            "test_output": state.test_output[-3000:] if state.test_output else "",
            "tests_passed": state.tests_passed,
            "commands_run": state.commands_run[-5:],
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
        response_format={"type": "json_object"},
    )

    try:
        data = json.loads(raw)
        state.error_class = data.get("error_class")
        state.last_error = data.get("diagnosis", "")
    except json.JSONDecodeError:
        state.last_error = raw

    return state


_FALLBACK_PROMPT = """
You are a code observer.
Analyze test output and classify the failure.
Return JSON: {"error_class": "...", "diagnosis": "...", "suggested_fix": "..."}
Error classes: syntax_error | import_error | logic_error | config_error | test_failure | timeout | unknown
"""
