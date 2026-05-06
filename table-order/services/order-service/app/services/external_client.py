"""외부 서비스 HTTP 클라이언트"""

import httpx

from app.core.config import settings


class MenuServiceClient:
    """Menu Service 내부 API 클라이언트"""

    async def validate_menu(self, menu_id: int) -> dict | None:
        """
        메뉴 가격 검증 데이터 조회
        - Timeout: 5초
        - 재시도: 1회 (총 2회 시도)
        - 실패 시: None 반환
        """
        url = f"{settings.menu_service_url}/internal/menus/{menu_id}/validate"

        for attempt in range(2):
            try:
                async with httpx.AsyncClient(
                    timeout=settings.menu_service_timeout
                ) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 404:
                        return None
            except (httpx.TimeoutException, httpx.ConnectError):
                if attempt == 1:
                    return None
                continue

        return None


class StoreServiceClient:
    """Store Service 내부 API 클라이언트"""

    async def validate_session(
        self, session_id: int
    ) -> dict | None:
        """
        세션 유효성 확인
        - Timeout: 3초
        - 재시도: 1회
        """
        url = f"{settings.store_service_url}/internal/sessions/{session_id}/validate"

        for attempt in range(2):
            try:
                async with httpx.AsyncClient(
                    timeout=settings.store_service_timeout
                ) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 404:
                        return None
            except (httpx.TimeoutException, httpx.ConnectError):
                if attempt == 1:
                    return None
                continue

        return None


menu_client = MenuServiceClient()
store_client = StoreServiceClient()
