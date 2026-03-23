from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass
class GraphState:
    """Shared state that flows through the orchestration graph."""
    session_id: str
    project_id: UUID
    goal: str
    repo_path: str
    expert_domain: str = "general"

    # Context assembled from memory
    context: dict[str, Any] = field(default_factory=dict)

    # Execution history
    plan: list[str] = field(default_factory=list)
    code_changes: list[str] = field(default_factory=list)
    commands_run: list[str] = field(default_factory=list)
    diffs: list[str] = field(default_factory=list)

    # Test results
    tests_passed: bool | None = None
    test_output: str = ""

    # Repair tracking
    repair_attempts: int = 0
    max_repair_attempts: int = 3
    error_class: str | None = None
    last_error: str = ""

    # Outcome
    success: bool = False
    summary: str = ""
    memory_judgment: dict[str, Any] = field(default_factory=dict)
