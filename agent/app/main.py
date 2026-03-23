from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import (
    agents_router,
    memory_router,
    ports_router,
    scripts_router,
    tasks_router,
)
from app.db import close_pool, get_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    yield
    await close_pool()


app = FastAPI(
    title="AI Agent System API",
    description="Agent Runtime, Unified Memory, Artifact Storage, Port Management, and Expert Agents",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(tasks_router)
app.include_router(memory_router)
app.include_router(scripts_router)
app.include_router(ports_router)
app.include_router(agents_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
