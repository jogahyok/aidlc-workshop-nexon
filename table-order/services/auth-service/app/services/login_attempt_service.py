import aiomysql

from app.core.config import settings
from app.db.queries.login_attempt_queries import count_recent_failures, record_attempt


async def is_account_locked(
    cursor: aiomysql.DictCursor,
    store_id: int,
    identifier: str,
    attempt_type: str,
) -> bool:
    count = await count_recent_failures(
        cursor, store_id, identifier, attempt_type, settings.login_lockout_minutes
    )
    return count >= settings.login_max_attempts


async def record_login_attempt(
    cursor: aiomysql.DictCursor,
    store_id: int,
    identifier: str,
    attempt_type: str,
    success: bool,
    ip_address: str | None = None,
) -> None:
    await record_attempt(cursor, store_id, identifier, attempt_type, success, ip_address)
