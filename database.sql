create database ecommerce;

use ecommerce;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
	first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'vendor', 'customer') NOT NULL
);

CREATE TABLE vendors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150),
    description TEXT,
    vendor_id INT,
    warranty_period INT,
    price DECIMAL(10,2),
    inventory INT,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

CREATE TABLE product_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    image_url TEXT,
    FOREIGN KEY (product_id) REFERENCES products(id)
); 

CREATE TABLE discounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    start_time DATETIME NULL,
    end_time DATETIME NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE carts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE product_variants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    color VARCHAR(50),
    size VARCHAR(50),
    stock INT,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT,
    product_variant_id INT,
    quantity INT,
    FOREIGN KEY (cart_id) REFERENCES carts(id),
    FOREIGN KEY (product_variant_id) REFERENCES product_variants(id)
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending','confirmed','handed_to_delivery','shipped'),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_variant_id INT,
    vendor_id INT,
    quantity INT,
    price_at_purchase DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_variant_id) REFERENCES product_variants(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    description TEXT,
    image_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    order_item_id INT,
    type ENUM('return','refund','warranty'),
    status ENUM('pending','rejected','confirmed','processing','complete'),
    title VARCHAR(150),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_item_id) REFERENCES order_items(id)
);

CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    receiver_id INT,
    message TEXT,
    image_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);

use ecommerce;

select * from users;

INSERT INTO users (first_name, last_name, email, username, password, role) VALUES
('Alice', 'Admin', 'alice.admin@example.com', 'alice_admin', 'pass1', 'admin'),
('Bob', 'Admin', 'bob.admin@example.com', 'bob_admin', 'pass2', 'admin'),

('Victor', 'Vendor', 'vendor1@example.com', 'vendor_one', 'pass3', 'vendor'),
('Vera', 'Vendor', 'vendor2@example.com', 'vendor_two', 'pass4', 'vendor'),
('Vince', 'Vendor', 'vendor3@example.com', 'vendor_three', 'pass5', 'vendor'),

('Charlie', 'Customer', 'charlie@example.com', 'charlie_c', 'pass6', 'customer'),
('Diana', 'Customer', 'diana@example.com', 'diana_c', 'pass7', 'customer'),
('Ethan', 'Customer', 'ethan@example.com', 'ethan_c', 'pass8', 'customer'),
('Fiona', 'Customer', 'fiona@example.com', 'fiona_c', 'pass9', 'customer'),
('George', 'Customer', 'george@example.com', 'george_c', 'pass10', 'customer');

INSERT INTO vendors (user_id) VALUES
(3), (4), (5);

INSERT INTO products (title, description, vendor_id, warranty_period, price, inventory) VALUES
('Laptop Pro 15', 'High end laptop', 1, 24, 1500.00, 20),
('Laptop Air 13', 'Lightweight laptop', 1, 12, 999.99, 30),
('Gaming Mouse X', 'RGB gaming mouse', 1, 6, 49.99, 100),

('Smartphone Z', 'Flagship smartphone', 2, 12, 899.00, 50),
('Smartphone Mini', 'Compact smartphone', 2, 12, 699.00, 40),
('Wireless Earbuds', 'Noise cancelling earbuds', 2, 6, 129.99, 80),

('4K Monitor', 'Ultra HD monitor', 3, 18, 399.99, 25),
('Mechanical Keyboard', 'Blue switch keyboard', 3, 12, 89.99, 60),
('USB-C Hub', '7-in-1 hub', 3, 6, 39.99, 150),
('Portable SSD 1TB', 'High speed SSD', 3, 24, 149.99, 40);

INSERT INTO product_variants (product_id, color, size, stock) VALUES
(1, 'Silver', '15-inch', 10),
(2, 'Gray', '13-inch', 15),
(3, 'Black', 'Standard', 50),
(4, 'Black', '128GB', 20),
(5, 'Blue', '128GB', 20),
(6, 'White', 'Standard', 40),
(7, 'Black', '27-inch', 10),
(8, 'Black', 'Full-size', 30),
(9, 'Gray', 'Standard', 70),
(10, 'Black', '1TB', 20);


-- Untimed discounts
INSERT INTO discounts (product_id, old_price, new_price) VALUES
(1, 1500.00, 1299.00),
(4, 899.00, 799.00);

-- Timed discounts
INSERT INTO discounts (product_id, old_price, new_price, start_time, end_time) VALUES
(7, 399.99, 349.99, '2026-04-01 00:00:00', '2026-04-30 23:59:59'),
(10, 149.99, 119.99, '2026-04-10 00:00:00', '2026-04-20 23:59:59');

INSERT INTO carts (user_id) VALUES
(6), (7), (8);

INSERT INTO cart_items (cart_id, product_variant_id, quantity) VALUES
(1, 1, 1),   -- Charlie: Laptop Pro 15
(1, 3, 2),   -- Charlie: Gaming Mouse X
(2, 4, 1),   -- Diana: Smartphone Z
(2, 6, 1),   -- Diana: Earbuds
(3, 7, 1),   -- Ethan: 4K Monitor
(3, 10, 1);  -- Ethan: SSD

INSERT INTO orders (user_id, status) VALUES
(6, 'pending'),
(7, 'confirmed'),
(8, 'handed_to_delivery'),
(9, 'shipped'),
(10, 'shipped'),
(6, 'shipped'),
(7, 'pending');

INSERT INTO order_items (order_id, product_variant_id, vendor_id, quantity, price_at_purchase) VALUES
(1, 1, 1, 1, 1500.00),
(1, 3, 1, 1, 49.99),
(2, 4, 2, 1, 899.00),
(3, 7, 3, 1, 399.99),
(4, 10, 3, 1, 149.99),
(5, 6, 2, 1, 129.99),
(6, 2, 1, 1, 999.99),
(7, 9, 3, 1, 39.99);

