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

select * from cart_items;


-- add these 2 lines to give shop names to vendors,
-- the python will also default to the vendor username if shop_name = null
ALTER TABLE vendors
ADD COLUMN shop_name VARCHAR(255);

UPDATE vendors
SET shop_name = "Victor's Laptop Emporium"
WHERE user_id = 3;
SELECT * FROM vendors;

use ecommerce;

ALTER TABLE products
ADD COLUMN is_sponsored BOOLEAN DEFAULT 0,
ADD COLUMN is_package BOOLEAN DEFAULT 0;

-- Add this to be able to cancel orders.
ALTER TABLE orders
MODIFY status ENUM(
    'pending',
    'confirmed',
    'handed_to_delivery',
    'shipped',
    'cancelled'
);

select * from orders;


-- add both of these for customer complaints
ALTER TABLE complaints
ADD image_url TEXT;
ALTER TABLE complaints
ADD admin_notes TEXT;

INSERT INTO users (first_name, last_name, email, username, password, role)
VALUES (
    'Admin',
    'User',
    'admin@example.com',
    'admin',
    'scrypt:32768:8:1$j184ObyhRZm0kahE$b303456d09f936a2b92f13d2571cee0120c1c1661e1b44130a3be2f2b3df11607b07ad577aa8cd399fa416d2ca1905c922767d309663987ece49d0d2d1e7bb08',
    'admin'
);

DELETE FROM chat_messages;
DELETE FROM complaints;
DELETE FROM reviews;
DELETE FROM order_items;
DELETE FROM orders;
DELETE FROM cart_items;
DELETE FROM carts;
DELETE FROM users;

SET FOREIGN_KEY_CHECKS = 0;

SET FOREIGN_KEY_CHECKS = 1;