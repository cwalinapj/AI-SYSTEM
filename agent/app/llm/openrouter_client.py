from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings


class OpenRouterClient:
    """Async client for the OpenRouter Responses API."""

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.openrouter_base_url.rstrip("/")
        self._api_key = settings.openrouter_api_key
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        """Send a chat completion request and return the assistant message text."""
        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            body["response_format"] = response_format

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers,
                json=body,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        """Get an embedding vector for the given text."""
        settings = get_settings()
        embed_model = model or settings.embedding_model
        body = {"model": embed_model, "input": text}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self._base_url}/embeddings",
                headers=self._headers,
                json=body,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
