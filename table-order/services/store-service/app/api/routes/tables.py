from fastapi import APIRouter, Depends, HTTPException

import aiomysql

from app.core.exceptions import TableNumberDuplicateError
from app.db.connection import get_connection
from pydantic import BaseModel, Field


class CreateTableRequest(BaseModel):
    table_number: int = Field(..., gt=0)
    password: str = Field(..., min_length=4, max_length=8)


router = APIRouter(prefix="/api/stores/{store_id}/tables", tags=["tables"])


@router.get("")
async def list_tables(store_id: int, cursor: aiomysql.DictCursor = Depends(get_connection)):
    await cursor.execute(
        "SELECT id, store_id, table_number, is_active, created_at FROM tables WHERE store_id = %s",
        (store_id,),
    )
    return await cursor.fetchall()


@router.post("", status_code=201)
async def create_table(
    store_id: int,
    body: CreateTableRequest,
    cursor: aiomysql.DictCursor = Depends(get_connection),
):
    # Check duplicate
    await cursor.execute(
        "SELECT id FROM tables WHERE store_id = %s AND table_number = %s",
        (store_id, body.table_number),
    )
    if await cursor.fetchone():
        raise TableNumberDuplicateError()

    # Create table
    await cursor.execute(
        "INSERT INTO tables (store_id, table_number) VALUES (%s, %s)",
        (store_id, body.table_number),
    )
    table_id = cursor.lastrowid

    # Create credential
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_hash = pwd_context.hash(body.password)

    await cursor.execute(
        "INSERT INTO table_credentials (store_id, table_id, password_hash) VALUES (%s, %s, %s)",
        (store_id, table_id, password_hash),
    )

    return {"table_id": table_id, "table_number": body.table_number}
