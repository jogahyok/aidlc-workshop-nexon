"""옵션 그룹/항목 관련 SQL 쿼리"""

LIST_OPTION_GROUPS = """
    SELECT id, menu_item_id, name, type, is_required, max_select,
           sort_order, created_at, updated_at
    FROM option_groups
    WHERE menu_item_id = %s
    ORDER BY sort_order ASC
"""

GET_OPTION_GROUP_BY_ID = """
    SELECT id, menu_item_id, name, type, is_required, max_select,
           sort_order, created_at, updated_at
    FROM option_groups
    WHERE id = %s
"""

GET_MAX_GROUP_SORT_ORDER = """
    SELECT COALESCE(MAX(sort_order), -1) as max_sort
    FROM option_groups
    WHERE menu_item_id = %s
"""

INSERT_OPTION_GROUP = """
    INSERT INTO option_groups (menu_item_id, name, type, is_required, max_select, sort_order)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

UPDATE_OPTION_GROUP = """
    UPDATE option_groups
    SET name = %s, type = %s, is_required = %s, max_select = %s, updated_at = NOW()
    WHERE id = %s
"""

DELETE_OPTION_GROUP = """
    DELETE FROM option_groups WHERE id = %s
"""

DELETE_OPTION_GROUPS_BY_MENU = """
    DELETE FROM option_groups WHERE menu_item_id = %s
"""

COUNT_OPTION_GROUPS = """
    SELECT COUNT(*) as cnt FROM option_groups WHERE menu_item_id = %s
"""

# Option Items
LIST_OPTION_ITEMS = """
    SELECT id, option_group_id, name, price, sort_order, created_at, updated_at
    FROM option_items
    WHERE option_group_id = %s
    ORDER BY sort_order ASC
"""

LIST_OPTION_ITEMS_BY_GROUPS = """
    SELECT id, option_group_id, name, price, sort_order, created_at, updated_at
    FROM option_items
    WHERE option_group_id IN ({placeholders})
    ORDER BY option_group_id, sort_order ASC
"""

GET_MAX_ITEM_SORT_ORDER = """
    SELECT COALESCE(MAX(sort_order), -1) as max_sort
    FROM option_items
    WHERE option_group_id = %s
"""

INSERT_OPTION_ITEM = """
    INSERT INTO option_items (option_group_id, name, price, sort_order)
    VALUES (%s, %s, %s, %s)
"""

UPDATE_OPTION_ITEM = """
    UPDATE option_items
    SET name = %s, price = %s, updated_at = NOW()
    WHERE id = %s
"""

DELETE_OPTION_ITEM = """
    DELETE FROM option_items WHERE id = %s
"""

DELETE_OPTION_ITEMS_BY_GROUP = """
    DELETE FROM option_items WHERE option_group_id = %s
"""
