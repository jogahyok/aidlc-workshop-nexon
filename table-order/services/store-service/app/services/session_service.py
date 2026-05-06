import logging

import aiomysql

from app.core.exceptions import SessionAlreadyCompletedError
from app.external.order_client import archive_session_orders

logger = logging.getLogger("store-service")


async def get_current_session(cursor: aiomysql.DictCursor, table_id: int) -> dict | None:
    await cursor.execute(
        "SELECT id, table_id, store_id, status, started_at, completed_at "
        "FROM table_sessions WHERE table_id = %s AND status = 'active'",
        (table_id,),
    )
    return await cursor.fetchone()


async def start_new_session(
    cursor: aiomysql.DictCursor, table_id: int, store_id: int
) -> dict:
    existing = await get_current_session(cursor, table_id)
    if existing:
        return existing

    await cursor.execute(
        "INSERT INTO table_sessions (table_id, store_id, status) VALUES (%s, %s, 'active')",
        (table_id, store_id),
    )
    session_id = cursor.lastrowid

    await cursor.execute(
        "SELECT id, table_id, store_id, status, started_at FROM table_sessions WHERE id = %s",
        (session_id,),
    )
    return await cursor.fetchone()


async def complete_session(
    cursor: aiomysql.DictCursor, store_id: int, table_id: int
) -> dict:
    session = await get_current_session(cursor, table_id)
    if not session:
        raise SessionAlreadyCompletedError()

    # Archive orders via Order Service (HTTP with retry)
    await archive_session_orders(session["id"])

    # Mark session as completed
    await cursor.execute(
        "UPDATE table_sessions SET status = 'completed', completed_at = NOW() WHERE id = %s",
        (session["id"],),
    )

    await cursor.execute(
        "SELECT id, table_id, store_id, status, started_at, completed_at "
        "FROM table_sessions WHERE id = %s",
        (session["id"],),
    )
    return await cursor.fetchone()
