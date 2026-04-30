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

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE chat_messages;
TRUNCATE TABLE complaints;
TRUNCATE TABLE reviews;
TRUNCATE TABLE order_items;
TRUNCATE TABLE orders;
TRUNCATE TABLE cart_items;
TRUNCATE TABLE carts;
TRUNCATE TABLE product_variants;
TRUNCATE TABLE discounts;
TRUNCATE TABLE product_images;
TRUNCATE TABLE products;
TRUNCATE TABLE vendors;
TRUNCATE TABLE users;

SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO users (first_name, last_name, email, username, password, role) VALUES
('Admin', 'User', 'admin@test.com', 'admin', 'hashed_pw', 'admin'),
('John', 'Vendor', 'john@shop.com', 'johnvendor', 'hashed_pw', 'vendor'),
('Sarah', 'Vendor', 'sarah@shop.com', 'sarahvendor', 'hashed_pw', 'vendor'),
('Mike', 'Customer', 'mike@test.com', 'mike123', 'hashed_pw', 'customer'),
('Emma', 'Customer', 'emma@test.com', 'emma123', 'hashed_pw', 'customer');

INSERT INTO vendors (user_id) VALUES
(2),
(3);

INSERT INTO products (title, description, vendor_id, warranty_period, price, inventory) VALUES
('Basic T-Shirt', 'Cotton t-shirt', 1, 12, 19.99, 100),
('Running Shoes', 'Lightweight running shoes', 1, 24, 79.99, 50),
('Hoodie', 'Warm winter hoodie', 2, 18, 39.99, 80),
('Snapback Hat', 'Stylish hat', 2, 6, 14.99, 120);

INSERT INTO product_images (product_id, image_url) VALUES
(1, 'tshirt1.jpg'),
(1, 'tshirt2.jpg'),
(2, 'shoes1.jpg'),
(3, 'hoodie1.jpg'),
(4, 'hat1.jpg');

INSERT INTO product_variants (product_id, color, size, stock) VALUES
(1, 'Red', 'M', 10),
(1, 'Blue', 'L', 5),

(2, 'Black', '42', 8),
(2, 'White', '43', 6),

(3, 'Black', 'S', 12),
(3, 'Grey', 'M', 7),

(4, 'Black', 'One Size', 20);

INSERT INTO discounts (product_id, old_price, new_price, start_time, end_time) VALUES
(2, 79.99, 59.99, NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY)),
(3, 39.99, 29.99, NOW(), DATE_ADD(NOW(), INTERVAL 5 DAY));

INSERT INTO carts (user_id) VALUES
(4),
(5);

INSERT INTO cart_items (cart_id, product_variant_id, quantity) VALUES
(1, 1, 2),
(1, 3, 1),
(2, 5, 1),
(2, 7, 3);

INSERT INTO orders (user_id, status) VALUES
(4, 'pending'),
(5, 'confirmed');

INSERT INTO order_items (order_id, product_variant_id, vendor_id, quantity, price_at_purchase) VALUES
(1, 1, 1, 2, 19.99),
(1, 3, 1, 1, 79.99),

(2, 5, 2, 1, 39.99),
(2, 7, 2, 3, 14.99);

INSERT INTO reviews (user_id, product_id, rating, description, image_url) VALUES
(4, 1, 5, 'Great shirt!', NULL),
(5, 3, 4, 'Very warm hoodie', NULL);

INSERT INTO complaints (user_id, order_item_id, type, status, title, description) VALUES
(4, 1, 'return', 'pending', 'Wrong size', 'The shirt is too small'),
(5, 3, 'refund', 'processing', 'Damaged item', 'Hoodie arrived damaged');

INSERT INTO chat_messages (sender_id, receiver_id, message, image_url) VALUES
(4, 2, 'Hi, do you have this in stock?', NULL),
(2, 4, 'Yes, it is available!', NULL),
(5, 3, 'When will my order ship?', NULL),
(3, 5, 'It ships tomorrow.', NULL);

select * from cart_items;

ALTER TABLE orders
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;