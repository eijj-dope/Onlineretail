-- CREATE DATABASE
CREATE DATABASE online_store2;
USE online_store2;

-- =========================
-- USERS TABLE
-- =========================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    fullname VARCHAR(150),
    address VARCHAR(255),
    city VARCHAR(100),
    zip_code VARCHAR(20),
    role VARCHAR(20) DEFAULT 'user'
);

-- =========================
-- PRODUCTS TABLE
-- =========================
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    image VARCHAR(255)
);

-- =========================
-- CART ITEMS
-- =========================
CREATE TABLE cart_items (
    cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT NOT NULL,
    UNIQUE(user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- =========================
-- ORDERS TABLE
-- =========================
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    fullname VARCHAR(150),
    address VARCHAR(255),
    city VARCHAR(100),
    zip_code VARCHAR(20),
    payment_method VARCHAR(50),
    total DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =========================
-- ORDER ITEMS
-- =========================
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- =========================
-- INDEXES (Performance)
-- =========================
CREATE INDEX idx_user_cart ON cart_items(user_id);
CREATE INDEX idx_order_user ON orders(user_id);

-- =========================
-- SAMPLE PRODUCTS
-- =========================
INSERT INTO products (name, price, stock, image) VALUES
('Laptop', 1200.00, 10, 'laptop.jpg'),
('Headphones', 150.00, 25, 'headphones.jpg'),
('Smartphone', 900.00, 15, 'smartphone.jpg'),
('Keyboard', 70.00, 30, 'keyboard.jpg');

-- =========================
-- SAMPLE ADMIN USER
-- =========================
INSERT INTO users (name, email, password, role)
VALUES ('Admin', 'russelchristianflores022@gmail.com', 'admin123', 'admin');

SELECT order_id, status FROM orders;

SELECT * FROM products WHERE product_id = 1;