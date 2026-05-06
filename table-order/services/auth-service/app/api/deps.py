from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.core.security import decode_access_token
from app.core.security import InvalidTokenError as JWTInvalidError
from app.db.connection import get_connection
from app.schemas.auth import UserInfo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/admin/login")


async def get_db():
    async for cursor in get_connection():
        yield cursor


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInfo:
    try:
        payload = decode_access_token(token)
    except JWTInvalidError:
        raise InvalidTokenError()

    if payload.get("exp") is None:
        raise InvalidTokenError()

    return UserInfo(
        user_id=int(payload["sub"]),
        store_id=payload["store_id"],
        user_type=payload["type"],
        table_number=payload.get("table_number"),
    )


async def get_current_admin(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    if user.user_type != "admin":
        raise InvalidTokenError()
    return user
