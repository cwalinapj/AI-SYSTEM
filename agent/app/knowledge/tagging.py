from __future__ import annotations

import json

from app.llm.model_router import ModelTier, get_router


async def tag_content(text: str, expert_domain: str = "general") -> list[str]:
    """
    Use the cheap model to generate relevant tags for a chunk of text.
    Returns a list of tag strings.
    """
    router = get_router()
    raw = await router.chat(
        tier=ModelTier.CHEAP,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a tagging system. Given a text snippet, return a JSON array of 3-7 "
                    f"relevant lowercase tag strings. Domain context: {expert_domain}. "
                    "Return only the JSON array, no explanation."
                ),
            },
            {"role": "user", "content": text[:800]},
        ],
        max_tokens=128,
        response_format={"type": "json_object"},
    )
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(t) for t in data]
        # Some models wrap in {"tags": [...]}
        for key in ("tags", "keywords", "labels"):
            if key in data and isinstance(data[key], list):
                return [str(t) for t in data[key]]
    except (json.JSONDecodeError, TypeError):
        pass
    return []
