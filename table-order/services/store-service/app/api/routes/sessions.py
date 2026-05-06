from fastapi import APIRouter, Depends

import aiomysql

from app.db.connection import get_connection
from app.services.session_service import complete_session, get_current_session, start_new_session

router = APIRouter(prefix="/api/stores/{store_id}/tables/{table_id}", tags=["sessions"])


@router.get("/session")
async def get_session(
    store_id: int,
    table_id: int,
    cursor: aiomysql.DictCursor = Depends(get_connection),
):
    session = await get_current_session(cursor, table_id)
    if not session:
        return {"session": None, "message": "활성 세션이 없습니다"}
    return session


@router.post("/session", status_code=201)
async def create_session(
    store_id: int,
    table_id: int,
    cursor: aiomysql.DictCursor = Depends(get_connection),
):
    session = await start_new_session(cursor, table_id, store_id)
    return session


@router.post("/complete")
async def complete_table_session(
    store_id: int,
    table_id: int,
    cursor: aiomysql.DictCursor = Depends(get_connection),
):
    session = await complete_session(cursor, store_id, table_id)
    return {"session_id": session["id"], "completed_at": session["completed_at"], "message": "이용 완료 처리되었습니다"}
