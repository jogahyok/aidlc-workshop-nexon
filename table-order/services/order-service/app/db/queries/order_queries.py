"""주문 관련 SQL 쿼리"""

# 주문 번호 생성 (당일 마지막 번호 조회)
GET_LAST_ORDER_NUMBER_TODAY = """
    SELECT order_number
    FROM orders
    WHERE store_id = %s AND DATE(created_at) = CURDATE()
    ORDER BY order_number DESC
    LIMIT 1
    FOR UPDATE
"""

# 주문 생성
INSERT_ORDER = """
    INSERT INTO orders (store_id, table_id, session_id, order_number, status, total_amount)
    VALUES (%s, %s, %s, %s, 'pending', %s)
"""

INSERT_ORDER_ITEM = """
    INSERT INTO order_items (order_id, menu_item_id, menu_name, menu_price, quantity, subtotal)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

INSERT_ORDER_ITEM_OPTION = """
    INSERT INTO order_item_options (order_item_id, option_item_id, option_name, option_price)
    VALUES (%s, %s, %s, %s)
"""

# 주문 조회
GET_ORDER_BY_ID = """
    SELECT id, store_id, table_id, session_id, order_number, status,
           total_amount, created_at, updated_at
    FROM orders
    WHERE id = %s
"""

LIST_ORDERS_BY_STORE = """
    SELECT id, store_id, table_id, session_id, order_number, status,
           total_amount, created_at, updated_at
    FROM orders
    WHERE store_id = %s
    {status_filter}
    ORDER BY created_at DESC
    LIMIT %s OFFSET %s
"""

COUNT_ORDERS_BY_STORE = """
    SELECT COUNT(*) as cnt
    FROM orders
    WHERE store_id = %s
    {status_filter}
"""

LIST_ORDERS_BY_TABLE_SESSION = """
    SELECT id, store_id, table_id, session_id, order_number, status,
           total_amount, created_at, updated_at
    FROM orders
    WHERE table_id = %s AND session_id = %s
    ORDER BY created_at ASC
"""

# 활성 주문 조회 (SSE 초기 데이터)
LIST_ACTIVE_ORDERS = """
    SELECT id, store_id, table_id, session_id, order_number, status,
           total_amount, created_at, updated_at
    FROM orders
    WHERE store_id = %s AND status IN ('pending', 'preparing')
    ORDER BY created_at ASC
"""

# pending 주문 확인 (동시 주문 제한)
CHECK_PENDING_ORDER = """
    SELECT id, order_number, status, created_at
    FROM orders
    WHERE table_id = %s AND session_id = %s AND status = 'pending'
    LIMIT 1
"""

# 주문 상태 변경
UPDATE_ORDER_STATUS = """
    UPDATE orders
    SET status = %s, updated_at = NOW()
    WHERE id = %s
"""

# 주문 삭제
DELETE_ORDER = """
    DELETE FROM orders WHERE id = %s
"""

# 주문 항목 조회
LIST_ORDER_ITEMS = """
    SELECT id, order_id, menu_item_id, menu_name, menu_price, quantity, subtotal, created_at
    FROM order_items
    WHERE order_id = %s
    ORDER BY id ASC
"""

LIST_ORDER_ITEMS_BY_ORDERS = """
    SELECT id, order_id, menu_item_id, menu_name, menu_price, quantity, subtotal, created_at
    FROM order_items
    WHERE order_id IN ({placeholders})
    ORDER BY order_id, id ASC
"""

# 주문 항목 옵션 조회
LIST_ORDER_ITEM_OPTIONS = """
    SELECT id, order_item_id, option_item_id, option_name, option_price, created_at
    FROM order_item_options
    WHERE order_item_id IN ({placeholders})
    ORDER BY order_item_id, id ASC
"""

# 아카이브
LIST_ORDERS_BY_SESSION = """
    SELECT id, store_id, table_id, session_id, order_number, status,
           total_amount, created_at, updated_at
    FROM orders
    WHERE session_id = %s
"""

INSERT_ORDER_HISTORY = """
    INSERT INTO order_history
        (original_order_id, store_id, table_id, session_id, order_number,
         status, total_amount, items_snapshot, ordered_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

DELETE_ORDERS_BY_SESSION = """
    DELETE FROM orders WHERE session_id = %s
"""

# 주문 이력 조회
LIST_ORDER_HISTORY = """
    SELECT id, original_order_id, store_id, table_id, session_id, order_number,
           status, total_amount, items_snapshot, ordered_at, archived_at
    FROM order_history
    WHERE store_id = %s AND table_id = %s
    {date_filter}
    ORDER BY archived_at DESC
    LIMIT %s OFFSET %s
"""

COUNT_ORDER_HISTORY = """
    SELECT COUNT(*) as cnt
    FROM order_history
    WHERE store_id = %s AND table_id = %s
    {date_filter}
"""
