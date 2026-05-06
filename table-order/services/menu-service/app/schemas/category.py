from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    sort_order: Optional[int] = None  # None이면 마지막에 추가


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    sort_order: Optional[int] = None


class CategoryResponse(BaseModel):
    id: int
    store_id: int
    name: str
    sort_order: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class CategoryMoveRequest(BaseModel):
    direction: str = Field(..., pattern="^(up|down)$")
