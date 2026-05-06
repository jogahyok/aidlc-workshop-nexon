-- Initialize databases for all services
CREATE DATABASE IF NOT EXISTS auth_db;
CREATE DATABASE IF NOT EXISTS store_db;
CREATE DATABASE IF NOT EXISTS menu_db;
CREATE DATABASE IF NOT EXISTS order_db;

-- Create service users
CREATE USER IF NOT EXISTS 'auth_user'@'%' IDENTIFIED BY 'auth_password';
CREATE USER IF NOT EXISTS 'store_user'@'%' IDENTIFIED BY 'store_password';
CREATE USER IF NOT EXISTS 'menu_user'@'%' IDENTIFIED BY 'menu_password';
CREATE USER IF NOT EXISTS 'order_user'@'%' IDENTIFIED BY 'order_password';

GRANT ALL PRIVILEGES ON auth_db.* TO 'auth_user'@'%';
GRANT ALL PRIVILEGES ON store_db.* TO 'store_user'@'%';
GRANT ALL PRIVILEGES ON menu_db.* TO 'menu_user'@'%';
GRANT ALL PRIVILEGES ON order_db.* TO 'order_user'@'%';

-- Auth service needs read access to store_db.stores and store_db.tables
GRANT SELECT ON store_db.stores TO 'auth_user'@'%';
GRANT SELECT ON store_db.tables TO 'auth_user'@'%';

FLUSH PRIVILEGES;
