"""쿼리 결과를 도메인 객체로 변환하는 매퍼"""

from app.models.category import Category
from app.models.menu_item import MenuItem
from app.models.option_group import OptionGroup
from app.models.option_item import OptionItem


def map_category(row: tuple) -> Category:
    return Category(
        id=row[0],
        store_id=row[1],
        name=row[2],
        sort_order=row[3],
        is_deleted=bool(row[4]),
        created_at=row[5],
        updated_at=row[6],
    )


def map_menu_item(row: tuple) -> MenuItem:
    return MenuItem(
        id=row[0],
        store_id=row[1],
        category_id=row[2],
        name=row[3],
        description=row[4],
        price=row[5],
        image_url=row[6],
        sort_order=row[7],
        is_deleted=bool(row[8]),
        has_options=bool(row[9]),
        created_at=row[10],
        updated_at=row[11],
    )


def map_option_group(row: tuple) -> OptionGroup:
    return OptionGroup(
        id=row[0],
        menu_item_id=row[1],
        name=row[2],
        type=row[3],
        is_required=bool(row[4]),
        max_select=row[5],
        sort_order=row[6],
        created_at=row[7],
        updated_at=row[8],
    )


def map_option_item(row: tuple) -> OptionItem:
    return OptionItem(
        id=row[0],
        option_group_id=row[1],
        name=row[2],
        price=row[3],
        sort_order=row[4],
        created_at=row[5],
        updated_at=row[6],
    )
