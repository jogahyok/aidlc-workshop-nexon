from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MenuItem:
    id: int
    store_id: int
    category_id: int
    name: str
    description: Optional[str]
    price: int
    image_url: Optional[str]
    sort_order: int
    is_deleted: bool
    has_options: bool
    created_at: datetime
    updated_at: datetime
