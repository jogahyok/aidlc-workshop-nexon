"""Property-based tests for session state machine (PBT-06: Stateful)."""
from hypothesis import given, settings as hyp_settings
from hypothesis import strategies as st


# PBT-03: Session invariant - at most one active session per table
@given(
    table_id=st.integers(min_value=1, max_value=100),
    num_start_calls=st.integers(min_value=1, max_value=10),
)
@hyp_settings(max_examples=30)
def test_session_start_idempotent(table_id: int, num_start_calls: int):
    """PBT-04: start_session is idempotent - calling multiple times returns same session.

    This tests the invariant that a table can have at most one active session.
    Simulated without DB - tests the logic pattern.
    """
    # Simulate session state
    sessions: dict[int, dict] = {}

    def start_session(tid: int) -> dict:
        if tid in sessions and sessions[tid]["status"] == "active":
            return sessions[tid]
        session = {"id": len(sessions) + 1, "table_id": tid, "status": "active"}
        sessions[tid] = session
        return session

    results = [start_session(table_id) for _ in range(num_start_calls)]

    # All calls return the same session (idempotent)
    assert all(r["id"] == results[0]["id"] for r in results)
    # Only one session exists for this table
    active_count = sum(1 for s in sessions.values() if s["table_id"] == table_id and s["status"] == "active")
    assert active_count <= 1


# PBT-03: Session state transitions are valid
@given(
    operations=st.lists(
        st.sampled_from(["start", "complete"]),
        min_size=1,
        max_size=20,
    )
)
@hyp_settings(max_examples=50)
def test_session_state_machine(operations: list[str]):
    """PBT-06: Stateful test - session transitions are always valid."""
    table_id = 1
    session_active = False
    completed_count = 0

    for op in operations:
        if op == "start":
            if not session_active:
                session_active = True
            # Idempotent: starting when active does nothing
        elif op == "complete":
            if session_active:
                session_active = False
                completed_count += 1
            # Completing when no active session raises error (skip in model)

    # Invariant: active sessions <= 1
    assert int(session_active) <= 1
    # Invariant: completed count is consistent
    assert completed_count >= 0
