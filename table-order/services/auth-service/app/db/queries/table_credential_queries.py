import aiomysql


async def find_table_by_store_and_number(
    cursor: aiomysql.DictCursor, store_id: int, table_number: int
) -> dict | None:
    await cursor.execute(
        "SELECT id, store_id, table_number, is_active "
        "FROM tables WHERE store_id = %s AND table_number = %s",
        (store_id, table_number),
    )
    return await cursor.fetchone()


async def find_credential_by_table_id(
    cursor: aiomysql.DictCursor, table_id: int
) -> dict | None:
    await cursor.execute(
        "SELECT id, store_id, table_id, password_hash "
        "FROM table_credentials WHERE table_id = %s",
        (table_id,),
    )
    return await cursor.fetchone()
