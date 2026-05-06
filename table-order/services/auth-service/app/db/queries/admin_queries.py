import aiomysql


async def find_admin_by_store_and_username(
    cursor: aiomysql.DictCursor, store_id: int, username: str
) -> dict | None:
    await cursor.execute(
        "SELECT id, store_id, username, password_hash, created_at, updated_at "
        "FROM admins WHERE store_id = %s AND username = %s",
        (store_id, username),
    )
    return await cursor.fetchone()


async def find_store_by_code(cursor: aiomysql.DictCursor, store_code: str) -> dict | None:
    await cursor.execute(
        "SELECT id, name, code, is_active FROM stores WHERE code = %s",
        (store_code,),
    )
    return await cursor.fetchone()
