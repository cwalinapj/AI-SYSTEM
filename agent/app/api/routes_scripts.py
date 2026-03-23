from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, UploadFile

from app.artifacts.script_registry import get_script_versions, register_script

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.post("/{project_id}/{script_name}", response_model=dict)
async def upload_script(
    project_id: UUID,
    script_name: str,
    file: UploadFile,
    language: str = "bash",
) -> dict[str, Any]:
    """Upload and register a new script version."""
    content = await file.read()
    result = await register_script(
        project_id=project_id,
        script_name=script_name,
        language=language,
        content=content,
    )
    return result


@router.get("/{project_id}/{script_name}", response_model=list)
async def list_script_versions(
    project_id: UUID,
    script_name: str,
) -> list[dict[str, Any]]:
    """List all versions of a script."""
    return await get_script_versions(project_id, script_name)
