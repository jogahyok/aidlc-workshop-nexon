from datetime import datetime, timedelta, timezone

import aiomysql


async def count_recent_failures(
    cursor: aiomysql.DictCursor,
    store_id: int,
    identifier: str,
    attempt_type: str,
    minutes: int = 15,
) -> int:
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    await cursor.execute(
        "SELECT COUNT(*) as cnt FROM login_attempts "
        "WHERE store_id = %s AND identifier = %s AND attempt_type = %s "
        "AND success = FALSE AND attempted_at >= %s",
        (store_id, identifier, attempt_type, since),
    )
    row = await cursor.fetchone()
    return row["cnt"] if row else 0


async def record_attempt(
    cursor: aiomysql.DictCursor,
    store_id: int,
    identifier: str,
    attempt_type: str,
    success: bool,
    ip_address: str | None = None,
) -> None:
    await cursor.execute(
        "INSERT INTO login_attempts (store_id, identifier, attempt_type, success, ip_address) "
        "VALUES (%s, %s, %s, %s, %s)",
        (store_id, identifier, attempt_type, success, ip_address),
    )
