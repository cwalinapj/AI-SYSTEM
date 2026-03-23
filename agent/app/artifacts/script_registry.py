from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from app.artifacts.s3 import checksum, upload_bytes, upload_text
from app.db import acquire


async def register_script(
    project_id: UUID,
    script_name: str,
    language: str,
    content: bytes,
    generated_from: dict[str, Any] | None = None,
    namespace: str = "global",
) -> dict[str, Any]:
    """
    Upload a script to MinIO and register it in Postgres.
    Returns metadata dict with artifact_id, version, uri.
    """
    async with acquire() as conn:
        # Find next version number
        row = await conn.fetchrow(
            "select coalesce(max(version), 0) + 1 as next_version from script_versions where project_id = $1 and script_name = $2",
            project_id,
            script_name,
        )
        version = row["next_version"]

        ext = {"bash": "sh", "python": "py", "make": "mk"}.get(language, "sh")
        key = f"projects/{project_id}/scripts/{script_name}/{version}/script.{ext}"
        cs = checksum(content)
        uri = upload_bytes(key, content, content_type="text/plain")

        # Upload metadata JSON
        meta = {
            "script_name": script_name,
            "language": language,
            "version": version,
            "checksum": cs,
            "generated_from": generated_from,
        }
        meta_key = f"projects/{project_id}/scripts/{script_name}/{version}/metadata.json"
        upload_text(meta_key, json.dumps(meta, indent=2))

        # Persist artifact record
        artifact_row = await conn.fetchrow(
            """
            insert into artifacts (project_id, namespace, artifact_type, title, uri, checksum, metadata)
            values ($1, $2, 'script', $3, $4, $5, $6::jsonb)
            returning id
            """,
            project_id,
            namespace,
            script_name,
            uri,
            cs,
            json.dumps(meta),
        )
        artifact_id = artifact_row["id"]

        # Persist script_version record
        sv_row = await conn.fetchrow(
            """
            insert into script_versions
              (project_id, script_name, version, language, artifact_id, generated_from, validation_status)
            values ($1, $2, $3, $4, $5, $6::jsonb, 'pending')
            returning id
            """,
            project_id,
            script_name,
            version,
            language,
            artifact_id,
            json.dumps(generated_from) if generated_from else "{}",
        )

    return {
        "script_version_id": str(sv_row["id"]),
        "artifact_id": str(artifact_id),
        "version": version,
        "uri": uri,
        "checksum": cs,
    }


async def get_script_versions(project_id: UUID, script_name: str) -> list[dict[str, Any]]:
    """Return all versions of a named script for a project."""
    async with acquire() as conn:
        rows = await conn.fetch(
            "select * from script_versions where project_id = $1 and script_name = $2 order by version desc",
            project_id,
            script_name,
        )
    return [dict(r) for r in rows]
