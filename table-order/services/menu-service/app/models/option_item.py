from dataclasses import dataclass
from datetime import datetime


@dataclass
class OptionItem:
    id: int
    option_group_id: int
    name: str
    price: int
    sort_order: int
    created_at: datetime
    updated_at: datetime
