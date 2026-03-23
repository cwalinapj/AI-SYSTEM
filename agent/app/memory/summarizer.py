from __future__ import annotations

from app.llm.model_router import ModelTier, get_router


async def summarize(text: str, max_tokens: int = 256) -> str:
    """Produce a concise summary of the given text using the cheap model."""
    router = get_router()
    return await router.chat(
        tier=ModelTier.CHEAP,
        messages=[
            {
                "role": "system",
                "content": "Summarize the following text concisely in plain language. Be brief.",
            },
            {"role": "user", "content": text},
        ],
        max_tokens=max_tokens,
    )
