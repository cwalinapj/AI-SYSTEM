from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from app.agents import get_agent_for_domain
from app.config import get_settings
from app.queue import get_queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")


async def process_task(task) -> None:  # type: ignore[type-arg]
    payload = task.payload
    goal = payload.get("goal", "")
    project_id_str = payload.get("project_id")
    expert_domain = payload.get("expert_domain", "general")
    repo_path = payload.get("repo_path", "/workspace")
    queue = get_queue()

    try:
        project_id = UUID(project_id_str) if project_id_str else None
        agent_class = get_agent_for_domain(expert_domain)
        agent = agent_class(project_id=project_id)
        result = await agent.run(goal=goal, repo_path=repo_path)
        queue.complete(task, result)
        logger.info("Task %s completed: %s", task.id, result.get("success"))
    except Exception as exc:
        logger.exception("Task %s failed: %s", task.id, exc)
        queue.fail(task, str(exc))
    finally:
        queue.task_done()


async def main() -> None:
    settings = get_settings()
    logger.info("Worker started. Poll interval: %ss", settings.task_queue_poll_interval)
    queue = get_queue()

    while True:
        try:
            task = await asyncio.wait_for(
                queue.dequeue(),
                timeout=settings.task_queue_poll_interval,
            )
            asyncio.create_task(process_task(task))
        except asyncio.TimeoutError:
            pass
        except Exception as exc:
            logger.exception("Worker error: %s", exc)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
