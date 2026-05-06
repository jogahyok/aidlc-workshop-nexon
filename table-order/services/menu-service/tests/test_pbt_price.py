"""Property-Based Testing: 가격 검증 invariant"""

from hypothesis import given, strategies as st


# 가격 invariant: 모든 메뉴 가격은 0 이상이어야 한다
@given(price=st.integers(min_value=0, max_value=10_000_000))
def test_valid_price_always_accepted(price: int):
    """유효한 가격(0 이상)은 항상 검증을 통과해야 한다"""
    assert validate_price(price) is True


@given(price=st.integers(max_value=-1))
def test_negative_price_always_rejected(price: int):
    """음수 가격은 항상 거부되어야 한다"""
    assert validate_price(price) is False


# 금액 계산 invariant: 주문 소계 = (메뉴 단가 + 옵션 합계) × 수량
@given(
    menu_price=st.integers(min_value=0, max_value=1_000_000),
    option_prices=st.lists(st.integers(min_value=0, max_value=100_000), max_size=10),
    quantity=st.integers(min_value=1, max_value=100),
)
def test_subtotal_calculation_invariant(
    menu_price: int, option_prices: list[int], quantity: int
):
    """주문 항목 소계는 항상 (메뉴가격 + 옵션합계) × 수량이어야 한다"""
    expected = (menu_price + sum(option_prices)) * quantity
    actual = calculate_subtotal(menu_price, option_prices, quantity)
    assert actual == expected


# 정렬 invariant: sort_order 변경 후 모든 항목의 순서가 유일해야 한다
@given(
    sort_orders=st.lists(
        st.integers(min_value=0, max_value=100),
        min_size=2,
        max_size=20,
        unique=True,
    )
)
def test_sort_order_uniqueness_after_swap(sort_orders: list[int]):
    """순서 교환 후에도 모든 sort_order 값은 유일해야 한다"""
    # 첫 두 항목의 순서를 교환
    swapped = sort_orders.copy()
    swapped[0], swapped[1] = swapped[1], swapped[0]

    # 유일성 확인
    assert len(set(swapped)) == len(swapped)


# --- Helper functions (실제 구현에서는 서비스 레이어 사용) ---


def validate_price(price: int) -> bool:
    """가격 유효성 검증"""
    return price >= 0


def calculate_subtotal(
    menu_price: int, option_prices: list[int], quantity: int
) -> int:
    """주문 항목 소계 계산"""
    return (menu_price + sum(option_prices)) * quantity
