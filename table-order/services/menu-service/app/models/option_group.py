from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class OptionGroup:
    id: int
    menu_item_id: int
    name: str
    type: str  # "radio" | "checkbox"
    is_required: bool
    max_select: Optional[int]
    sort_order: int
    created_at: datetime
    updated_at: datetime
