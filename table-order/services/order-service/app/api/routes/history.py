"""주문 이력 API 라우트"""

import math
from typing import Optional

from fastapi import APIRouter, Query

from app.schemas.order import (
    OrderHistoryResponse,
    PaginationMeta,
)
from app.services.order_service import OrderService

router = APIRouter()
service = OrderService()


@router.get("/stores/{store_id}/tables/{table_id}/history")
async def get_order_history(
    store_id: int,
    table_id: int,
    date_from: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    histories, total = await service.get_order_history(
        store_id, table_id, date_from, date_to, page, size
    )
    total_pages = math.ceil(total / size) if total > 0 else 0

    return {
        "items": [
            OrderHistoryResponse(**h.__dict__) for h in histories
        ],
        "pagination": PaginationMeta(
            page=page,
            size=size,
            total_items=total,
            total_pages=total_pages,
        ),
    }
