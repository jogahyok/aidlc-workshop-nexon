from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MenuItemCreate(BaseModel):
    category_id: int
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: int = Field(..., ge=0)
    image_url: Optional[str] = None
    sort_order: Optional[int] = None  # None이면 마지막에 추가


class MenuItemUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None


class MenuItemResponse(BaseModel):
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


class MenuItemMoveRequest(BaseModel):
    direction: str = Field(..., pattern="^(up|down)$")


class ImageUploadRequest(BaseModel):
    content_type: str = Field(..., pattern="^image/(jpeg|png|webp)$")


class ImageUploadResponse(BaseModel):
    presigned_url: str
    image_key: str
