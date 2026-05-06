from fastapi import APIRouter, Depends, Request

import aiomysql

from app.api.deps import get_current_user, get_db
from app.schemas.auth import (
    AdminLoginRequest,
    TableLoginRequest,
    TableTokenResponse,
    TokenResponse,
    UserInfo,
)
from app.services.auth_service import authenticate_admin, authenticate_table

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(
    body: AdminLoginRequest,
    request: Request,
    cursor: aiomysql.DictCursor = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    result = await authenticate_admin(
        cursor, body.store_code, body.username, body.password, ip_address
    )
    return TokenResponse(**result)


@router.post("/table/login", response_model=TableTokenResponse)
async def table_login(
    body: TableLoginRequest,
    request: Request,
    cursor: aiomysql.DictCursor = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    result = await authenticate_table(
        cursor, body.store_code, body.table_number, body.password, ip_address
    )
    return TableTokenResponse(**result)


@router.get("/me", response_model=UserInfo)
async def get_me(user: UserInfo = Depends(get_current_user)):
    return user
