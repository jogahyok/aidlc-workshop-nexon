"""Property-Based Testing: 아카이브 무결성 invariant"""

import json
from hypothesis import given, strategies as st


# === 아카이브 무결성 ===

def simulate_archive(orders: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    아카이브 시뮬레이션
    - 입력: 원본 주문 목록
    - 출력: (아카이브된 이력, 남은 원본 주문)
    - 규칙: 모든 주문이 이력으로 이동, 원본은 비어야 함
    """
    archived = []
    for order in orders:
        history_entry = {
            "original_order_id": order["id"],
            "store_id": order["store_id"],
            "table_id": order["table_id"],
            "session_id": order["session_id"],
            "order_number": order["order_number"],
            "status": order["status"],
            "total_amount": order["total_amount"],
            "items_snapshot": json.dumps(order.get("items", [])),
        }
        archived.append(history_entry)

    remaining = []  # 아카이브 후 원본은 비어야 함
    return archived, remaining


order_strategy = st.fixed_dictionaries({
    "id": st.integers(min_value=1, max_value=10000),
    "store_id": st.integers(min_value=1, max_value=100),
    "table_id": st.integers(min_value=1, max_value=50),
    "session_id": st.integers(min_value=1, max_value=10000),
    "order_number": st.from_regex(r"[0-9]{3}", fullmatch=True),
    "status": st.sampled_from(["pending", "preparing", "completed"]),
    "total_amount": st.integers(min_value=0, max_value=10_000_000),
    "items": st.just([]),
})


@given(orders=st.lists(order_strategy, min_size=0, max_size=20))
def test_archive_moves_all_orders(orders: list[dict]):
    """아카이브 후 원본 주문은 비어야 한다"""
    archived, remaining = simulate_archive(orders)
    assert len(remaining) == 0


@given(orders=st.lists(order_strategy, min_size=1, max_size=20))
def test_archive_count_matches_original(orders: list[dict]):
    """아카이브된 이력 수는 원본 주문 수와 동일해야 한다"""
    archived, _ = simulate_archive(orders)
    assert len(archived) == len(orders)


@given(orders=st.lists(order_strategy, min_size=1, max_size=20))
def test_archive_preserves_order_data(orders: list[dict]):
    """아카이브된 이력은 원본 주문의 핵심 데이터를 보존해야 한다"""
    archived, _ = simulate_archive(orders)

    for i, history in enumerate(archived):
        original = orders[i]
        assert history["original_order_id"] == original["id"]
        assert history["store_id"] == original["store_id"]
        assert history["table_id"] == original["table_id"]
        assert history["session_id"] == original["session_id"]
        assert history["order_number"] == original["order_number"]
        assert history["status"] == original["status"]
        assert history["total_amount"] == original["total_amount"]


@given(orders=st.lists(order_strategy, min_size=1, max_size=20))
def test_archive_includes_all_statuses(orders: list[dict]):
    """아카이브는 상태 무관하게 모든 주문을 포함해야 한다"""
    archived, _ = simulate_archive(orders)

    original_ids = {o["id"] for o in orders}
    archived_ids = {h["original_order_id"] for h in archived}
    assert original_ids == archived_ids


@given(orders=st.lists(order_strategy, min_size=1, max_size=20))
def test_archive_items_snapshot_is_valid_json(orders: list[dict]):
    """items_snapshot은 유효한 JSON이어야 한다"""
    archived, _ = simulate_archive(orders)

    for history in archived:
        parsed = json.loads(history["items_snapshot"])
        assert isinstance(parsed, list)
