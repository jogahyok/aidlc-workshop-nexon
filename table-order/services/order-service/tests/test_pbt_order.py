"""Property-Based Testing: 주문 금액 계산 및 상태 머신 invariant"""

from hypothesis import given, strategies as st, assume
import pytest


# === 금액 계산 invariant ===

def calculate_item_subtotal(menu_price: int, option_prices: list[int], quantity: int) -> int:
    """주문 항목 소계 = (메뉴 단가 + 옵션 합계) × 수량"""
    return (menu_price + sum(option_prices)) * quantity


def calculate_order_total(items: list[dict]) -> int:
    """주문 총액 = Σ(각 항목 소계)"""
    return sum(item["subtotal"] for item in items)


@given(
    menu_price=st.integers(min_value=0, max_value=1_000_000),
    option_prices=st.lists(st.integers(min_value=0, max_value=100_000), max_size=10),
    quantity=st.integers(min_value=1, max_value=99),
)
def test_subtotal_is_nonnegative(menu_price: int, option_prices: list[int], quantity: int):
    """주문 항목 소계는 항상 0 이상이어야 한다"""
    subtotal = calculate_item_subtotal(menu_price, option_prices, quantity)
    assert subtotal >= 0


@given(
    menu_price=st.integers(min_value=0, max_value=1_000_000),
    option_prices=st.lists(st.integers(min_value=0, max_value=100_000), max_size=10),
    quantity=st.integers(min_value=1, max_value=99),
)
def test_subtotal_formula_correct(menu_price: int, option_prices: list[int], quantity: int):
    """소계 = (메뉴가격 + 옵션합계) × 수량"""
    subtotal = calculate_item_subtotal(menu_price, option_prices, quantity)
    expected = (menu_price + sum(option_prices)) * quantity
    assert subtotal == expected


@given(
    items=st.lists(
        st.fixed_dictionaries({
            "subtotal": st.integers(min_value=0, max_value=10_000_000),
        }),
        min_size=1,
        max_size=20,
    )
)
def test_order_total_is_sum_of_subtotals(items: list[dict]):
    """주문 총액은 모든 항목 소계의 합이어야 한다"""
    total = calculate_order_total(items)
    expected = sum(item["subtotal"] for item in items)
    assert total == expected


@given(
    items=st.lists(
        st.fixed_dictionaries({
            "subtotal": st.integers(min_value=0, max_value=10_000_000),
        }),
        min_size=1,
        max_size=20,
    )
)
def test_order_total_nonnegative(items: list[dict]):
    """주문 총액은 항상 0 이상이어야 한다"""
    total = calculate_order_total(items)
    assert total >= 0


# === 상태 머신 invariant (자유 전이) ===

VALID_STATUSES = {"pending", "preparing", "completed"}


class OrderStateMachine:
    """주문 상태 머신 (자유 전이)"""

    def __init__(self):
        self.status = "pending"

    def transition(self, new_status: str) -> bool:
        """상태 전이 시도. 유효한 상태면 True, 아니면 False"""
        if new_status not in VALID_STATUSES:
            return False
        self.status = new_status
        return True

    def is_valid_status(self, status: str) -> bool:
        return status in VALID_STATUSES


@given(new_status=st.sampled_from(list(VALID_STATUSES)))
def test_valid_status_always_accepted(new_status: str):
    """유효한 상태값은 항상 전이 성공"""
    sm = OrderStateMachine()
    assert sm.transition(new_status) is True
    assert sm.status == new_status


@given(
    transitions=st.lists(
        st.sampled_from(list(VALID_STATUSES)),
        min_size=1,
        max_size=50,
    )
)
def test_any_sequence_of_valid_transitions_succeeds(transitions: list[str]):
    """유효한 상태의 어떤 시퀀스든 모두 성공해야 한다 (자유 전이)"""
    sm = OrderStateMachine()
    for status in transitions:
        assert sm.transition(status) is True
    assert sm.status == transitions[-1]


@given(
    invalid_status=st.text(min_size=1, max_size=20).filter(
        lambda x: x not in VALID_STATUSES
    )
)
def test_invalid_status_always_rejected(invalid_status: str):
    """유효하지 않은 상태값은 항상 전이 실패"""
    sm = OrderStateMachine()
    assert sm.transition(invalid_status) is False
    assert sm.status == "pending"  # 상태 변경 없음


@given(new_status=st.sampled_from(list(VALID_STATUSES)))
def test_status_after_transition_is_new_status(new_status: str):
    """전이 후 상태는 항상 새 상태와 동일"""
    sm = OrderStateMachine()
    sm.transition(new_status)
    assert sm.status == new_status


# === 주문 번호 생성 invariant ===

def generate_order_number(last_number: str | None) -> str:
    """당일 일련번호 생성"""
    if last_number is None:
        return "001"
    next_num = int(last_number) + 1
    return str(next_num).zfill(3)


@given(last_num=st.integers(min_value=0, max_value=998))
def test_order_number_increments(last_num: int):
    """주문 번호는 항상 이전 번호 + 1"""
    last_str = str(last_num).zfill(3)
    new_number = generate_order_number(last_str)
    assert int(new_number) == last_num + 1


def test_first_order_number_is_001():
    """첫 주문 번호는 항상 001"""
    assert generate_order_number(None) == "001"


@given(last_num=st.integers(min_value=0, max_value=998))
def test_order_number_is_zero_padded(last_num: int):
    """주문 번호는 최소 3자리 zero-padded"""
    last_str = str(last_num).zfill(3)
    new_number = generate_order_number(last_str)
    assert len(new_number) >= 3
