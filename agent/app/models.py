from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class Project(BaseModel):
    id: UUID
    name: str
    root_path: str | None = None
    created_at: datetime


class MemoryItem(BaseModel):
    id: UUID
    project_id: UUID | None = None
    namespace: str
    memory_type: str  # semantic | episodic | procedural
    title: str
    summary: str
    content: str | None = None
    importance: int = 3
    tags: list[str] = Field(default_factory=list)
    source_kind: str | None = None
    source_ref: str | None = None
    expert_domain: str = "general"
    created_at: datetime
    last_used_at: datetime | None = None
    use_count: int = 0


class Artifact(BaseModel):
    id: UUID
    project_id: UUID | None = None
    namespace: str
    artifact_type: str  # script | log | diff | bundle | report | snapshot
    title: str
    uri: str
    checksum: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ScriptVersion(BaseModel):
    id: UUID
    project_id: UUID | None = None
    script_name: str
    version: int
    language: str  # bash | python | make
    artifact_id: UUID | None = None
    generated_from: dict[str, Any] | None = None
    validation_status: str  # pending | passed | failed
    created_at: datetime


class PortLease(BaseModel):
    id: UUID
    service_name: str
    host_name: str
    protocol: str = "tcp"
    requested_port: int | None = None
    assigned_port: int
    port_range: str | None = None
    owner_agent: str | None = None
    status: str  # reserved | active | stale | conflict | released
    metadata: dict[str, Any] = Field(default_factory=dict)
    heartbeat_at: datetime | None = None
    created_at: datetime


# ---- Request / response schemas ----

class CreateTaskRequest(BaseModel):
    project_id: UUID
    goal: str
    context: str = ""
    expert_domain: str = "general"


class TaskResult(BaseModel):
    session_id: str
    goal: str
    success: bool
    summary: str
    diffs: list[str] = Field(default_factory=list)
    commands_run: list[str] = Field(default_factory=list)
    tests_passed: bool | None = None
    error_class: str | None = None


class ReservePortRequest(BaseModel):
    service_name: str
    host_name: str = "localhost"
    protocol: str = "tcp"
    preferred_range: str = "apis"
    preferred_port: int | None = None
    owner_agent: str | None = None


class MemorySearchRequest(BaseModel):
    query: str
    project_id: UUID | None = None
    namespace: str | None = None
    memory_type: str | None = None
    expert_domain: str | None = None
    top_k: int = 5
