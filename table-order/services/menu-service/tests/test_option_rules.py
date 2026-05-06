"""Property-Based Testing: 옵션 그룹 규칙 검증"""

from hypothesis import given, strategies as st, assume
import pytest


# 옵션 그룹 타입 규칙
class OptionGroupRules:
    @staticmethod
    def validate_group(group_type: str, max_select: int | None) -> dict:
        """옵션 그룹 생성 시 규칙 적용"""
        if group_type == "radio":
            return {
                "type": "radio",
                "is_required": True,
                "max_select": 1,
            }
        elif group_type == "checkbox":
            return {
                "type": "checkbox",
                "is_required": False,
                "max_select": max_select,
            }
        else:
            raise ValueError(f"Invalid type: {group_type}")

    @staticmethod
    def validate_selection(
        group_type: str,
        max_select: int | None,
        selected_count: int,
    ) -> bool:
        """옵션 선택 유효성 검증"""
        if group_type == "radio":
            return selected_count == 1
        elif group_type == "checkbox":
            if selected_count < 0:
                return False
            if max_select is not None and selected_count > max_select:
                return False
            return True
        return False


rules = OptionGroupRules()


# PBT: radio 타입은 항상 is_required=True, max_select=1
@given(max_select=st.integers(min_value=1, max_value=100))
def test_radio_always_required_and_single(max_select: int):
    """radio 타입은 입력 max_select와 무관하게 항상 required=True, max_select=1"""
    result = rules.validate_group("radio", max_select)
    assert result["is_required"] is True
    assert result["max_select"] == 1


# PBT: checkbox 타입은 is_required=False
@given(max_select=st.one_of(st.none(), st.integers(min_value=1, max_value=50)))
def test_checkbox_never_required(max_select: int | None):
    """checkbox 타입은 항상 is_required=False"""
    result = rules.validate_group("checkbox", max_select)
    assert result["is_required"] is False


# PBT: radio 선택은 정확히 1개만 유효
@given(selected=st.integers(min_value=0, max_value=10))
def test_radio_selection_exactly_one(selected: int):
    """radio 타입에서 정확히 1개 선택만 유효"""
    is_valid = rules.validate_selection("radio", 1, selected)
    assert is_valid == (selected == 1)


# PBT: checkbox 선택은 0~max_select 범위만 유효
@given(
    max_select=st.integers(min_value=1, max_value=10),
    selected=st.integers(min_value=0, max_value=15),
)
def test_checkbox_selection_within_max(max_select: int, selected: int):
    """checkbox 타입에서 0~max_select 범위만 유효"""
    is_valid = rules.validate_selection("checkbox", max_select, selected)
    assert is_valid == (0 <= selected <= max_select)


# PBT: checkbox max_select=None이면 모든 양수 선택 유효
@given(selected=st.integers(min_value=0, max_value=1000))
def test_checkbox_unlimited_selection(selected: int):
    """checkbox max_select=None이면 0 이상 모든 선택 유효"""
    is_valid = rules.validate_selection("checkbox", None, selected)
    assert is_valid is True


# PBT: 잘못된 타입은 항상 에러
@given(group_type=st.text(min_size=1, max_size=20).filter(lambda x: x not in ("radio", "checkbox")))
def test_invalid_type_raises_error(group_type: str):
    """유효하지 않은 타입은 항상 ValueError"""
    with pytest.raises(ValueError):
        rules.validate_group(group_type, None)
