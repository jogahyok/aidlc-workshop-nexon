"""테스트 설정"""

import pytest


@pytest.fixture
def sample_menu_data():
    return {
        "category_id": 1,
        "name": "아메리카노",
        "description": "깊고 풍부한 에스프레소",
        "price": 4500,
    }


@pytest.fixture
def sample_option_group_radio():
    return {
        "name": "사이즈",
        "type": "radio",
        "items": [
            {"name": "레귤러", "price": 0},
            {"name": "라지", "price": 500},
        ],
    }


@pytest.fixture
def sample_option_group_checkbox():
    return {
        "name": "토핑",
        "type": "checkbox",
        "max_select": 3,
        "items": [
            {"name": "휘핑크림", "price": 500},
            {"name": "바닐라 시럽", "price": 300},
            {"name": "카라멜 시럽", "price": 300},
            {"name": "초코 시럽", "price": 300},
        ],
    }
