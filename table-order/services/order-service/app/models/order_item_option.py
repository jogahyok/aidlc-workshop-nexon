from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderItemOption:
    id: int
    order_item_id: int
    option_item_id: int
    option_name: str
    option_price: int
    created_at: datetime
