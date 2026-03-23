from __future__ import annotations

from app.llm.model_router import get_router


async def embed(text: str) -> list[float]:
    """Return an embedding vector for the given text using the configured embedding model."""
    router = get_router()
    return await router.embed(text)
