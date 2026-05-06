"""카테고리 관련 SQL 쿼리"""

LIST_CATEGORIES = """
    SELECT id, store_id, name, sort_order, is_deleted, created_at, updated_at
    FROM categories
    WHERE store_id = %s AND is_deleted = FALSE
    ORDER BY sort_order ASC
"""

LIST_DELETED_CATEGORIES = """
    SELECT id, store_id, name, sort_order, is_deleted, created_at, updated_at
    FROM categories
    WHERE store_id = %s AND is_deleted = TRUE
    ORDER BY updated_at DESC
"""

GET_CATEGORY_BY_ID = """
    SELECT id, store_id, name, sort_order, is_deleted, created_at, updated_at
    FROM categories
    WHERE id = %s
"""

GET_MAX_SORT_ORDER = """
    SELECT COALESCE(MAX(sort_order), -1) as max_sort
    FROM categories
    WHERE store_id = %s AND is_deleted = FALSE
"""

CHECK_DUPLICATE_NAME = """
    SELECT COUNT(*) as cnt
    FROM categories
    WHERE store_id = %s AND name = %s AND is_deleted = FALSE AND id != %s
"""

INSERT_CATEGORY = """
    INSERT INTO categories (store_id, name, sort_order, is_deleted)
    VALUES (%s, %s, %s, FALSE)
"""

UPDATE_CATEGORY = """
    UPDATE categories
    SET name = %s, sort_order = %s, updated_at = NOW()
    WHERE id = %s
"""

SOFT_DELETE_CATEGORY = """
    UPDATE categories
    SET is_deleted = TRUE, updated_at = NOW()
    WHERE id = %s
"""

RESTORE_CATEGORY = """
    UPDATE categories
    SET is_deleted = FALSE, updated_at = NOW()
    WHERE id = %s
"""

GET_ADJACENT_CATEGORY = """
    SELECT id, sort_order
    FROM categories
    WHERE store_id = %s AND is_deleted = FALSE AND sort_order {op} %s
    ORDER BY sort_order {order}
    LIMIT 1
"""

SWAP_SORT_ORDER = """
    UPDATE categories
    SET sort_order = CASE id
        WHEN %s THEN %s
        WHEN %s THEN %s
    END,
    updated_at = NOW()
    WHERE id IN (%s, %s)
"""
