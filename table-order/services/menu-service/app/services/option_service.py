"""옵션 그룹/항목 비즈니스 로직"""

from typing import Optional

from app.db.connection import get_pool
from app.db.mappers.mappers import map_option_group, map_option_item
from app.db.queries import option_queries as q
from app.models.option_group import OptionGroup
from app.models.option_item import OptionItem
from app.schemas.option import OptionGroupCreate, OptionGroupUpdate
from app.services.menu_service import MenuItemService


class OptionService:
    def __init__(self):
        self._menu_service = MenuItemService()

    async def list_option_groups(self, menu_item_id: int) -> list[dict]:
        """옵션 그룹 목록 + 각 그룹의 항목 포함"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 그룹 조회
                await cur.execute(q.LIST_OPTION_GROUPS, (menu_item_id,))
                group_rows = await cur.fetchall()
                groups = [map_option_group(row) for row in group_rows]

                if not groups:
                    return []

                # 모든 그룹의 항목을 한번에 조회
                group_ids = [g.id for g in groups]
                placeholders = ",".join(["%s"] * len(group_ids))
                query = q.LIST_OPTION_ITEMS_BY_GROUPS.format(
                    placeholders=placeholders
                )
                await cur.execute(query, group_ids)
                item_rows = await cur.fetchall()
                items = [map_option_item(row) for row in item_rows]

                # 그룹별로 항목 매핑
                items_by_group: dict[int, list[OptionItem]] = {}
                for item in items:
                    items_by_group.setdefault(item.option_group_id, []).append(item)

                result = []
                for group in groups:
                    result.append({
                        "group": group,
                        "items": items_by_group.get(group.id, []),
                    })

                return result

    async def get_option_group(self, group_id: int) -> Optional[OptionGroup]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_OPTION_GROUP_BY_ID, (group_id,))
                row = await cur.fetchone()
                return map_option_group(row) if row else None

    async def create_option_group(
        self, menu_item_id: int, data: OptionGroupCreate
    ) -> dict:
        """옵션 그룹 생성 (항목 포함)"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # radio 타입은 is_required=True 고정
                is_required = data.type == "radio"
                max_select = 1 if data.type == "radio" else data.max_select

                # sort_order 결정
                sort_order = data.sort_order
                if sort_order is None:
                    await cur.execute(q.GET_MAX_GROUP_SORT_ORDER, (menu_item_id,))
                    row = await cur.fetchone()
                    sort_order = row[0] + 1

                # 그룹 생성
                await cur.execute(
                    q.INSERT_OPTION_GROUP,
                    (menu_item_id, data.name, data.type, is_required, max_select, sort_order),
                )
                group_id = cur.lastrowid

                # 항목 생성
                items = []
                for idx, item_data in enumerate(data.items):
                    item_sort = item_data.sort_order if item_data.sort_order is not None else idx
                    await cur.execute(
                        q.INSERT_OPTION_ITEM,
                        (group_id, item_data.name, item_data.price, item_sort),
                    )

                # has_options 갱신
                await self._menu_service.update_has_options(menu_item_id)

                # 생성된 그룹 + 항목 조회
                await cur.execute(q.GET_OPTION_GROUP_BY_ID, (group_id,))
                group_row = await cur.fetchone()
                group = map_option_group(group_row)

                await cur.execute(q.LIST_OPTION_ITEMS, (group_id,))
                item_rows = await cur.fetchall()
                items = [map_option_item(row) for row in item_rows]

                return {"group": group, "items": items}

    async def update_option_group(
        self, group_id: int, data: OptionGroupUpdate
    ) -> OptionGroup:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_OPTION_GROUP_BY_ID, (group_id,))
                row = await cur.fetchone()
                if not row:
                    raise ValueError("옵션 그룹을 찾을 수 없습니다.")

                current = map_option_group(row)

                new_name = data.name if data.name is not None else current.name
                new_type = data.type if data.type is not None else current.type
                new_required = new_type == "radio"
                new_max = (
                    1 if new_type == "radio"
                    else (data.max_select if data.max_select is not None else current.max_select)
                )

                await cur.execute(
                    q.UPDATE_OPTION_GROUP,
                    (new_name, new_type, new_required, new_max, group_id),
                )

                await cur.execute(q.GET_OPTION_GROUP_BY_ID, (group_id,))
                row = await cur.fetchone()
                return map_option_group(row)

    async def delete_option_group(self, group_id: int) -> None:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_OPTION_GROUP_BY_ID, (group_id,))
                row = await cur.fetchone()
                if not row:
                    raise ValueError("옵션 그룹을 찾을 수 없습니다.")

                group = map_option_group(row)

                # 항목 삭제 후 그룹 삭제
                await cur.execute(q.DELETE_OPTION_ITEMS_BY_GROUP, (group_id,))
                await cur.execute(q.DELETE_OPTION_GROUP, (group_id,))

                # has_options 갱신
                await self._menu_service.update_has_options(group.menu_item_id)
