from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderItem:
    id: int
    order_id: int
    menu_item_id: int
    menu_name: str
    menu_price: int
    quantity: int
    subtotal: int
    created_at: datetime
