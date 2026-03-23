"""
Basic unit tests for the AI agent system.
Tests run without requiring live Postgres or MinIO connections.
"""
from __future__ import annotations

import pytest


def test_config_defaults():
    """Settings should load with defaults."""
    from app.config import Settings
    s = Settings(openrouter_api_key="test")
    assert s.cheap_model == "openai/gpt-4o-mini"
    assert s.strong_model == "anthropic/claude-3.5-sonnet"
    assert "apis" in s.port_ranges
    assert s.port_ranges["apis"] == (4000, 4999)


def test_chunking_short_text():
    """Short text should return a single chunk."""
    from app.knowledge.chunking import chunk_text
    text = "Hello, world!"
    chunks = chunk_text(text)
    assert chunks == ["Hello, world!"]


def test_chunking_long_text():
    """Long text should be split into overlapping chunks."""
    from app.knowledge.chunking import chunk_text
    text = "word " * 1000
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 110  # chunk_size + some tolerance


def test_queue_enqueue_dequeue():
    """Queue should enqueue and dequeue tasks."""
    import asyncio
    from app.queue import InMemoryQueue

    queue = InMemoryQueue()

    async def run():
        task = await queue.enqueue({"goal": "test goal"})
        assert task.status == "queued"
        assert task.payload["goal"] == "test goal"

        dequeued = await queue.dequeue()
        assert dequeued.id == task.id
        assert dequeued.status == "running"

        queue.complete(dequeued, {"success": True})
        assert dequeued.status == "done"
        assert dequeued.result["success"] is True

    asyncio.run(run())


def test_queue_fail():
    """Queue should record task failures."""
    import asyncio
    from app.queue import InMemoryQueue

    queue = InMemoryQueue()

    async def run():
        task = await queue.enqueue({"goal": "failing task"})
        t = await queue.dequeue()
        queue.fail(t, "Something went wrong")
        assert t.status == "failed"
        assert t.error == "Something went wrong"

    asyncio.run(run())


def test_agent_domain_map():
    """Agent domain map should include all required agents."""
    from app.agents import DOMAIN_AGENT_MAP, get_agent_for_domain
    from app.agents.generalist import GeneralistAgent
    from app.agents.port_manager import PortManagerAgent
    from app.agents.luxonis_expert import LuxonisExpertAgent
    from app.agents.ml_expert import MLExpertAgent
    from app.agents.devops_expert import DevOpsExpertAgent

    assert "general" in DOMAIN_AGENT_MAP
    assert "network" in DOMAIN_AGENT_MAP
    assert "luxonis" in DOMAIN_AGENT_MAP
    assert "ml" in DOMAIN_AGENT_MAP
    assert "devops" in DOMAIN_AGENT_MAP

    assert get_agent_for_domain("general") is GeneralistAgent
    assert get_agent_for_domain("network") is PortManagerAgent
    assert get_agent_for_domain("luxonis") is LuxonisExpertAgent
    assert get_agent_for_domain("ml") is MLExpertAgent
    assert get_agent_for_domain("devops") is DevOpsExpertAgent

    # Unknown domain falls back to GeneralistAgent
    assert get_agent_for_domain("unknown_domain") is GeneralistAgent


def test_graph_state_defaults():
    """GraphState should initialize with sensible defaults."""
    import uuid
    from app.orchestration.graph import GraphState

    state = GraphState(
        session_id="test-session",
        project_id=uuid.uuid4(),
        goal="Fix the bug",
        repo_path="/workspace",
    )
    assert state.repair_attempts == 0
    assert state.max_repair_attempts == 3
    assert state.success is False
    assert state.expert_domain == "general"


def test_repair_loop_should_repair():
    """should_repair returns False when tests pass or max attempts reached."""
    import uuid
    from app.orchestration.graph import GraphState
    from app.orchestration.repair_loop import should_repair

    state = GraphState(
        session_id="s",
        project_id=uuid.uuid4(),
        goal="goal",
        repo_path="/ws",
    )
    # No tests run yet, no attempts → should repair
    assert should_repair(state) is True

    # Tests passed → no repair needed
    state.tests_passed = True
    assert should_repair(state) is False

    # Max attempts reached
    state.tests_passed = False
    state.repair_attempts = 3
    assert should_repair(state) is False


def test_fastapi_app_routes():
    """FastAPI app should expose all required routes."""
    from app.main import app

    paths = {r.path for r in app.routes}
    assert "/health" in paths
    assert "/tasks" in paths
    assert "/memory/search" in paths
    assert "/ports/reserve" in paths
    assert "/agents" in paths
    assert "/scripts/{project_id}/{script_name}" in paths


def test_port_ranges_no_overlap():
    """Managed port ranges should not overlap."""
    from app.config import Settings
    s = Settings(openrouter_api_key="test")
    ranges = list(s.port_ranges.values())
    for i, (a_start, a_end) in enumerate(ranges):
        for j, (b_start, b_end) in enumerate(ranges):
            if i != j:
                assert a_end < b_start or b_end < a_start, (
                    f"Overlapping ranges: {ranges[i]} and {ranges[j]}"
                )
