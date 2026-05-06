from dataclasses import dataclass
from datetime import datetime


@dataclass
class Order:
    id: int
    store_id: int
    table_id: int
    session_id: int
    order_number: str
    status: str  # "pending" | "preparing" | "completed"
    total_amount: int
    created_at: datetime
    updated_at: datetime
