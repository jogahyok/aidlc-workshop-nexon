"""내부 API 라우트 (Order Service용 가격 검증)"""

from fastapi import APIRouter, HTTPException

from app.schemas.internal import MenuValidationResponse
from app.services.validation_service import ValidationService

router = APIRouter()
service = ValidationService()


@router.get(
    "/internal/menus/{menu_id}/validate",
    response_model=MenuValidationResponse,
)
async def validate_menu(menu_id: int):
    """
    Order Service용 메뉴 가격 검증 API

    - 메뉴의 현재 가격, 옵션 정보, 가용 여부를 반환
    - 삭제된 메뉴도 조회 가능 (is_available=False로 표시)
    - 내부 네트워크에서만 접근 가능 (별도 인증 없음)
    """
    result = await service.validate_menu(menu_id)
    if result is None:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다.")
    return result
