from datetime import datetime, timezone

from fastapi import APIRouter

from app.db.connection import pool

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    db_ok = False
    if pool:
        try:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    db_ok = True
        except Exception:
            db_ok = False

    status = "healthy" if db_ok else "unhealthy"
    return {
        "status": status,
        "checks": {"database": "ok" if db_ok else "failed"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
