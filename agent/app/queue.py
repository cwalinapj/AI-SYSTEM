from __future__ import annotations

import asyncio
import json
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    payload: dict[str, Any] = field(default_factory=dict)
    status: str = "queued"  # queued | running | done | failed
    result: Any = None
    error: str | None = None


class InMemoryQueue:
    """Simple async in-memory task queue (replace with Redis/Postgres queue in production)."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[Task] = asyncio.Queue()
        self._tasks: dict[str, Task] = {}

    async def enqueue(self, payload: dict[str, Any]) -> Task:
        task = Task(payload=payload)
        self._tasks[task.id] = task
        await self._queue.put(task)
        return task

    async def dequeue(self) -> Task:
        task = await self._queue.get()
        task.status = "running"
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def complete(self, task: Task, result: Any) -> None:
        task.status = "done"
        task.result = result

    def fail(self, task: Task, error: str) -> None:
        task.status = "failed"
        task.error = error

    def task_done(self) -> None:
        self._queue.task_done()


# Global singleton queue
_queue: InMemoryQueue | None = None


def get_queue() -> InMemoryQueue:
    global _queue
    if _queue is None:
        _queue = InMemoryQueue()
    return _queue
