-- -------------------------------------------------------------------
-- Quick Commerce DB - Complete Setup File
-- -------------------------------------------------------------------

-- 1. Create and Use Database
CREATE DATABASE IF NOT EXISTS QuickCommerceDB;
USE QuickCommerceDB;

-- -------------------------------------------------------------------
-- 2. DDL (Table Definitions)
-- -------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS PRODUCT (
    Product_ID INT PRIMARY KEY AUTO_INCREMENT,
    P_Name VARCHAR(255) NOT NULL,
    Description TEXT,
    Price DECIMAL(10, 2) NOT NULL,
    Expiry_Date DATE
);

CREATE TABLE IF NOT EXISTS WAREHOUSE (
    Warehouse_ID INT PRIMARY KEY AUTO_INCREMENT,
    Location VARCHAR(255) NOT NULL,
    Capacity INT
);

-- This is the enhanced Inventory table
CREATE TABLE IF NOT EXISTS Inventory (
    Inventory_ID INT PRIMARY KEY AUTO_INCREMENT,
    Product_ID INT,
    Warehouse_ID INT,
    Quantity INT NOT NULL,
    UNIQUE(Product_ID, Warehouse_ID),
    FOREIGN KEY (Product_ID) REFERENCES PRODUCT(Product_ID) ON DELETE CASCADE,
    FOREIGN KEY (Warehouse_ID) REFERENCES WAREHOUSE(Warehouse_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS DRIVER (
    Driver_ID INT PRIMARY KEY AUTO_INCREMENT,
    D_Name VARCHAR(100) NOT NULL,
    Availability ENUM('Available', 'On-Trip', 'Unavailable') DEFAULT 'Available',
    Vehicle_no VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS FLEET (
    Vehicle_no VARCHAR(20) PRIMARY KEY,
    Availability ENUM('Available', 'In-Use', 'Maintenance') DEFAULT 'Available',
    Location VARCHAR(255),
    Driver_ID INT UNIQUE,
    CONSTRAINT fk_fleet_driver FOREIGN KEY (Driver_ID) REFERENCES DRIVER(Driver_ID) ON DELETE SET NULL
);

ALTER TABLE DRIVER
ADD CONSTRAINT fk_driver_fleet FOREIGN KEY (Vehicle_no) REFERENCES FLEET(Vehicle_no) ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS CUSTOMER (
    Customer_ID INT PRIMARY KEY AUTO_INCREMENT,
    C_Name VARCHAR(100) NOT NULL,
    Email_ID VARCHAR(255) UNIQUE NOT NULL,
    Driver_ID INT,
    Payment_ID INT
);

CREATE TABLE IF NOT EXISTS `ORDER` (
    Order_ID INT PRIMARY KEY AUTO_INCREMENT,
    Items TEXT NULL, -- Modified from original schema
    Order_Total DECIMAL(10, 2) NOT NULL,
    Warehouse_ID INT,
    Status VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (Warehouse_ID) REFERENCES WAREHOUSE(Warehouse_ID) ON DELETE SET NULL
);

-- This is the enhanced Order_Items junction table
CREATE TABLE IF NOT EXISTS ORDER_ITEMS (
    OrderItem_ID INT PRIMARY KEY AUTO_INCREMENT,
    Order_ID INT,
    Product_ID INT,
    Quantity INT NOT NULL,
    FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE,
    FOREIGN KEY (Product_ID) REFERENCES PRODUCT(Product_ID) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS PAYMENT (
    Payment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Payment_mode VARCHAR(50) NOT NULL,
    Trans_date DATETIME NOT NULL,
    Status VARCHAR(50) DEFAULT 'Pending',
    Order_ID INT UNIQUE NOT NULL,
    FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CUST_ORDER (
    Cust_OrderID INT PRIMARY KEY AUTO_INCREMENT,
    Customer_ID INT,
    Order_ID INT,
    FOREIGN KEY (Customer_ID) REFERENCES CUSTOMER(Customer_ID) ON DELETE CASCADE,
    FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Order_History (
    History_ID INT PRIMARY KEY AUTO_INCREMENT,
    Order_ID INT,
    Status VARCHAR(50),
    Log_Time DATETIME NOT NULL,
    FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE
);

-- -------------------------------------------------------------------
-- 3. Required Data & Database Fixes
-- -------------------------------------------------------------------

-- Insert the default warehouse (ID 1) that the GUI relies on
INSERT IGNORE INTO WAREHOUSE (Warehouse_ID, Location, Capacity)
VALUES (1, 'Main Warehouse', 99999);

-- Alter the original 'Items' column to allow NULLs
ALTER TABLE `ORDER`
MODIFY COLUMN Items TEXT NULL;

-- -------------------------------------------------------------------
-- 4. Triggers
-- -------------------------------------------------------------------

DROP TRIGGER IF EXISTS After_OrderStatusUpdate_Log;
DROP TRIGGER IF EXISTS After_ProductSale_UpdateInventory; -- Dropped to fix bug

DELIMITER $$
CREATE TRIGGER After_OrderStatusUpdate_Log
AFTER UPDATE ON `ORDER`
FOR EACH ROW
BEGIN
    IF OLD.Status <> NEW.Status THEN
        INSERT INTO Order_History (Order_ID, Status, Log_Time)
        VALUES (NEW.Order_ID, NEW.Status, NOW());
    END IF;
END$$
DELIMITER ;

-- -------------------------------------------------------------------
-- 5. Stored Procedures
-- -------------------------------------------------------------------

DROP PROCEDURE IF EXISTS PlaceNewOrder;
DROP PROCEDURE IF EXISTS AssignDriverToVehicle;
DROP PROCEDURE IF EXISTS GenerateSalesReport;

-- Procedure: PlaceNewOrder
DELIMITER $$
CREATE PROCEDURE PlaceNewOrder(
    IN p_customerID INT,
    IN p_warehouseID INT,
    IN p_cart_json JSON
)
BEGIN
    DECLARE new_orderID INT;
    DECLARE order_total DECIMAL(10, 2) DEFAULT 0.00;
    DECLARE i INT DEFAULT 0;
    DECLARE num_items INT;
    DECLARE p_id INT;
    DECLARE p_qty INT;
    DECLARE current_stock INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET num_items = JSON_LENGTH(p_cart_json);
    START TRANSACTION;

    -- 1. Check stock
    WHILE i < num_items DO
        SET p_id = JSON_UNQUOTE(JSON_EXTRACT(p_cart_json, CONCAT('$[', i, '].product_id')));
        SET p_qty = JSON_UNQUOTE(JSON_EXTRACT(p_cart_json, CONCAT('$[', i, '].quantity')));

        SELECT Quantity INTO current_stock FROM Inventory 
        WHERE Product_ID = p_id AND Warehouse_ID = 1; -- Using hardcoded WH 1
        
        IF current_stock IS NULL OR current_stock < p_qty THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Not enough stock for one or more items.';
        END IF;
        SET i = i + 1;
    END WHILE;
    
    -- 2. Create order
    INSERT INTO `ORDER` (Warehouse_ID, Status, Order_Total) 
    VALUES (1, 'Pending', 0.00); -- Using hardcoded WH 1
    
    SET new_orderID = LAST_INSERT_ID();

    -- 3. Link customer
    INSERT INTO CUST_ORDER (Customer_ID, Order_ID) VALUES (p_customerID, new_orderID);

    -- 4. Add items, update inventory, calculate total
    SET i = 0;
    WHILE i < num_items DO
        SET p_id = JSON_UNQUOTE(JSON_EXTRACT(p_cart_json, CONCAT('$[', i, '].product_id')));
        SET p_qty = JSON_UNQUOTE(JSON_EXTRACT(p_cart_json, CONCAT('$[', i, '].quantity')));

        INSERT INTO ORDER_ITEMS (Order_ID, Product_ID, Quantity) 
        VALUES (new_orderID, p_id, p_qty);

        UPDATE Inventory SET Quantity = Quantity - p_qty 
        WHERE Product_ID = p_id AND Warehouse_ID = 1; -- Using hardcoded WH 1

        SELECT order_total + (p.Price * p_qty) INTO order_total 
        FROM PRODUCT p WHERE p.Product_ID = p_id;
        
        SET i = i + 1;
    END WHILE;
    
    -- 5. Update order total
    UPDATE `ORDER` SET Order_Total = order_total WHERE Order_ID = new_orderID;

    -- 6. Create payment record
    INSERT INTO PAYMENT (Payment_mode, Trans_date, Status, Order_ID)
    VALUES ('Pending', NOW(), 'Awaiting Payment', new_orderID);

    COMMIT;
END$$
DELIMITER ;

-- Procedure: AssignDriverToVehicle
DELIMITER $$
CREATE PROCEDURE AssignDriverToVehicle(
    IN p_driverID INT,
    IN p_vehicleNo VARCHAR(20)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    UPDATE DRIVER
    SET Availability = 'On-Trip', Vehicle_no = p_vehicleNo
    WHERE Driver_ID = p_driverID AND Availability = 'Available';

    UPDATE FLEET
    SET Availability = 'In-Use', Driver_ID = p_driverID
    WHERE Vehicle_no = p_vehicleNo AND Availability = 'Available';

    COMMIT;
END$$
DELIMITER ;

-- Procedure: GenerateSalesReport
DELIMITER $$
CREATE PROCEDURE GenerateSalesReport(IN p_startDate DATE, IN p_endDate DATE)
BEGIN
    SELECT
        p.Order_ID,
        c.C_Name AS Customer_Name,
        o.Order_Total,
        p.Trans_date AS Payment_Date,
        w.Location AS Warehouse
    FROM PAYMENT p
    JOIN `ORDER` o ON p.Order_ID = o.Order_ID
    JOIN CUST_ORDER co ON o.Order_ID = co.Order_ID
    JOIN CUSTOMER c ON co.Customer_ID = c.Customer_ID
    JOIN WAREHOUSE w ON o.Warehouse_ID = w.Warehouse_ID
    WHERE
        -- Fixed: Removed "p.Status = 'Completed'" to show all orders
        DATE(p.Trans_date) BETWEEN p_startDate AND p_endDate
    ORDER BY
        p.Trans_date DESC;
END$$
DELIMITER ;