-- Order Service 초기 스키마
-- 실행 순서: orders → order_items → order_item_options → order_history

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    table_id INT NOT NULL,
    session_id INT NOT NULL,
    order_number VARCHAR(10) NOT NULL,
    status ENUM('pending', 'preparing', 'completed') NOT NULL DEFAULT 'pending',
    total_amount INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_store_status (store_id, status),
    INDEX idx_table_session (table_id, session_id),
    INDEX idx_store_created (store_id, created_at),
    INDEX idx_session (session_id),
    CONSTRAINT chk_total CHECK (total_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_item_id INT NOT NULL,
    menu_name VARCHAR(100) NOT NULL,
    menu_price INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    subtotal INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order (order_id),
    CONSTRAINT chk_quantity CHECK (quantity >= 1),
    CONSTRAINT chk_subtotal CHECK (subtotal >= 0),
    CONSTRAINT fk_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS order_item_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_item_id INT NOT NULL,
    option_item_id INT NOT NULL,
    option_name VARCHAR(50) NOT NULL,
    option_price INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order_item (order_item_id),
    CONSTRAINT chk_opt_price CHECK (option_price >= 0),
    CONSTRAINT fk_order_item FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS order_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_order_id INT NOT NULL,
    store_id INT NOT NULL,
    table_id INT NOT NULL,
    session_id INT NOT NULL,
    order_number VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount INT NOT NULL,
    items_snapshot JSON NOT NULL,
    ordered_at DATETIME NOT NULL,
    archived_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_store_table (store_id, table_id),
    INDEX idx_session (session_id),
    INDEX idx_archived (store_id, archived_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
