from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID

from app.knowledge.chunking import chunk_text
from app.knowledge.tagging import tag_content
from app.memory.store import store_memory


async def ingest_file(
    file_path: Path,
    project_id: UUID | None = None,
    namespace: str = "global",
    expert_domain: str = "general",
    source_kind: str = "script",
) -> list[str]:
    """
    Ingest a file into memory: chunk → tag → embed → store.
    Returns list of memory item UUIDs.
    """
    content = file_path.read_text(errors="replace")
    chunks = chunk_text(content)
    ids: list[str] = []

    for i, chunk in enumerate(chunks):
        tags = await tag_content(chunk, expert_domain=expert_domain)
        mem_id = await store_memory(
            namespace=namespace,
            memory_type="semantic",
            title=f"{file_path.name} (chunk {i + 1})",
            summary=chunk[:300],
            content=chunk,
            importance=2,
            tags=tags,
            source_kind=source_kind,
            source_ref=str(file_path),
            expert_domain=expert_domain,
            project_id=project_id,
        )
        ids.append(mem_id)

    return ids


async def ingest_text(
    text: str,
    title: str,
    project_id: UUID | None = None,
    namespace: str = "global",
    memory_type: str = "semantic",
    expert_domain: str = "general",
    source_kind: str = "chat",
    importance: int = 3,
) -> list[str]:
    """
    Ingest arbitrary text into memory.
    Returns list of memory item UUIDs.
    """
    chunks = chunk_text(text)
    ids: list[str] = []

    for i, chunk in enumerate(chunks):
        tags = await tag_content(chunk, expert_domain=expert_domain)
        mem_id = await store_memory(
            namespace=namespace,
            memory_type=memory_type,
            title=f"{title} (chunk {i + 1})" if len(chunks) > 1 else title,
            summary=chunk[:300],
            content=chunk,
            importance=importance,
            tags=tags,
            source_kind=source_kind,
            expert_domain=expert_domain,
            project_id=project_id,
        )
        ids.append(mem_id)

    return ids
