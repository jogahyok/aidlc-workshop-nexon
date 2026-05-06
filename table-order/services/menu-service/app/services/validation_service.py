"""내부 API용 메뉴 가격 검증 서비스"""

from typing import Optional

from app.db.connection import get_pool
from app.db.mappers.mappers import map_menu_item, map_option_group, map_option_item
from app.db.queries import menu_queries as mq
from app.db.queries import option_queries as oq
from app.schemas.internal import (
    MenuValidationResponse,
    OptionGroupValidation,
    OptionValidation,
)


class ValidationService:
    async def validate_menu(self, menu_id: int) -> Optional[MenuValidationResponse]:
        """Order Service용 메뉴 가격 검증 데이터 반환"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 메뉴 조회
                await cur.execute(mq.GET_MENU_BY_ID, (menu_id,))
                row = await cur.fetchone()
                if not row:
                    return None

                menu = map_menu_item(row)

                # 옵션 그룹 조회
                await cur.execute(oq.LIST_OPTION_GROUPS, (menu_id,))
                group_rows = await cur.fetchall()
                groups = [map_option_group(r) for r in group_rows]

                # 옵션 항목 조회
                option_groups = []
                for group in groups:
                    await cur.execute(oq.LIST_OPTION_ITEMS, (group.id,))
                    item_rows = await cur.fetchall()
                    items = [map_option_item(r) for r in item_rows]

                    option_groups.append(
                        OptionGroupValidation(
                            id=group.id,
                            name=group.name,
                            type=group.type,
                            is_required=group.is_required,
                            max_select=group.max_select,
                            options=[
                                OptionValidation(
                                    id=item.id,
                                    name=item.name,
                                    price=item.price,
                                )
                                for item in items
                            ],
                        )
                    )

                return MenuValidationResponse(
                    menu_id=menu.id,
                    name=menu.name,
                    price=menu.price,
                    is_available=not menu.is_deleted,
                    option_groups=option_groups,
                )
