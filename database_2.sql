USE ecommerce;

SET FOREIGN_KEY_CHECKS = 0;
SET FOREIGN_KEY_CHECKS = 1;

SET SQL_SAFE_UPDATES = 0;
SET SQL_SAFE_UPDATES = 1;

/* =========================================================
CLEAR DATA
========================================================= */

DELETE FROM chat_messages;
DELETE FROM complaints;
DELETE FROM reviews;
DELETE FROM order_items;
DELETE FROM orders;
DELETE FROM cart_items;
DELETE FROM carts;
DELETE FROM discounts;
DELETE FROM product_images;
DELETE FROM product_variants;
DELETE FROM products;
DELETE FROM vendors;
DELETE FROM users;

/* RESET IDS */
ALTER TABLE users AUTO_INCREMENT = 1;
ALTER TABLE vendors AUTO_INCREMENT = 1;
ALTER TABLE products AUTO_INCREMENT = 1;
ALTER TABLE product_images AUTO_INCREMENT = 1;
ALTER TABLE product_variants AUTO_INCREMENT = 1;

SET FOREIGN_KEY_CHECKS = 1;


/* =========================================================
USERS (PASSWORD = 123)
========================================================= */

INSERT INTO users (first_name,last_name,email,username,password,role)
VALUES
('Admin','One','admin1@example.com','admin1','scrypt:32768:8:1$j184ObyhRZm0kahE$b303456d09f936a2b92f13d2571cee0120c1c1661e1b44130a3be2f2b3df11607b07ad577aa8cd399fa416d2ca1905c922767d309663987ece49d0d2d1e7bb08','admin'),
('Admin','Two','admin2@example.com','admin2','scrypt:32768:8:1$j184ObyhRZm0kahE$b303456d09f936a2b92f13d2571cee0120c1c1661e1b44130a3be2f2b3df11607b07ad577aa8cd399fa416d2ca1905c922767d309663987ece49d0d2d1e7bb08','admin'),
('Admin','Three','admin3@example.com','admin3','scrypt:32768:8:1$j184ObyhRZm0kahE$b303456d09f936a2b92f13d2571cee0120c1c1661e1b44130a3be2f2b3df11607b07ad577aa8cd399fa416d2ca1905c922767d309663987ece49d0d2d1e7bb08','admin'),

('Israel','Cohen','israel@example.com','israel_funeral','scrypt:32768:8:1$j184ObyhRZm0kahE$b303456d09f936a2b92f13d2571cee0120c1c1661e1b44130a3be2f2b3df11607b07ad577aa8cd399fa416d2ca1905c922767d309663987ece49d0d2d1e7bb08','vendor'),
('Steve','Irwin','steve@example.com','steve_irwin','scrypt:32768:8:1$j184ObyhRZm0kahE$b303456d09f936a2b92f13d2571cee0120c1c1661e1b44130a3be2f2b3df11607b07ad577aa8cd399fa416d2ca1905c922767d309663987ece49d0d2d1e7bb08','vendor'),
('Jane','Doe','jane@example.com','janedoe','scrypt:32768:8:1$j184ObyhRZm0kahE$b303456d09f936a2b92f13d2571cee0120c1c1661e1b44130a3be2f2b3df11607b07ad577aa8cd399fa416d2ca1905c922767d309663987ece49d0d2d1e7bb08','vendor'),
('Kaden','Black','kaden@example.com','kadenshop','scrypt:32768:8:1$j184ObyhRZm0kahE$b303456d09f936a2b92f13d2571cee0120c1c1661e1b44130a3be2f2b3df11607b07ad577aa8cd399fa416d2ca1905c922767d309663987ece49d0d2d1e7bb08','vendor'),
('Military','Dan','dan@example.com','militarydan','scrypt:32768:8:1$j184ObyhRZm0kahE$b303456d09f936a2b92f13d2571cee0120c1c1661e1b44130a3be2f2b3df11607b07ad577aa8cd399fa416d2ca1905c922767d309663987ece49d0d2d1e7bb08','vendor'),

('Oliver','Smith','oliver@example.com','oliver123','scrypt:32768:8:1$j184ObyhRZm0kahE$b303456d09f936a2b92f13d2571cee0120c1c1661e1b44130a3be2f2b3df11607b07ad577aa8cd399fa416d2ca1905c922767d309663987ece49d0d2d1e7bb08','customer'),
('Emily','Stone','emily@example.com','emstone','scrypt:32768:8:1$j184ObyhRZm0kahE$b303456d09f936a2b92f13d2571cee0120c1c1661e1b44130a3be2f2b3df11607b07ad577aa8cd399fa416d2ca1905c922767d309663987ece49d0d2d1e7bb08','customer');


/* =========================================================
VENDORS
========================================================= */

INSERT INTO vendors (user_id, shop_name)
VALUES
(4,'Israel''s Funeral Oddities'),
(5,'Steve Irwin''s Supply'),
(6,'Jane Doe Memorials'),
(7,'Kaden''s Eternal Luxury'),
(8,'International Funeral Supply Co.');


/* =========================================================
PRODUCTS (ORDER MATTERS FOR IMAGE MATCHING)
========================================================= */

INSERT INTO products (title,description,vendor_id,warranty_period,price,inventory,is_sponsored)
VALUES

('Asia Coffin','Traditional styled coffin with engraved detailing',4,180,12999.99,22,0),
('Canada Urn','Premium maple-inspired memorial urn',5,180,6999.99,18,0),
('Bowling Urn','Bowling themed memorial urn',6,120,7499.99,9,0),
('Cammo Casket','Military camouflage luxury casket',8,365,23999.99,6,0),

('Car Urn','Automotive themed urn series',7,365,8999.99,25,0),
('Cheeta Urn','Fast-pattern wildlife urn design',5,180,6999.99,14,0),
('Cow Casket','Farm styled premium casket',5,365,21999.99,7,0),
('Disco Urn','Retro disco themed urn',6,120,5999.99,30,0),

('Dog Urn','Pet memorial urn series',6,90,3999.99,40,0),
('Eagle Urn','Patriotic eagle engraved urn',5,180,8499.99,12,0),
('Fish Urn','Ocean themed urn collection',4,120,4999.99,33,0),
('Furry Urn','Soft texture novelty urn',4,30,3999.99,8,0),

('Galaxy Urn','Space themed luxury urn',5,365,11999.99,5,0),
('Gold Casket','Luxury gold plated casket',4,365,29999.99,4,0),
('Gold Egg Urn','Egg shaped gold memorial urn',5,365,15999.99,6,0),
('Military Casket','Full ceremonial military casket set',8,365,25999.99,11,0),

('Military Urn','Service themed memorial urn',8,365,10999.99,20,0),
('Open Urn','Minimal open design urn',7,120,5499.99,28,0),
('Orange Casket','Bright colored casket series',6,180,15999.99,21,0),
('Peanutbutter Urn','Novelty food themed urn',7,60,4999.99,3,0),

('Pine Casket','Natural wood pine casket',6,730,27999.99,17,0),
('Pink Casket','Feminine pink casket variant',6,365,24999.99,22,0),
('Purple Casket','Feminine purple casket variant',6,365,24999.99,19,0),
('Sage Casket','Feminine sage casket variant',6,365,24999.99,16,0),

('Silver Urn','Premium silver finish urn',5,180,8999.99,24,0),
('Thanos Urn','Purple titan themed urn',5,90,12999.99,2,0),
('Undertaker Urn','Dark gothic premium urn',4,180,9999.99,7,0),
('Purple Urn','Royal purple urn series',6,180,6499.99,26,0),

('Rainbow Urn','Color shifting memorial urn',6,180,7999.99,13,0);


/* =========================================================
PRODUCT IMAGES (MATCHED EXACTLY TO FILENAMES)
========================================================= */

INSERT INTO product_images (product_id, image_url) VALUES

(1,'/static/images/products/asia_coffin_1.png'),
(1,'/static/images/products/asia_coffin_2.png'),

(2,'/static/images/products/canada_urn_1.png'),
(2,'/static/images/products/canada_urn_2.png'),
(2,'/static/images/products/canada_urn_3.png'),

(3,'/static/images/products/bowling_urn_1.png'),
(3,'/static/images/products/bowling_urn_2.png'),
(3,'/static/images/products/bowling_urn_3.png'),

(4,'/static/images/products/cammo_casket_1.png'),
(4,'/static/images/products/cammo_casket_2.png'),

(5,'/static/images/products/car_urn_1.png'),
(5,'/static/images/products/car_urn_2.png'),
(5,'/static/images/products/car_urn_3.png'),
(5,'/static/images/products/car_urn_4.png'),

(6,'/static/images/products/cheeta_urn_1.png'),
(6,'/static/images/products/cheeta_urn_2.png'),
(6,'/static/images/products/cheeta_urn_3.png'),

(7,'/static/images/products/cow_casket_1.png'),
(7,'/static/images/products/cow_casket_2.png'),

(8,'/static/images/products/disco_urn_1.png'),
(8,'/static/images/products/disco_urn_2.png'),

(9,'/static/images/products/dog_urn_1.png'),
(9,'/static/images/products/dog_urn_2.png'),
(9,'/static/images/products/dog_urn_3.png'),
(9,'/static/images/products/dog_urn_4.png'),

(10,'/static/images/products/eagle_urn_1.png'),
(10,'/static/images/products/eagle_urn_2.png'),
(10,'/static/images/products/eagle_urn_3.png'),

(11,'/static/images/products/fish_urn_1.png'),
(11,'/static/images/products/fish_urn_2.png'),
(11,'/static/images/products/fish_urn_3.png'),

(12,'/static/images/products/furry_urn_1.png'),

(13,'/static/images/products/galaxy_urn_1.png'),
(13,'/static/images/products/galaxy_urn_2.png'),
(13,'/static/images/products/galaxy_urn_3.png'),
(13,'/static/images/products/galaxy_urn_4.png'),
(13,'/static/images/products/galaxy_urn_5.png'),

(14,'/static/images/products/gold_casket_1.png'),
(14,'/static/images/products/gold_casket_2.png'),

(15,'/static/images/products/goldegg_urn_1.png'),
(15,'/static/images/products/goldegg_urn_2.png'),
(15,'/static/images/products/goldegg_urn_3.png'),

(16,'/static/images/products/military_casket_1.png'),
(16,'/static/images/products/military_casket_2.png'),
(16,'/static/images/products/military_casket_3.png'),
(16,'/static/images/products/military_casket_4.png'),
(16,'/static/images/products/military_casket_5.png'),

(17,'/static/images/products/military_urn_1.png'),
(17,'/static/images/products/military_urn_2.png'),
(17,'/static/images/products/military_urn_3.png'),

(18,'/static/images/products/open_urn_1.png'),
(18,'/static/images/products/open_urn_2.png'),

(19,'/static/images/products/orange_casket_1.png'),
(19,'/static/images/products/orange_casket_2.png'),

(20,'/static/images/products/peanutbutter_urn_1.png'),

(21,'/static/images/products/pine_casket_1.png'),
(21,'/static/images/products/pine_casket_2.png'),
(21,'/static/images/products/pine_casket_3.png'),
(21,'/static/images/products/pine_casket_4.png'),

(22,'/static/images/products/pink_casket_1.png'),
(22,'/static/images/products/pink_casket_2.png'),

(23,'/static/images/products/purple_casket_1.png'),
(23,'/static/images/products/purple_casket_2.png'),

(24,'/static/images/products/sage_casket_1.png'),
(24,'/static/images/products/sage_casket_2.png'),

(25,'/static/images/products/silver_urn_1.png'),
(25,'/static/images/products/silver_urn_2.png'),

(26,'/static/images/products/thanos_urn_1.png'),

(27,'/static/images/products/undertaker_urn_1.png'),
(27,'/static/images/products/undertaker_urn_2.png'),
(27,'/static/images/products/undertaker_urn_3.png'),
(27,'/static/images/products/undertaker_urn_4.png'),

(28,'/static/images/products/purple_urn_1.png'),
(28,'/static/images/products/purple_urn_2.png'),
(28,'/static/images/products/purple_urn_3.png'),

(29,'/static/images/products/rainbow_urn_1.png'),
(29,'/static/images/products/rainbow_urn_2.png'),
(29,'/static/images/products/rainbow_urn_3.png');


/* =========================================================
VARIANTS (ONLY WHERE LOGICAL)
========================================================= */

INSERT INTO product_variants (product_id,color,size,stock)
VALUES
(5,'Red','Standard',10),
(5,'Green','Standard',12),
(5,'Yellow','Standard',8),

(16,'Standard','Full',5),
(17,'Standard','Standard',20),

(22,'Pink','Large',22),
(23,'Purple','Large',19),
(24,'Sage','Large',16),

(25,'Silver','Medium',24),
(28,'Purple','Large',26);


/* =========================================================
REVIEWS
========================================================= */

INSERT INTO reviews (user_id,product_id,rating,description,image_url)
VALUES
(9,3,5,'Unexpectedly perfect bowling themed urn.',NULL),
(10,9,4,'Dog urn was oddly comforting.',NULL),
(9,14,5,'Gold casket was ridiculous but impressive.',NULL);


/* =========================================================
DISCOUNTS (OPTIONAL)
========================================================= */

INSERT INTO discounts (product_id,old_price,new_price,start_time,end_time)
VALUES
(13,12999.99,10999.99,NOW(),DATE_ADD(NOW(),INTERVAL 10 DAY)),
(27,9999.99,8499.99,NOW(),DATE_ADD(NOW(),INTERVAL 7 DAY)),
(29,7999.99,6999.99,NOW(),DATE_ADD(NOW(),INTERVAL 5 DAY));






UPDATE products SET inventory = CASE title

WHEN 'Asia Coffin' THEN 22
WHEN 'Canada Urn' THEN 18
WHEN 'Bowling Urn' THEN 9
WHEN 'Cammo Casket' THEN 6

WHEN 'Car Urn' THEN 25
WHEN 'Cheeta Urn' THEN 14
WHEN 'Cow Casket' THEN 7
WHEN 'Disco Urn' THEN 30

WHEN 'Dog Urn' THEN 40
WHEN 'Eagle Urn' THEN 12
WHEN 'Fish Urn' THEN 33
WHEN 'Furry Urn' THEN 8

WHEN 'Galaxy Urn' THEN 13
WHEN 'Gold Casket' THEN 4
WHEN 'Gold Egg Urn' THEN 6
WHEN 'Military Casket' THEN 11

WHEN 'Military Urn' THEN 20
WHEN 'Open Urn' THEN 28
WHEN 'Orange Casket' THEN 21
WHEN 'Peanutbutter Urn' THEN 3

WHEN 'Pine Casket' THEN 17
WHEN 'Pink Casket' THEN 22
WHEN 'Purple Casket' THEN 19
WHEN 'Sage Casket' THEN 16

WHEN 'Silver Urn' THEN 24
WHEN 'Thanos Urn' THEN 2
WHEN 'Undertaker Urn' THEN 7
WHEN 'Purple Urn' THEN 26

WHEN 'Rainbow Urn' THEN 19

ELSE inventory
END;