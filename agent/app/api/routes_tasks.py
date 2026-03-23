from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.agents import get_agent_for_domain
from app.models import CreateTaskRequest, TaskResult
from app.queue import get_queue

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=dict)
async def create_task(req: CreateTaskRequest) -> dict[str, Any]:
    """Enqueue a new coding task."""
    queue = get_queue()
    task = await queue.enqueue(
        {
            "goal": req.goal,
            "project_id": str(req.project_id),
            "context": req.context,
            "expert_domain": req.expert_domain,
        }
    )
    return {"task_id": task.id, "status": task.status}


@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: str) -> dict[str, Any]:
    """Get the status and result of a task."""
    queue = get_queue()
    task = queue.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result,
        "error": task.error,
    }
