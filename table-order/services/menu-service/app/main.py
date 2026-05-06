"""Menu Service 메인 애플리케이션"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import categories, internal, menus, options
from app.core.config import settings
from app.db.connection import close_pool, get_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: DB 커넥션 풀 초기화
    await get_pool()
    yield
    # Shutdown: 커넥션 풀 정리
    await close_pool()


app = FastAPI(
    title="Menu Service",
    description="메뉴/카테고리/옵션 관리 서비스",
    version="1.0.0",
    lifespan=lifespan,
)

# 라우트 등록
app.include_router(categories.router, tags=["Categories"])
app.include_router(menus.router, tags=["Menus"])
app.include_router(options.router, tags=["Options"])
app.include_router(internal.router, tags=["Internal"])


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
        return {"status": "healthy", "service": settings.service_name}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
