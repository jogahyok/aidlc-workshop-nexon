from datetime import datetime, timedelta, timezone

import aiomysql

from app.core.config import settings
from app.core.exceptions import (
    AccountLockedError,
    AuthenticationError,
    StoreNotFoundError,
    TableNotFoundError,
)
from app.core.security import create_access_token, verify_password
from app.db.queries.admin_queries import find_admin_by_store_and_username, find_store_by_code
from app.db.queries.table_credential_queries import (
    find_credential_by_table_id,
    find_table_by_store_and_number,
)
from app.services.login_attempt_service import is_account_locked, record_login_attempt


async def authenticate_admin(
    cursor: aiomysql.DictCursor,
    store_code: str,
    username: str,
    password: str,
    ip_address: str | None = None,
) -> dict:
    store = await find_store_by_code(cursor, store_code)
    if not store:
        raise StoreNotFoundError()

    store_id = store["id"]

    if await is_account_locked(cursor, store_id, username, "admin"):
        raise AccountLockedError(settings.login_lockout_minutes)

    admin = await find_admin_by_store_and_username(cursor, store_id, username)
    if not admin or not verify_password(password, admin["password_hash"]):
        await record_login_attempt(cursor, store_id, username, "admin", False, ip_address)
        raise AuthenticationError()

    await record_login_attempt(cursor, store_id, username, "admin", True, ip_address)

    token = create_access_token(
        subject=admin["id"], store_id=store_id, token_type="admin"
    )
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
    }


async def authenticate_table(
    cursor: aiomysql.DictCursor,
    store_code: str,
    table_number: int,
    password: str,
    ip_address: str | None = None,
) -> dict:
    store = await find_store_by_code(cursor, store_code)
    if not store:
        raise StoreNotFoundError()

    store_id = store["id"]
    identifier = str(table_number)

    if await is_account_locked(cursor, store_id, identifier, "table"):
        raise AccountLockedError(settings.login_lockout_minutes)

    table = await find_table_by_store_and_number(cursor, store_id, table_number)
    if not table:
        await record_login_attempt(cursor, store_id, identifier, "table", False, ip_address)
        raise TableNotFoundError()

    credential = await find_credential_by_table_id(cursor, table["id"])
    if not credential or not verify_password(password, credential["password_hash"]):
        await record_login_attempt(cursor, store_id, identifier, "table", False, ip_address)
        raise AuthenticationError()

    await record_login_attempt(cursor, store_id, identifier, "table", True, ip_address)

    token = create_access_token(
        subject=table["id"],
        store_id=store_id,
        token_type="table",
        table_number=table_number,
    )
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
        "table_id": table["id"],
        "table_number": table_number,
        "store_id": store_id,
    }
