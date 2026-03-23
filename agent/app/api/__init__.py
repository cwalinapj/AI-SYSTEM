from app.api.routes_tasks import router as tasks_router
from app.api.routes_memory import router as memory_router
from app.api.routes_scripts import router as scripts_router
from app.api.routes_ports import router as ports_router
from app.api.routes_agents import router as agents_router

__all__ = [
    "tasks_router",
    "memory_router",
    "scripts_router",
    "ports_router",
    "agents_router",
]
