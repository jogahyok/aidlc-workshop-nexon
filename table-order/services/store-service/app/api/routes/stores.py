from fastapi import APIRouter, Depends

import aiomysql

from app.db.connection import get_connection

router = APIRouter(prefix="/api/stores", tags=["stores"])


@router.get("/{store_id}")
async def get_store(store_id: int, cursor: aiomysql.DictCursor = Depends(get_connection)):
    await cursor.execute(
        "SELECT id, name, code, is_active, created_at FROM stores WHERE id = %s",
        (store_id,),
    )
    store = await cursor.fetchone()
    if not store:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Store not found")
    return store
