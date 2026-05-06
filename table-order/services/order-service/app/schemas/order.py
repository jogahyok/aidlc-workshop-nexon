from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OrderItemOptionRequest(BaseModel):
    option_item_id: int
    option_name: str
    option_price: int = Field(..., ge=0)


class OrderItemRequest(BaseModel):
    menu_item_id: int
    menu_name: str
    menu_price: int = Field(..., ge=0)
    quantity: int = Field(..., ge=1)
    options: list[OrderItemOptionRequest] = Field(default_factory=list)


class OrderCreateRequest(BaseModel):
    table_id: int
    session_id: int
    items: list[OrderItemRequest] = Field(..., min_length=1)


class OrderStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(pending|preparing|completed)$")


class OrderItemOptionResponse(BaseModel):
    id: int
    order_item_id: int
    option_item_id: int
    option_name: str
    option_price: int
    created_at: datetime


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    menu_item_id: int
    menu_name: str
    menu_price: int
    quantity: int
    subtotal: int
    options: list[OrderItemOptionResponse] = Field(default_factory=list)
    created_at: datetime


class OrderResponse(BaseModel):
    id: int
    store_id: int
    table_id: int
    session_id: int
    order_number: str
    status: str
    total_amount: int
    items: list[OrderItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class OrderHistoryResponse(BaseModel):
    id: int
    original_order_id: int
    store_id: int
    table_id: int
    session_id: int
    order_number: str
    status: str
    total_amount: int
    items_snapshot: str  # JSON
    ordered_at: datetime
    archived_at: datetime


class PaginationMeta(BaseModel):
    page: int
    size: int
    total_items: int
    total_pages: int


class PaginatedOrdersResponse(BaseModel):
    items: list[OrderResponse]
    pagination: PaginationMeta


class PriceMismatchItem(BaseModel):
    menu_id: int
    current_price: int
    submitted_price: int


class PriceMismatchError(BaseModel):
    error: str = "PRICE_MISMATCH"
    message: str = "메뉴 가격이 변경되었습니다. 최신 가격을 확인해 주세요."
    updated_items: list[PriceMismatchItem]


class PendingOrderError(BaseModel):
    error: str = "PENDING_ORDER_EXISTS"
    message: str = "이전 주문이 아직 대기 중입니다."
    existing_order: dict
