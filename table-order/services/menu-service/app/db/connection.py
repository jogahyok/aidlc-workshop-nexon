import aiomysql

from app.core.config import settings

_pool: aiomysql.Pool | None = None


async def get_pool() -> aiomysql.Pool:
    global _pool
    if _pool is None:
        _pool = await aiomysql.create_pool(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            db=settings.db_name,
            maxsize=settings.db_pool_size,
            autocommit=True,
            charset="utf8mb4",
        )
    return _pool


async def close_pool():
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None


async def get_connection():
    """컨텍스트 매니저로 사용할 커넥션 획득"""
    pool = await get_pool()
    return pool.acquire()
