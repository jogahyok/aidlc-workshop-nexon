"""메뉴 항목 관련 SQL 쿼리"""

LIST_MENUS = """
    SELECT id, store_id, category_id, name, description, price,
           image_url, sort_order, is_deleted, has_options, created_at, updated_at
    FROM menu_items
    WHERE store_id = %s AND is_deleted = FALSE
    {category_filter}
    ORDER BY {sort_column}
"""

LIST_DELETED_MENUS = """
    SELECT id, store_id, category_id, name, description, price,
           image_url, sort_order, is_deleted, has_options, created_at, updated_at
    FROM menu_items
    WHERE store_id = %s AND is_deleted = TRUE
    ORDER BY updated_at DESC
"""

GET_MENU_BY_ID = """
    SELECT id, store_id, category_id, name, description, price,
           image_url, sort_order, is_deleted, has_options, created_at, updated_at
    FROM menu_items
    WHERE id = %s
"""

GET_MAX_SORT_ORDER = """
    SELECT COALESCE(MAX(sort_order), -1) as max_sort
    FROM menu_items
    WHERE store_id = %s AND category_id = %s AND is_deleted = FALSE
"""

INSERT_MENU = """
    INSERT INTO menu_items (store_id, category_id, name, description, price,
                           image_url, sort_order, is_deleted, has_options)
    VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE, FALSE)
"""

UPDATE_MENU = """
    UPDATE menu_items
    SET category_id = %s, name = %s, description = %s, price = %s,
        image_url = %s, updated_at = NOW()
    WHERE id = %s
"""

SOFT_DELETE_MENU = """
    UPDATE menu_items
    SET is_deleted = TRUE, updated_at = NOW()
    WHERE id = %s
"""

SOFT_DELETE_MENUS_BY_CATEGORY = """
    UPDATE menu_items
    SET is_deleted = TRUE, updated_at = NOW()
    WHERE category_id = %s AND is_deleted = FALSE
"""

RESTORE_MENU = """
    UPDATE menu_items
    SET is_deleted = FALSE, updated_at = NOW()
    WHERE id = %s
"""

UPDATE_HAS_OPTIONS = """
    UPDATE menu_items
    SET has_options = %s, updated_at = NOW()
    WHERE id = %s
"""

GET_ADJACENT_MENU = """
    SELECT id, sort_order
    FROM menu_items
    WHERE store_id = %s AND category_id = %s AND is_deleted = FALSE
          AND sort_order {op} %s
    ORDER BY sort_order {order}
    LIMIT 1
"""

SWAP_SORT_ORDER = """
    UPDATE menu_items
    SET sort_order = CASE id
        WHEN %s THEN %s
        WHEN %s THEN %s
    END,
    updated_at = NOW()
    WHERE id IN (%s, %s)
"""

COUNT_ACTIVE_MENUS_IN_CATEGORY = """
    SELECT COUNT(*) as cnt
    FROM menu_items
    WHERE category_id = %s AND is_deleted = FALSE
"""
