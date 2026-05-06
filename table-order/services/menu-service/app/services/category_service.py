"""카테고리 비즈니스 로직"""

from typing import Optional

from app.db.connection import get_pool
from app.db.mappers.mappers import map_category
from app.db.queries import category_queries as q
from app.db.queries import menu_queries as mq
from app.models.category import Category


class CategoryService:
    async def list_categories(self, store_id: int) -> list[Category]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.LIST_CATEGORIES, (store_id,))
                rows = await cur.fetchall()
                return [map_category(row) for row in rows]

    async def list_deleted_categories(self, store_id: int) -> list[Category]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.LIST_DELETED_CATEGORIES, (store_id,))
                rows = await cur.fetchall()
                return [map_category(row) for row in rows]

    async def get_category(self, category_id: int) -> Optional[Category]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_CATEGORY_BY_ID, (category_id,))
                row = await cur.fetchone()
                return map_category(row) if row else None

    async def create_category(
        self, store_id: int, name: str, sort_order: Optional[int] = None
    ) -> Category:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 중복 이름 확인
                await cur.execute(q.CHECK_DUPLICATE_NAME, (store_id, name, 0))
                row = await cur.fetchone()
                if row[0] > 0:
                    raise ValueError(f"카테고리명 '{name}'이(가) 이미 존재합니다.")

                # sort_order 결정
                if sort_order is None:
                    await cur.execute(q.GET_MAX_SORT_ORDER, (store_id,))
                    row = await cur.fetchone()
                    sort_order = row[0] + 1

                await cur.execute(q.INSERT_CATEGORY, (store_id, name, sort_order))
                category_id = cur.lastrowid

                await cur.execute(q.GET_CATEGORY_BY_ID, (category_id,))
                row = await cur.fetchone()
                return map_category(row)

    async def update_category(
        self, category_id: int, name: Optional[str], sort_order: Optional[int]
    ) -> Category:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 기존 카테고리 조회
                await cur.execute(q.GET_CATEGORY_BY_ID, (category_id,))
                row = await cur.fetchone()
                if not row:
                    raise ValueError("카테고리를 찾을 수 없습니다.")

                current = map_category(row)
                new_name = name if name is not None else current.name
                new_sort = sort_order if sort_order is not None else current.sort_order

                # 중복 이름 확인
                if name is not None:
                    await cur.execute(
                        q.CHECK_DUPLICATE_NAME, (current.store_id, new_name, category_id)
                    )
                    dup_row = await cur.fetchone()
                    if dup_row[0] > 0:
                        raise ValueError(f"카테고리명 '{new_name}'이(가) 이미 존재합니다.")

                await cur.execute(q.UPDATE_CATEGORY, (new_name, new_sort, category_id))

                await cur.execute(q.GET_CATEGORY_BY_ID, (category_id,))
                row = await cur.fetchone()
                return map_category(row)

    async def delete_category(self, category_id: int) -> None:
        """카테고리 소프트 삭제 + 하위 메뉴 cascade 소프트 삭제"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_CATEGORY_BY_ID, (category_id,))
                row = await cur.fetchone()
                if not row:
                    raise ValueError("카테고리를 찾을 수 없습니다.")

                # 하위 메뉴 cascade 소프트 삭제
                await cur.execute(mq.SOFT_DELETE_MENUS_BY_CATEGORY, (category_id,))
                # 카테고리 소프트 삭제
                await cur.execute(q.SOFT_DELETE_CATEGORY, (category_id,))

    async def restore_category(self, category_id: int) -> Category:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_CATEGORY_BY_ID, (category_id,))
                row = await cur.fetchone()
                if not row:
                    raise ValueError("카테고리를 찾을 수 없습니다.")

                current = map_category(row)
                if not current.is_deleted:
                    raise ValueError("삭제되지 않은 카테고리입니다.")

                await cur.execute(q.RESTORE_CATEGORY, (category_id,))

                await cur.execute(q.GET_CATEGORY_BY_ID, (category_id,))
                row = await cur.fetchone()
                return map_category(row)

    async def move_category(self, category_id: int, direction: str) -> None:
        """카테고리 순서 이동 (up/down)"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_CATEGORY_BY_ID, (category_id,))
                row = await cur.fetchone()
                if not row:
                    raise ValueError("카테고리를 찾을 수 없습니다.")

                current = map_category(row)

                # 인접 항목 찾기
                if direction == "up":
                    op, order = "<", "DESC"
                else:
                    op, order = ">", "ASC"

                query = q.GET_ADJACENT_CATEGORY.format(op=op, order=order)
                await cur.execute(query, (current.store_id, current.sort_order))
                adjacent = await cur.fetchone()

                if not adjacent:
                    # 첫 번째/마지막 항목이면 무시
                    return

                adj_id, adj_sort = adjacent[0], adjacent[1]

                # sort_order 교환
                await cur.execute(
                    q.SWAP_SORT_ORDER,
                    (
                        category_id, adj_sort,
                        adj_id, current.sort_order,
                        category_id, adj_id,
                    ),
                )
