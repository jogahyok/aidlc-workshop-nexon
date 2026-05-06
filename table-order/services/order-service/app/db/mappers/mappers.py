"""쿼리 결과를 도메인 객체로 변환하는 매퍼"""

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_item_option import OrderItemOption
from app.models.order_history import OrderHistory


def map_order(row: tuple) -> Order:
    return Order(
        id=row[0],
        store_id=row[1],
        table_id=row[2],
        session_id=row[3],
        order_number=row[4],
        status=row[5],
        total_amount=row[6],
        created_at=row[7],
        updated_at=row[8],
    )


def map_order_item(row: tuple) -> OrderItem:
    return OrderItem(
        id=row[0],
        order_id=row[1],
        menu_item_id=row[2],
        menu_name=row[3],
        menu_price=row[4],
        quantity=row[5],
        subtotal=row[6],
        created_at=row[7],
    )


def map_order_item_option(row: tuple) -> OrderItemOption:
    return OrderItemOption(
        id=row[0],
        order_item_id=row[1],
        option_item_id=row[2],
        option_name=row[3],
        option_price=row[4],
        created_at=row[5],
    )


def map_order_history(row: tuple) -> OrderHistory:
    return OrderHistory(
        id=row[0],
        original_order_id=row[1],
        store_id=row[2],
        table_id=row[3],
        session_id=row[4],
        order_number=row[5],
        status=row[6],
        total_amount=row[7],
        items_snapshot=row[8],
        ordered_at=row[9],
        archived_at=row[10],
    )
