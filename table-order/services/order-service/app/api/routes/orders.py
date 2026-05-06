"""주문 API 라우트"""

import math
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.schemas.order import (
    OrderCreateRequest,
    OrderResponse,
    OrderStatusUpdateRequest,
    PaginatedOrdersResponse,
    PaginationMeta,
)
from app.services.order_service import (
    BusinessRuleError,
    NotFoundError,
    OrderService,
    PendingOrderExistsError,
    PriceMismatchError,
    ServiceUnavailableError,
)

router = APIRouter()
service = OrderService()


@router.post("/stores/{store_id}/orders", response_model=OrderResponse, status_code=201)
async def create_order(store_id: int, data: OrderCreateRequest):
    try:
        order = await service.create_order(store_id, data)
        return order
    except PriceMismatchError as e:
        return JSONResponse(
            status_code=409,
            content={
                "error": "PRICE_MISMATCH",
                "message": "메뉴 가격이 변경되었습니다. 최신 가격을 확인해 주세요.",
                "updated_items": e.mismatches,
            },
        )
    except PendingOrderExistsError as e:
        return JSONResponse(
            status_code=409,
            content={
                "error": "PENDING_ORDER_EXISTS",
                "message": "이전 주문이 아직 대기 중입니다. 주문이 접수된 후 추가 주문이 가능합니다.",
                "existing_order": e.existing_order,
            },
        )
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ServiceUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/stores/{store_id}/orders", response_model=PaginatedOrdersResponse)
async def list_orders(
    store_id: int,
    status: Optional[str] = Query(None, pattern="^(pending|preparing|completed)$"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    orders, total = await service.list_orders(store_id, status, page, size)
    total_pages = math.ceil(total / size) if total > 0 else 0

    return PaginatedOrdersResponse(
        items=orders,
        pagination=PaginationMeta(
            page=page,
            size=size,
            total_items=total,
            total_pages=total_pages,
        ),
    )


@router.get(
    "/stores/{store_id}/tables/{table_id}/orders",
    response_model=list[OrderResponse],
)
async def list_table_orders(
    store_id: int,
    table_id: int,
    session_id: int = Query(..., description="세션 ID"),
):
    orders = await service.list_table_orders(table_id, session_id)
    return orders


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: int, data: OrderStatusUpdateRequest):
    try:
        order = await service.update_order_status(order_id, data.status)
        return order
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/orders/{order_id}", status_code=200)
async def delete_order(order_id: int):
    try:
        deleted_data = await service.delete_order(order_id)
        return {"message": "주문이 삭제되었습니다.", "deleted_order": deleted_data}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
