from __future__ import annotations

from app.orchestration.graph import GraphState
from app.orchestration.coder import code
from app.orchestration.observer import observe


async def repair(state: GraphState) -> GraphState:
    """
    Attempt to repair a failing implementation.
    Increments repair_attempts; re-runs coding with the error context.
    """
    state.repair_attempts += 1
    # Re-observe to get fresh diagnosis
    state = await observe(state)
    # Re-code with the error in context
    state = await code(state)
    return state


def should_repair(state: GraphState) -> bool:
    """Return True if the repair loop should continue."""
    if state.tests_passed:
        return False
    return state.repair_attempts < state.max_repair_attempts
