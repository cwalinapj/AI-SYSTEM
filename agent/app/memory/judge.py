from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.llm.model_router import ModelTier, get_router

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "memory_judge.md"


async def judge(
    goal: str,
    project: str,
    commands_run: list[str],
    diffs: list[str],
    tests_passed: bool | None,
    error_class: str | None,
    novel: bool,
    content: str = "",
) -> dict[str, Any]:
    """
    Run the memory judge to decide whether to store an outcome.
    Uses a cheap model — triage only.
    Returns a parsed JSON dict with the judge's decision.
    """
    system_prompt = _PROMPT_PATH.read_text() if _PROMPT_PATH.exists() else _FALLBACK_PROMPT

    user_msg = json.dumps(
        {
            "goal": goal,
            "project": project,
            "commands_run": commands_run,
            "diffs_summary": diffs[:5],
            "tests_passed": tests_passed,
            "error_class": error_class,
            "novel": novel,
            "content_preview": content[:500],
        },
        indent=2,
    )

    router = get_router()
    raw = await router.chat(
        tier=ModelTier.CHEAP,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
    )

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"store": False, "reason": "parse_error", "raw": raw}


_FALLBACK_PROMPT = """
You are a memory triage system.
Decide whether the event should be stored for future use.
Prefer high precision over high recall.

Return JSON:
{
  "store": true,
  "memory_type": "semantic|episodic|procedural|artifact_only",
  "importance": 1,
  "summary": "",
  "tags": [],
  "script_candidate": false,
  "expert_domain": "general|luxonis|ml|devops|network",
  "reason": ""
}

Store only if one of these is true:
- stable preference or convention
- successful fix likely to recur
- reusable workflow
- important decision
- surprising failure with clear diagnosis
- script-worthy repeated sequence
"""
