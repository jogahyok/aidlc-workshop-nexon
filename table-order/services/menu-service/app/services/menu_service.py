"""메뉴 항목 비즈니스 로직"""

from typing import Optional

from app.db.connection import get_pool
from app.db.mappers.mappers import map_menu_item
from app.db.queries import menu_queries as q
from app.db.queries import option_queries as oq
from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate


SORT_COLUMNS = {
    "sort_order": "sort_order ASC",
    "price_asc": "price ASC",
    "price_desc": "price DESC",
    "name_asc": "name ASC",
    "name_desc": "name DESC",
}


class MenuItemService:
    async def list_menus(
        self,
        store_id: int,
        category_id: Optional[int] = None,
        sort_by: str = "sort_order",
        include_deleted: bool = False,
    ) -> list[MenuItem]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                if include_deleted:
                    await cur.execute(q.LIST_DELETED_MENUS, (store_id,))
                else:
                    category_filter = (
                        f"AND category_id = {int(category_id)}"
                        if category_id
                        else ""
                    )
                    sort_column = SORT_COLUMNS.get(sort_by, "sort_order ASC")
                    query = q.LIST_MENUS.format(
                        category_filter=category_filter, sort_column=sort_column
                    )
                    await cur.execute(query, (store_id,))

                rows = await cur.fetchall()
                return [map_menu_item(row) for row in rows]

    async def get_menu(self, menu_id: int) -> Optional[MenuItem]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_MENU_BY_ID, (menu_id,))
                row = await cur.fetchone()
                return map_menu_item(row) if row else None

    async def create_menu(self, store_id: int, data: MenuItemCreate) -> MenuItem:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # sort_order 결정
                sort_order = data.sort_order
                if sort_order is None:
                    await cur.execute(
                        q.GET_MAX_SORT_ORDER, (store_id, data.category_id)
                    )
                    row = await cur.fetchone()
                    sort_order = row[0] + 1

                await cur.execute(
                    q.INSERT_MENU,
                    (
                        store_id,
                        data.category_id,
                        data.name,
                        data.description,
                        data.price,
                        data.image_url,
                        sort_order,
                    ),
                )
                menu_id = cur.lastrowid

                await cur.execute(q.GET_MENU_BY_ID, (menu_id,))
                row = await cur.fetchone()
                return map_menu_item(row)

    async def update_menu(self, menu_id: int, data: MenuItemUpdate) -> MenuItem:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_MENU_BY_ID, (menu_id,))
                row = await cur.fetchone()
                if not row:
                    raise ValueError("메뉴를 찾을 수 없습니다.")

                current = map_menu_item(row)

                new_category = (
                    data.category_id
                    if data.category_id is not None
                    else current.category_id
                )
                new_name = data.name if data.name is not None else current.name
                new_desc = (
                    data.description
                    if data.description is not None
                    else current.description
                )
                new_price = data.price if data.price is not None else current.price
                new_image = (
                    data.image_url
                    if data.image_url is not None
                    else current.image_url
                )

                await cur.execute(
                    q.UPDATE_MENU,
                    (new_category, new_name, new_desc, new_price, new_image, menu_id),
                )

                await cur.execute(q.GET_MENU_BY_ID, (menu_id,))
                row = await cur.fetchone()
                return map_menu_item(row)

    async def delete_menu(self, menu_id: int) -> None:
        """메뉴 소프트 삭제"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_MENU_BY_ID, (menu_id,))
                row = await cur.fetchone()
                if not row:
                    raise ValueError("메뉴를 찾을 수 없습니다.")

                await cur.execute(q.SOFT_DELETE_MENU, (menu_id,))

    async def restore_menu(self, menu_id: int) -> MenuItem:
        """소프트 삭제된 메뉴 복구"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_MENU_BY_ID, (menu_id,))
                row = await cur.fetchone()
                if not row:
                    raise ValueError("메뉴를 찾을 수 없습니다.")

                current = map_menu_item(row)
                if not current.is_deleted:
                    raise ValueError("삭제되지 않은 메뉴입니다.")

                await cur.execute(q.RESTORE_MENU, (menu_id,))

                await cur.execute(q.GET_MENU_BY_ID, (menu_id,))
                row = await cur.fetchone()
                return map_menu_item(row)

    async def move_menu(self, menu_id: int, direction: str) -> None:
        """메뉴 순서 이동 (up/down)"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_MENU_BY_ID, (menu_id,))
                row = await cur.fetchone()
                if not row:
                    raise ValueError("메뉴를 찾을 수 없습니다.")

                current = map_menu_item(row)

                if direction == "up":
                    op, order = "<", "DESC"
                else:
                    op, order = ">", "ASC"

                query = q.GET_ADJACENT_MENU.format(op=op, order=order)
                await cur.execute(
                    query,
                    (current.store_id, current.category_id, current.sort_order),
                )
                adjacent = await cur.fetchone()

                if not adjacent:
                    return  # 첫 번째/마지막이면 무시

                adj_id, adj_sort = adjacent[0], adjacent[1]

                await cur.execute(
                    q.SWAP_SORT_ORDER,
                    (
                        menu_id, adj_sort,
                        adj_id, current.sort_order,
                        menu_id, adj_id,
                    ),
                )

    async def update_has_options(self, menu_id: int) -> None:
        """옵션 그룹 존재 여부에 따라 has_options 갱신"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(oq.COUNT_OPTION_GROUPS, (menu_id,))
                row = await cur.fetchone()
                has_options = row[0] > 0
                await cur.execute(q.UPDATE_HAS_OPTIONS, (has_options, menu_id))
