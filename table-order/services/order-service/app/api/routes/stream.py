"""SSE 실시간 주문 스트림 라우트"""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.order_service import OrderService
from app.sse.event_manager import sse_manager

router = APIRouter()
service = OrderService()


@router.get("/stores/{store_id}/orders/stream")
async def order_stream(store_id: int):
    """
    SSE 실시간 주문 스트림

    - 연결 즉시 현재 활성 주문(pending + preparing) 전체 전송
    - 이후 new_order, status_changed, order_deleted 이벤트 수신
    - 30초마다 heartbeat 전송
    """

    async def event_generator():
        # 연결 등록
        queue = sse_manager.connect(store_id)

        try:
            # 초기 데이터: 활성 주문 전체 전송
            active_orders = await service.list_active_orders(store_id)
            initial_data = {
                "orders": [order.model_dump() for order in active_orders]
            }
            initial_json = json.dumps(initial_data, ensure_ascii=False, default=str)
            yield f"event: initial_data\ndata: {initial_json}\n\n"

            # 이벤트 스트림
            async for event_str in sse_manager.event_generator(store_id, queue):
                yield event_str

        except Exception:
            sse_manager.disconnect(store_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
