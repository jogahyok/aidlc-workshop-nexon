from dataclasses import dataclass
from datetime import datetime


@dataclass
class Admin:
    id: int
    store_id: int
    username: str
    password_hash: str
    created_at: datetime
    updated_at: datetime
