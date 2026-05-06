"""Order Service 메인 애플리케이션"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import history, internal, orders, stream
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
    title="Order Service",
    description="주문 생성/조회/상태관리/삭제/이력/SSE 실시간 스트림 서비스",
    version="1.0.0",
    lifespan=lifespan,
)

# 라우트 등록
app.include_router(orders.router, tags=["Orders"])
app.include_router(history.router, tags=["Order History"])
app.include_router(stream.router, tags=["SSE Stream"])
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
