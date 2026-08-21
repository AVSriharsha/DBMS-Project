CREATE DATABASE IF NOT EXISTS car_customizer;

USE car_customizer;

-- ============================================================
-- ROLES
-- ============================================================

CREATE TABLE roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO roles (role_name) VALUES
('Guest'),
('Player'),
('Shop Manager'),
('Administrator');


-- ============================================================
-- USERS
-- nickname: name used by the app when greeting the user
-- is_active: 1 = active, 0 = deactivated by management
-- ============================================================

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100) NOT NULL,
    money DECIMAL(10,2) DEFAULT 50000.00,
    role_id INT NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,

    FOREIGN KEY (role_id)
        REFERENCES roles(role_id)
);


-- ============================================================
-- MANUFACTURERS
-- ============================================================

CREATE TABLE manufacturers (
    manufacturer_id INT PRIMARY KEY AUTO_INCREMENT,
    manufacturer_name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(100)
);

INSERT INTO manufacturers
(manufacturer_name, country)
VALUES
('Toyota', 'Japan'),
('Honda', 'Japan'),
('BMW', 'Germany'),
('Nissan', 'Japan');


-- ============================================================
-- CAR MODELS
-- ============================================================

CREATE TABLE car_models (
    model_id INT PRIMARY KEY AUTO_INCREMENT,
    manufacturer_id INT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_year INT,

    base_hp INT DEFAULT 100,
    base_weight INT DEFAULT 1000,
    base_top_speed INT DEFAULT 150,
    base_acceleration DECIMAL(5,2) DEFAULT 10.0,

    FOREIGN KEY (manufacturer_id)
        REFERENCES manufacturers(manufacturer_id)
);


INSERT INTO car_models
(
    manufacturer_id,
    model_name,
    model_year,
    base_hp,
    base_weight,
    base_top_speed,
    base_acceleration
)
VALUES
(4, 'Skyline GT-R R34', 1999, 280, 1490, 250, 5.0),
(2, 'Civic EK9', 1999, 182, 1090, 225, 6.5),
(3, 'M3 E46', 2003, 333, 1570, 250, 5.2);


-- ============================================================
-- PLAYER VEHICLES
-- ============================================================

CREATE TABLE vehicles (
    vehicle_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    model_id INT NOT NULL,
    nickname VARCHAR(100),

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    FOREIGN KEY (model_id)
        REFERENCES car_models(model_id)
);


-- ============================================================
-- PART CATEGORIES
-- ============================================================

CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO categories (category_name) VALUES
('Wheels'),
('Spoiler'),
('Bumper'),
('Paint'),
('Engine');


-- ============================================================
-- PARTS
-- ============================================================

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

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);


INSERT INTO parts
(
    category_id,
    part_name,
    manufacturer,
    price,
    hp_bonus,
    weight_change,
    top_speed_bonus,
    acceleration_bonus,
    sprite_file,
    layer_order
)
VALUES

-- Wheels
(1, 'Steel Wheels', 'Toyota', 500, 0, 0, 0, 0, 'steel.png', 4),
(1, 'Alloy Wheels', 'BBS', 2500, 0, -20, 2, 0.2, 'alloy.png', 4),
(1, 'Forged Wheels', 'RAYS', 5000, 0, -35, 4, 0.4, 'forged.png', 4),

-- Spoilers
(2, 'Stock Spoiler', 'Toyota', 0, 0, 0, 0, 0, 'stock.png', 6),
(2, 'GT Wing', 'APR', 4000, 5, 10, 5, 0.3, 'gtwing.png', 6),

-- Bumpers
(3, 'Stock Bumper', 'Toyota', 0, 0, 0, 0, 0, 'stock.png', 5),
(3, 'Bull Bar', 'ARB', 3500, 0, 50, 0, 0, 'bullbar.png', 5),

-- Paint
(4, 'Red Paint', 'Custom', 1000, 0, 0, 0, 0, 'red.png', 1),
(4, 'Blue Paint', 'Custom', 1000, 0, 0, 0, 0, 'blue.png', 1),

-- Engines
(5, 'Stock Engine', 'Toyota', 0, 0, 0, 0, 0, 'engine_stock.png', 2),
(5, 'Turbo Engine', 'Garrett', 15000, 80, 20, 15, 1.0, 'turbo.png', 2);


-- ============================================================
-- SHOP INVENTORY
-- ============================================================

CREATE TABLE shop_inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,

    part_id INT NOT NULL,

    stock INT DEFAULT 0,

    FOREIGN KEY (part_id)
        REFERENCES parts(part_id)
);


INSERT INTO shop_inventory (part_id, stock)
SELECT part_id, 20
FROM parts;


-- ============================================================
-- PLAYER INVENTORY
-- ============================================================

CREATE TABLE player_inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,

    user_id INT NOT NULL,
    part_id INT NOT NULL,

    quantity INT DEFAULT 1,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    FOREIGN KEY (part_id)
        REFERENCES parts(part_id)
);


-- ============================================================
-- INSTALLED PARTS
-- ============================================================

CREATE TABLE vehicle_parts (
    vehicle_id INT NOT NULL,
    category_id INT NOT NULL,
    part_id INT NOT NULL,

    PRIMARY KEY (vehicle_id, category_id),

    FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(vehicle_id)
        ON DELETE CASCADE,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id),

    FOREIGN KEY (part_id)
        REFERENCES parts(part_id)
);


-- ============================================================
-- PURCHASE HISTORY
-- ============================================================

CREATE TABLE purchases (
    purchase_id INT PRIMARY KEY AUTO_INCREMENT,

    user_id INT NOT NULL,
    part_id INT NOT NULL,

    quantity INT DEFAULT 1,

    total_price DECIMAL(10,2),

    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id),

    FOREIGN KEY (part_id)
        REFERENCES parts(part_id)
);


-- ============================================================
-- DEFAULT USERS
-- ============================================================
-- These are the original/demo accounts.
-- New accounts are created through the application's Sign Up
-- screen and should NOT be hard-coded into this SQL file.
--
-- Starting player money is 50,000.
-- nickname is initially the same as username.
-- ============================================================

INSERT INTO users
(username, password, nickname, money, role_id, is_active)
VALUES
('admin', 'admin123', 'admin', 999999.00, 4, 1),
('manager', 'manager123', 'manager', 50000.00, 3, 1),
('player', 'player123', 'player', 50000.00, 2, 1);


-- ============================================================
-- DEFAULT PLAYER VEHICLE
-- ============================================================

INSERT INTO vehicles
(user_id, model_id, nickname)
VALUES
(3, 1, 'My Skyline');


-- ============================================================
-- DEFAULT INSTALLED PARTS
-- ============================================================

INSERT INTO vehicle_parts
(vehicle_id, category_id, part_id)
VALUES
(1, 1, 1),
(1, 2, 4),
(1, 3, 6),
(1, 4, 8),
(1, 5, 10);
