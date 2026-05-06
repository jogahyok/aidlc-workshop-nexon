"""카테고리 API 라우트"""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.category import (
    CategoryCreate,
    CategoryMoveRequest,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import CategoryService

router = APIRouter()
service = CategoryService()


@router.get("/stores/{store_id}/categories", response_model=list[CategoryResponse])
async def list_categories(
    store_id: int,
    deleted: bool = Query(False, description="삭제된 카테고리 조회"),
):
    if deleted:
        categories = await service.list_deleted_categories(store_id)
    else:
        categories = await service.list_categories(store_id)
    return [CategoryResponse(**c.__dict__) for c in categories]


@router.post(
    "/stores/{store_id}/categories",
    response_model=CategoryResponse,
    status_code=201,
)
async def create_category(store_id: int, data: CategoryCreate):
    try:
        category = await service.create_category(
            store_id, data.name, data.sort_order
        )
        return CategoryResponse(**category.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, data: CategoryUpdate):
    try:
        category = await service.update_category(
            category_id, data.name, data.sort_order
        )
        return CategoryResponse(**category.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(category_id: int):
    try:
        await service.delete_category(category_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/categories/{category_id}/restore", response_model=CategoryResponse)
async def restore_category(category_id: int):
    try:
        category = await service.restore_category(category_id)
        return CategoryResponse(**category.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/categories/{category_id}/move", status_code=200)
async def move_category(category_id: int, data: CategoryMoveRequest):
    try:
        await service.move_category(category_id, data.direction)
        return {"message": "순서가 변경되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
