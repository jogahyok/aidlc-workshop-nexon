import aiomysql

from app.core.config import settings

pool: aiomysql.Pool | None = None


async def create_pool() -> aiomysql.Pool:
    global pool
    pool = await aiomysql.create_pool(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        db=settings.db_name,
        minsize=1,
        maxsize=10,
        pool_recycle=3600,
        autocommit=True,
        charset="utf8mb4",
    )
    return pool


async def close_pool() -> None:
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()
        pool = None


async def get_connection():
    if pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            yield cursor
