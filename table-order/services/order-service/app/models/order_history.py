from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderHistory:
    id: int
    original_order_id: int
    store_id: int
    table_id: int
    session_id: int
    order_number: str
    status: str
    total_amount: int
    items_snapshot: str  # JSON string
    ordered_at: datetime
    archived_at: datetime
