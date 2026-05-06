"""옵션 그룹/항목 API 라우트"""

from fastapi import APIRouter, HTTPException

from app.schemas.option import (
    OptionGroupCreate,
    OptionGroupResponse,
    OptionGroupUpdate,
    OptionItemResponse,
)
from app.services.option_service import OptionService

router = APIRouter()
service = OptionService()


@router.get("/menus/{menu_id}/options", response_model=list[OptionGroupResponse])
async def list_option_groups(menu_id: int):
    groups_with_items = await service.list_option_groups(menu_id)

    result = []
    for entry in groups_with_items:
        group = entry["group"]
        items = entry["items"]
        result.append(
            OptionGroupResponse(
                id=group.id,
                menu_item_id=group.menu_item_id,
                name=group.name,
                type=group.type,
                is_required=group.is_required,
                max_select=group.max_select,
                sort_order=group.sort_order,
                items=[OptionItemResponse(**i.__dict__) for i in items],
                created_at=group.created_at,
                updated_at=group.updated_at,
            )
        )
    return result


@router.post(
    "/menus/{menu_id}/options",
    response_model=OptionGroupResponse,
    status_code=201,
)
async def create_option_group(menu_id: int, data: OptionGroupCreate):
    result = await service.create_option_group(menu_id, data)
    group = result["group"]
    items = result["items"]

    return OptionGroupResponse(
        id=group.id,
        menu_item_id=group.menu_item_id,
        name=group.name,
        type=group.type,
        is_required=group.is_required,
        max_select=group.max_select,
        sort_order=group.sort_order,
        items=[OptionItemResponse(**i.__dict__) for i in items],
        created_at=group.created_at,
        updated_at=group.updated_at,
    )


@router.put("/option-groups/{group_id}", response_model=OptionGroupResponse)
async def update_option_group(group_id: int, data: OptionGroupUpdate):
    try:
        group = await service.update_option_group(group_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 항목도 함께 조회
    groups_with_items = await service.list_option_groups(group.menu_item_id)
    items = []
    for entry in groups_with_items:
        if entry["group"].id == group_id:
            items = entry["items"]
            break

    return OptionGroupResponse(
        id=group.id,
        menu_item_id=group.menu_item_id,
        name=group.name,
        type=group.type,
        is_required=group.is_required,
        max_select=group.max_select,
        sort_order=group.sort_order,
        items=[OptionItemResponse(**i.__dict__) for i in items],
        created_at=group.created_at,
        updated_at=group.updated_at,
    )


@router.delete("/option-groups/{group_id}", status_code=204)
async def delete_option_group(group_id: int):
    try:
        await service.delete_option_group(group_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
