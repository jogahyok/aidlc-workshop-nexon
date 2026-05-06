"""테스트 설정"""

import pytest


@pytest.fixture
def sample_order_request():
    return {
        "table_id": 3,
        "session_id": 100,
        "items": [
            {
                "menu_item_id": 1,
                "menu_name": "아메리카노",
                "menu_price": 4500,
                "quantity": 2,
                "options": [
                    {
                        "option_item_id": 1,
                        "option_name": "라지",
                        "option_price": 500,
                    }
                ],
            },
            {
                "menu_item_id": 2,
                "menu_name": "카페라떼",
                "menu_price": 5500,
                "quantity": 1,
                "options": [],
            },
        ],
    }


@pytest.fixture
def sample_order_total():
    """
    아메리카노: (4500 + 500) × 2 = 10000
    카페라떼: (5500 + 0) × 1 = 5500
    총액: 15500
    """
    return 15500
