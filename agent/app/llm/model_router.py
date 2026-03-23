from __future__ import annotations

from enum import Enum
from typing import Any

from app.config import get_settings
from app.llm.openrouter_client import OpenRouterClient


class ModelTier(str, Enum):
    STRONG = "strong"   # coding, repair, architecture, expert tasks
    CHEAP = "cheap"     # memory judge, tagging, classification
    EMBED = "embed"     # embeddings only


class ModelRouter:
    """Routes LLM calls to the appropriate model based on task tier."""

    def __init__(self, client: OpenRouterClient | None = None) -> None:
        self._client = client or OpenRouterClient()
        self._settings = get_settings()

    def _model_for_tier(self, tier: ModelTier) -> str:
        if tier == ModelTier.STRONG:
            return self._settings.strong_model
        if tier == ModelTier.CHEAP:
            return self._settings.cheap_model
        return self._settings.embedding_model

    async def chat(
        self,
        tier: ModelTier,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        model = self._model_for_tier(tier)
        return await self._client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

    async def embed(self, text: str) -> list[float]:
        return await self._client.embed(text)


_router: ModelRouter | None = None


def get_router() -> ModelRouter:
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router
