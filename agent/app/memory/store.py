from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from app.db import acquire
from app.llm.model_router import get_router


async def embed_text(text: str) -> list[float]:
    """Return embedding vector for the given text."""
    router = get_router()
    return await router.embed(text)


async def store_memory(
    namespace: str,
    memory_type: str,
    title: str,
    summary: str,
    content: str | None = None,
    importance: int = 3,
    tags: list[str] | None = None,
    source_kind: str | None = None,
    source_ref: str | None = None,
    expert_domain: str = "general",
    project_id: UUID | None = None,
) -> str:
    """Embed and store a memory item, returning its UUID."""
    vector = await embed_text(summary)
    vector_str = "[" + ",".join(str(v) for v in vector) + "]"

    async with acquire() as conn:
        row = await conn.fetchrow(
            """
            insert into memory_items
              (project_id, namespace, memory_type, title, summary, content,
               importance, tags, source_kind, source_ref, expert_domain, embedding)
            values ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10, $11, $12::vector)
            returning id
            """,
            project_id,
            namespace,
            memory_type,
            title,
            summary,
            content,
            importance,
            json.dumps(tags or []),
            source_kind,
            source_ref,
            expert_domain,
            vector_str,
        )
    return str(row["id"])


async def search_memory(
    query: str,
    project_id: UUID | None = None,
    namespace: str | None = None,
    memory_type: str | None = None,
    expert_domain: str | None = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Semantic search over memory items using cosine similarity."""
    vector = await embed_text(query)
    vector_str = "[" + ",".join(str(v) for v in vector) + "]"

    conditions = ["true"]
    params: list[Any] = [vector_str, top_k]
    idx = 3

    if project_id is not None:
        conditions.append(f"project_id = ${idx}")
        params.append(project_id)
        idx += 1
    if namespace is not None:
        conditions.append(f"namespace = ${idx}")
        params.append(namespace)
        idx += 1
    if memory_type is not None:
        conditions.append(f"memory_type = ${idx}")
        params.append(memory_type)
        idx += 1
    if expert_domain is not None:
        conditions.append(f"expert_domain = ${idx}")
        params.append(expert_domain)
        idx += 1

    where_clause = " and ".join(conditions)
    sql = f"""
        select id, namespace, memory_type, title, summary, importance,
               tags, expert_domain, created_at,
               1 - (embedding <=> $1::vector) as score
        from memory_items
        where embedding is not null and {where_clause}
        order by score desc
        limit $2
    """

    async with acquire() as conn:
        rows = await conn.fetch(sql, *params)

    return [dict(r) for r in rows]
