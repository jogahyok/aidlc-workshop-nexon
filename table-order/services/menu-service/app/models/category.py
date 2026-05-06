from dataclasses import dataclass
from datetime import datetime


@dataclass
class Category:
    id: int
    store_id: int
    name: str
    sort_order: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
