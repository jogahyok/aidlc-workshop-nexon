"""내부 API 라우트 (Store Service용 아카이브)"""

from fastapi import APIRouter, HTTPException

from app.schemas.internal import ArchiveRequest, ArchiveResponse
from app.services.order_service import OrderService

router = APIRouter()
service = OrderService()


@router.post("/internal/orders/archive", response_model=ArchiveResponse)
async def archive_session_orders(data: ArchiveRequest):
    """
    세션 주문 아카이브 API

    - Store Service의 세션 종료 요청으로 트리거
    - 해당 session_id의 모든 주문을 order_history로 이동
    - 상태 무관 (pending/preparing/completed 모두 아카이브)
    - 내부 네트워크에서만 접근 가능 (별도 인증 없음)
    """
    try:
        archived_count = await service.archive_session_orders(
            data.session_id, data.store_id
        )
        return ArchiveResponse(
            archived_count=archived_count,
            session_id=data.session_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ARCHIVE_FAILED",
                "message": f"아카이브 처리 중 오류가 발생했습니다: {str(e)}",
            },
        )
