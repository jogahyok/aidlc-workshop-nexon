"""메뉴 항목 API 라우트"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.menu_item import (
    ImageUploadRequest,
    ImageUploadResponse,
    MenuItemCreate,
    MenuItemMoveRequest,
    MenuItemResponse,
    MenuItemUpdate,
)
from app.services.menu_service import MenuItemService
from app.external.s3_client import s3_client

router = APIRouter()
service = MenuItemService()


@router.get("/stores/{store_id}/menus", response_model=list[MenuItemResponse])
async def list_menus(
    store_id: int,
    category_id: Optional[int] = Query(None, description="카테고리 필터"),
    sort_by: str = Query("sort_order", description="정렬 기준"),
    deleted: bool = Query(False, description="삭제된 메뉴 조회"),
):
    valid_sorts = ["sort_order", "price_asc", "price_desc", "name_asc", "name_desc"]
    if sort_by not in valid_sorts:
        raise HTTPException(
            status_code=422,
            detail=f"sort_by는 {valid_sorts} 중 하나여야 합니다.",
        )

    menus = await service.list_menus(
        store_id, category_id, sort_by, include_deleted=deleted
    )
    return [MenuItemResponse(**m.__dict__) for m in menus]


@router.post(
    "/stores/{store_id}/menus", response_model=MenuItemResponse, status_code=201
)
async def create_menu(store_id: int, data: MenuItemCreate):
    menu = await service.create_menu(store_id, data)
    return MenuItemResponse(**menu.__dict__)


@router.put("/menus/{menu_id}", response_model=MenuItemResponse)
async def update_menu(menu_id: int, data: MenuItemUpdate):
    try:
        menu = await service.update_menu(menu_id, data)
        return MenuItemResponse(**menu.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/menus/{menu_id}", status_code=204)
async def delete_menu(menu_id: int):
    try:
        await service.delete_menu(menu_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/menus/{menu_id}/restore", response_model=MenuItemResponse)
async def restore_menu(menu_id: int):
    try:
        menu = await service.restore_menu(menu_id)
        return MenuItemResponse(**menu.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/menus/{menu_id}/move", status_code=200)
async def move_menu(menu_id: int, data: MenuItemMoveRequest):
    try:
        await service.move_menu(menu_id, data.direction)
        return {"message": "순서가 변경되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/menus/{menu_id}/image", response_model=ImageUploadResponse)
async def generate_upload_url(menu_id: int, data: ImageUploadRequest):
    # 메뉴 존재 확인
    menu = await service.get_menu(menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다.")

    presigned_url, image_key = s3_client.generate_presigned_upload_url(
        menu_id, data.content_type
    )

    return ImageUploadResponse(presigned_url=presigned_url, image_key=image_key)
