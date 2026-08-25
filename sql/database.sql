CREATE DATABASE IF NOT EXISTS car_customizer;
USE car_customizer;

CREATE TABLE roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE
);
INSERT INTO roles (role_name) VALUES
('Guest'), ('Player'), ('Shop Manager'), ('Administrator');

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100) NOT NULL,
    money DECIMAL(10,2) DEFAULT 50000.00,
    role_id INT NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);
INSERT INTO users (username, password, nickname, money, role_id, is_active) VALUES
('admin', 'admin123', 'admin', 999999.00, 4, 1),
('manager', 'manager123', 'manager', 50000.00, 3, 1),
('player', 'player123', 'player', 50000.00, 2, 1);

CREATE TABLE manufacturers (
    manufacturer_id INT PRIMARY KEY AUTO_INCREMENT,
    manufacturer_name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(100)
);
INSERT INTO manufacturers (manufacturer_name, country) VALUES
('Toyota', 'Japan'),
('Honda', 'Japan'),
('Nissan', 'Japan'),
('Lexus', 'Japan'),
('Mitsubishi', 'Japan'),
('Mazda', 'Japan');

CREATE TABLE car_models (
    model_id INT PRIMARY KEY AUTO_INCREMENT,
    manufacturer_id INT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_year INT,
    base_hp INT DEFAULT 100,
    base_weight INT DEFAULT 1000,
    base_top_speed INT DEFAULT 150,
    base_acceleration DECIMAL(5,2) DEFAULT 10.0,
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id)
);
INSERT INTO car_models
(manufacturer_id, model_name, model_year, base_hp, base_weight, base_top_speed, base_acceleration)
VALUES
(3, 'Skyline GT-R R34', 1999, 280, 1490, 250, 5.00),
(1, 'Supra MK4', 1993, 320, 1510, 250, 5.10),
(4, 'Lexus LFA', 2010, 552, 1480, 325, 3.70),
(5, 'Lancer Evolution IX', 2006, 286, 1410, 250, 5.20),
(2, 'Honda NSX', 1990, 270, 1350, 270, 5.90),
(6, 'RX-7', 1992, 276, 1250, 250, 5.00);

CREATE TABLE vehicles (
    vehicle_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    model_id INT NOT NULL,
    nickname VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES car_models(model_id)
);

CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL UNIQUE
);
INSERT INTO categories (category_name) VALUES
('Wheels'), ('Spoiler'), ('Bumper'), ('Paint'), ('Engine');

CREATE TABLE parts (
    part_id INT PRIMARY KEY AUTO_INCREMENT,
    category_id INT NOT NULL,
    part_name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    hp_bonus INT DEFAULT 0,
    weight_change INT DEFAULT 0,
    top_speed_bonus INT DEFAULT 0,
    acceleration_bonus DECIMAL(5,2) DEFAULT 0,
    sprite_file VARCHAR(255),
    layer_order INT DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Wheels
INSERT INTO parts
(category_id, part_name, manufacturer, price, hp_bonus, weight_change, top_speed_bonus, acceleration_bonus, sprite_file, layer_order)
VALUES
(1, 'Stock Wheels', 'OEM', 500.00, 0, 0, 0, 0.00, 'stock_wheels.png', 4),
(1, 'BBS LM', 'BBS', 4500.00, 0, -15, 2, 0.15, 'bbs_lm.png', 4),
(1, 'RAYS TE37', 'RAYS', 6000.00, 0, -25, 3, 0.25, 'te37.png', 4),
(1, 'Volk CE28', 'RAYS', 7000.00, 0, -30, 4, 0.30, 'ce28.png', 4),
(1, 'HRE Performance Wheels', 'HRE', 9000.00, 0, -35, 5, 0.35, 'hre.png', 4);

-- Spoilers
INSERT INTO parts
(category_id, part_name, manufacturer, price, hp_bonus, weight_change, top_speed_bonus, acceleration_bonus, sprite_file, layer_order)
VALUES
(2, 'Stock Spoiler', 'OEM', 500.00, 0, 0, 0, 0.00, 'stock_spoiler.png', 6),
(2, 'GT Wing', 'APR', 4000.00, 5, 10, 5, 0.30, 'gt_wing.png', 6),
(2, 'Ducktail Spoiler', 'Mugen', 3500.00, 0, -5, 2, 0.15, 'ducktail.png', 6),
(2, 'Carbon GT Wing', 'Varis', 6500.00, 8, 5, 8, 0.45, 'carbon_gt_wing.png', 6),
(2, 'Time Attack Wing', 'Voltex', 8500.00, 10, 15, 12, 0.60, 'time_attack_wing.png', 6);

-- Bumpers
INSERT INTO parts
(category_id, part_name, manufacturer, price, hp_bonus, weight_change, top_speed_bonus, acceleration_bonus, sprite_file, layer_order)
VALUES
(3, 'Stock Bumper', 'OEM', 500.00, 0, 0, 0, 0.00, 'stock_bumper.png', 5),
(3, 'Bull Bar', 'ARB', 3500.00, 0, 40, 0, 0.00, 'bull_bar.png', 5),
(3, 'NISMO Front Bumper', 'NISMO', 5000.00, 5, -10, 3, 0.20, 'nismo_bumper.png', 5),
(3, 'Rocket Bunny Bumper', 'TRA Kyoto', 6500.00, 8, 5, 5, 0.30, 'rocket_bunny_bumper.png', 5),
(3, 'Varis Front Bumper', 'Varis', 8000.00, 10, -5, 7, 0.40, 'varis_bumper.png', 5);

-- Existing Paint
INSERT INTO parts
(category_id, part_name, manufacturer, price, hp_bonus, weight_change, top_speed_bonus, acceleration_bonus, sprite_file, layer_order)
VALUES
(4, 'Red Paint', 'Custom', 1000.00, 0, 0, 0, 0.00, 'red.png', 1),
(4, 'Blue Paint', 'Custom', 1000.00, 0, 0, 0, 0.00, 'blue.png', 1);

-- Existing Engines
INSERT INTO parts
(category_id, part_name, manufacturer, price, hp_bonus, weight_change, top_speed_bonus, acceleration_bonus, sprite_file, layer_order)
VALUES
(5, 'Stock Engine', 'Toyota', 0.00, 0, 0, 0, 0.00, 'engine_stock.png', 2),
(5, 'Turbo Engine', 'Garrett', 15000.00, 80, 20, 15, 1.00, 'turbo.png', 2);

CREATE TABLE shop_inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    part_id INT NOT NULL,
    stock INT DEFAULT 0,
    FOREIGN KEY (part_id) REFERENCES parts(part_id)
);
INSERT INTO shop_inventory (part_id, stock)
SELECT part_id, 20 FROM parts;

CREATE TABLE player_inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    part_id INT NOT NULL,
    quantity INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (part_id) REFERENCES parts(part_id)
);

CREATE TABLE vehicle_parts (
    vehicle_id INT NOT NULL,
    category_id INT NOT NULL,
    part_id INT NOT NULL,
    PRIMARY KEY (vehicle_id, category_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (part_id) REFERENCES parts(part_id)
);

CREATE TABLE purchases (
    purchase_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    part_id INT NOT NULL,
    quantity INT DEFAULT 1,
    total_price DECIMAL(10,2),
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (part_id) REFERENCES parts(part_id)
);

INSERT INTO vehicles (user_id, model_id, nickname)
VALUES (3, 1, 'My Skyline');

-- Default installed parts for the player's Skyline.
-- IDs are based on this fresh database's insertion order:
-- 1 = Stock Wheels, 6 = Stock Spoiler,
-- 11 = Stock Bumper, 16 = Red Paint, 18 = Stock Engine.
INSERT INTO vehicle_parts (vehicle_id, category_id, part_id) VALUES
(1, 1, 1),
(1, 2, 6),
(1, 3, 11),
(1, 4, 16),
(1, 5, 18);
