-- ============================================================
-- MEDICINE EXPIRY TRACKER — COMPLETE DATABASE SCHEMA
-- DBMS Mini Project | DSATM | AI & ML | 4th Semester
-- ============================================================

DROP DATABASE IF EXISTS medicine_tracker;
CREATE DATABASE medicine_tracker;
USE medicine_tracker;

-- ============================================================
-- TABLE 1: Medicine
-- ============================================================
CREATE TABLE Medicine (
    medicine_id     INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(100) NOT NULL,
    category        VARCHAR(50)  NOT NULL,
    dosage_form     VARCHAR(30)  NOT NULL,
    manufacturer    VARCHAR(100) NOT NULL,
    min_stock_level INT          NOT NULL DEFAULT 10,
    description     VARCHAR(255),
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_min_stock CHECK (min_stock_level > 0)
);

-- ============================================================
-- TABLE 2: Supplier
-- ============================================================
CREATE TABLE Supplier (
    supplier_id     INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(100) NOT NULL,
    contact_number  VARCHAR(15)  NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    city            VARCHAR(50)  NOT NULL,
    state           VARCHAR(50)  NOT NULL DEFAULT 'Karnataka',
    gst_number      VARCHAR(20)  UNIQUE,
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 3: Batch
-- ============================================================
CREATE TABLE Batch (
    batch_id            INT PRIMARY KEY AUTO_INCREMENT,
    medicine_id         INT            NOT NULL,
    supplier_id         INT            NOT NULL,
    batch_number        VARCHAR(50)    NOT NULL UNIQUE,
    purchase_date       DATE           NOT NULL,
    manufacture_date    DATE           NOT NULL,
    expiry_date         DATE           NOT NULL,
    quantity_purchased  INT            NOT NULL,
    quantity_remaining  INT            NOT NULL,
    unit_price          DECIMAL(10,2)  NOT NULL,
    created_at          TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medicine_id) REFERENCES Medicine(medicine_id) ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id) ON DELETE CASCADE,
    CONSTRAINT chk_qty_purchased  CHECK (quantity_purchased > 0),
    CONSTRAINT chk_qty_remaining  CHECK (quantity_remaining >= 0),
    CONSTRAINT chk_unit_price     CHECK (unit_price > 0)
);

-- ============================================================
-- TABLE 4: Stock
-- ============================================================
CREATE TABLE Stock (
    stock_id            INT PRIMARY KEY AUTO_INCREMENT,
    medicine_id         INT       NOT NULL UNIQUE,
    current_quantity    INT       NOT NULL DEFAULT 0,
    last_updated        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (medicine_id) REFERENCES Medicine(medicine_id) ON DELETE CASCADE,
    CONSTRAINT chk_current_qty CHECK (current_quantity >= 0)
);

-- ============================================================
-- TABLE 5: Alert
-- ============================================================
CREATE TABLE Alert (
    alert_id        INT PRIMARY KEY AUTO_INCREMENT,
    medicine_id     INT         NOT NULL,
    batch_id        INT,
    alert_type      ENUM('EXPIRY_CRITICAL','EXPIRY_WARNING','LOW_STOCK') NOT NULL,
    alert_message   TEXT        NOT NULL,
    created_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    is_resolved     BOOLEAN     DEFAULT FALSE,
    resolved_at     TIMESTAMP   NULL,
    FOREIGN KEY (medicine_id) REFERENCES Medicine(medicine_id) ON DELETE CASCADE,
    FOREIGN KEY (batch_id)    REFERENCES Batch(batch_id)    ON DELETE SET NULL
);

-- ============================================================
-- TABLE 6: Users
-- ============================================================
CREATE TABLE Users (
    user_id     INT PRIMARY KEY AUTO_INCREMENT,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    role        ENUM('admin','staff') NOT NULL DEFAULT 'staff',
    full_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(100) UNIQUE,
    is_active   BOOLEAN      DEFAULT TRUE,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_batch_expiry     ON Batch(expiry_date);
CREATE INDEX idx_batch_medicine   ON Batch(medicine_id);
CREATE INDEX idx_alert_resolved   ON Alert(is_resolved);
CREATE INDEX idx_alert_medicine   ON Alert(medicine_id);
CREATE INDEX idx_stock_medicine   ON Stock(medicine_id);

-- ============================================================
-- ASSERTIONS (simulated via BEFORE triggers)
-- ============================================================
DELIMITER $$

-- Assertion 1: expiry_date must be after manufacture_date
CREATE TRIGGER assert_expiry_after_manufacture
BEFORE INSERT ON Batch FOR EACH ROW
BEGIN
    IF NEW.expiry_date <= NEW.manufacture_date THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ASSERTION FAILED: Expiry date must be after manufacture date';
    END IF;
END $$

-- Assertion 2: stock quantity must never go negative
CREATE TRIGGER assert_no_negative_stock
BEFORE UPDATE ON Stock FOR EACH ROW
BEGIN
    IF NEW.current_quantity < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ASSERTION FAILED: Stock quantity cannot be negative';
    END IF;
END $$

-- Assertion 3: unit_price must be greater than zero (on UPDATE too)
CREATE TRIGGER assert_positive_price_update
BEFORE UPDATE ON Batch FOR EACH ROW
BEGIN
    IF NEW.unit_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ASSERTION FAILED: Unit price must be greater than zero';
    END IF;
END $$

-- Assertion 4: one stock record per medicine (prevent duplicate inserts)
CREATE TRIGGER assert_one_stock_per_medicine
BEFORE INSERT ON Stock FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM Stock WHERE medicine_id = NEW.medicine_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ASSERTION FAILED: A medicine can only have one stock record';
    END IF;
END $$

-- Assertion 5: quantity_remaining cannot exceed quantity_purchased
CREATE TRIGGER assert_remaining_lte_purchased
BEFORE UPDATE ON Batch FOR EACH ROW
BEGIN
    IF NEW.quantity_remaining > NEW.quantity_purchased THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ASSERTION FAILED: Remaining quantity cannot exceed purchased quantity';
    END IF;
END $$

DELIMITER ;

-- ============================================================
-- BUSINESS LOGIC TRIGGERS (AFTER)
-- ============================================================
DELIMITER $$

-- Trigger 1: Auto expiry alert on new batch insert
CREATE TRIGGER trg_expiry_alert
AFTER INSERT ON Batch FOR EACH ROW
BEGIN
    DECLARE days_left INT;
    SET days_left = DATEDIFF(NEW.expiry_date, CURDATE());
    IF days_left <= 30 THEN
        INSERT INTO Alert (medicine_id, batch_id, alert_type, alert_message)
        VALUES (NEW.medicine_id, NEW.batch_id, 'EXPIRY_CRITICAL',
            CONCAT('CRITICAL: Batch ', NEW.batch_number, ' expires in ', days_left, ' days on ', NEW.expiry_date));
    ELSEIF days_left <= 90 THEN
        INSERT INTO Alert (medicine_id, batch_id, alert_type, alert_message)
        VALUES (NEW.medicine_id, NEW.batch_id, 'EXPIRY_WARNING',
            CONCAT('WARNING: Batch ', NEW.batch_number, ' expires in ', days_left, ' days on ', NEW.expiry_date));
    END IF;
END $$

-- Trigger 2: Auto low-stock alert on stock update
CREATE TRIGGER trg_low_stock_alert
AFTER UPDATE ON Stock FOR EACH ROW
BEGIN
    DECLARE min_lvl INT;
    SELECT min_stock_level INTO min_lvl
    FROM Medicine WHERE medicine_id = NEW.medicine_id;
    IF NEW.current_quantity < min_lvl AND OLD.current_quantity >= min_lvl THEN
        INSERT INTO Alert (medicine_id, alert_type, alert_message)
        VALUES (NEW.medicine_id, 'LOW_STOCK',
            CONCAT('LOW STOCK: Only ', NEW.current_quantity, ' units remaining. Minimum required: ', min_lvl));
    END IF;
END $$

DELIMITER ;

-- ============================================================
-- VIEWS
-- ============================================================

CREATE VIEW ExpiredMedicines AS
SELECT m.medicine_id, m.name AS medicine_name, m.category,
       b.batch_id, b.batch_number, b.expiry_date,
       b.quantity_remaining, s.name AS supplier_name,
       DATEDIFF(CURDATE(), b.expiry_date) AS days_expired
FROM Batch b
JOIN Medicine m ON b.medicine_id = m.medicine_id
JOIN Supplier s ON b.supplier_id = s.supplier_id
WHERE b.expiry_date < CURDATE();

CREATE VIEW NearExpiryIn30Days AS
SELECT m.name AS medicine_name, m.category,
       b.batch_number, b.expiry_date, b.quantity_remaining,
       s.name AS supplier_name, s.contact_number,
       DATEDIFF(b.expiry_date, CURDATE()) AS days_remaining
FROM Batch b
JOIN Medicine m ON b.medicine_id = m.medicine_id
JOIN Supplier s ON b.supplier_id = s.supplier_id
WHERE DATEDIFF(b.expiry_date, CURDATE()) BETWEEN 0 AND 30
ORDER BY b.expiry_date ASC;

CREATE VIEW NearExpiryIn90Days AS
SELECT m.name AS medicine_name, m.category,
       b.batch_number, b.expiry_date, b.quantity_remaining,
       s.name AS supplier_name,
       DATEDIFF(b.expiry_date, CURDATE()) AS days_remaining
FROM Batch b
JOIN Medicine m ON b.medicine_id = m.medicine_id
JOIN Supplier s ON b.supplier_id = s.supplier_id
WHERE DATEDIFF(b.expiry_date, CURDATE()) BETWEEN 0 AND 90
ORDER BY b.expiry_date ASC;

CREATE VIEW LowStockMedicines AS
SELECT m.medicine_id, m.name AS medicine_name, m.category,
       st.current_quantity, m.min_stock_level,
       (m.min_stock_level - st.current_quantity) AS shortage
FROM Stock st
JOIN Medicine m ON st.medicine_id = m.medicine_id
WHERE st.current_quantity < m.min_stock_level;

CREATE VIEW ActiveAlerts AS
SELECT a.alert_id, m.name AS medicine_name, b.batch_number,
       a.alert_type, a.alert_message, a.created_at
FROM Alert a
JOIN Medicine m ON a.medicine_id = m.medicine_id
LEFT JOIN Batch b ON a.batch_id = b.batch_id
WHERE a.is_resolved = FALSE
ORDER BY a.created_at DESC;

CREATE VIEW SupplierBatchHistory AS
SELECT s.supplier_id, s.name AS supplier_name, s.city,
       m.name AS medicine_name, b.batch_number,
       b.purchase_date, b.expiry_date,
       b.quantity_purchased, b.unit_price,
       (b.quantity_purchased * b.unit_price) AS total_value
FROM Batch b
JOIN Supplier s ON b.supplier_id = s.supplier_id
JOIN Medicine m ON b.medicine_id = m.medicine_id
ORDER BY s.name, b.purchase_date DESC;

-- ============================================================
-- STORED PROCEDURES
-- ============================================================
DELIMITER $$

-- Procedure 1: Full medicine report
CREATE PROCEDURE GetMedicineReport(IN p_medicine_id INT)
BEGIN
    SELECT m.name, m.category, m.dosage_form, m.manufacturer,
           st.current_quantity, m.min_stock_level, st.last_updated
    FROM Medicine m
    JOIN Stock st ON m.medicine_id = st.medicine_id
    WHERE m.medicine_id = p_medicine_id;

    SELECT b.batch_number, b.expiry_date, b.quantity_remaining,
           s.name AS supplier, DATEDIFF(b.expiry_date, CURDATE()) AS days_left
    FROM Batch b
    JOIN Supplier s ON b.supplier_id = s.supplier_id
    WHERE b.medicine_id = p_medicine_id
    ORDER BY b.expiry_date ASC;

    SELECT alert_type, alert_message, created_at
    FROM Alert
    WHERE medicine_id = p_medicine_id AND is_resolved = FALSE;
END $$

-- Procedure 2: Role-based alert resolution (admin only)
CREATE PROCEDURE ResolveAlert(IN p_alert_id INT, IN p_role VARCHAR(20))
BEGIN
    IF p_role != 'admin' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ACCESS DENIED: Only admin can resolve alerts';
    ELSE
        UPDATE Alert
        SET is_resolved = TRUE, resolved_at = NOW()
        WHERE alert_id = p_alert_id;
        SELECT ROW_COUNT() AS rows_updated;
    END IF;
END $$

-- Procedure 3: Dashboard summary stats
CREATE PROCEDURE GetDashboardStats()
BEGIN
    SELECT
        (SELECT COUNT(*) FROM Medicine) AS total_medicines,
        (SELECT COUNT(*) FROM Supplier) AS total_suppliers,
        (SELECT COUNT(*) FROM Batch WHERE expiry_date >= CURDATE()) AS active_batches,
        (SELECT COUNT(*) FROM Alert WHERE is_resolved = FALSE) AS active_alerts,
        (SELECT COUNT(*) FROM Alert WHERE alert_type='EXPIRY_CRITICAL' AND is_resolved=FALSE) AS critical_alerts,
        (SELECT COUNT(*) FROM LowStockMedicines) AS low_stock_count,
        (SELECT COUNT(*) FROM ExpiredMedicines) AS expired_count;
END $$

DELIMITER ;

-- ============================================================
-- SAMPLE DATA — Medicine (10 records)
-- ============================================================
INSERT INTO Medicine (name, category, dosage_form, manufacturer, min_stock_level, description) VALUES
('Paracetamol 500mg',      'Analgesic',     'Tablet',    'Sun Pharma',        20, 'Used for fever and mild pain relief'),
('Amoxicillin 250mg',      'Antibiotic',    'Capsule',   'Cipla Ltd',         15, 'Broad-spectrum antibiotic'),
('Metformin 500mg',        'Antidiabetic',  'Tablet',    'Dr. Reddys Labs',   25, 'Used for type 2 diabetes management'),
('Atorvastatin 10mg',      'Antilipemic',   'Tablet',    'Lupin Ltd',         10, 'Cholesterol-lowering medication'),
('Cetirizine 10mg',        'Antihistamine', 'Tablet',    'Mankind Pharma',    15, 'For allergy and cold symptoms'),
('Omeprazole 20mg',        'Antacid',       'Capsule',   'Zydus Cadila',      20, 'For acid reflux and ulcers'),
('Azithromycin 500mg',     'Antibiotic',    'Tablet',    'Cipla Ltd',         10, 'Z-pack antibiotic for infections'),
('Amlodipine 5mg',         'Antihypertensive','Tablet',  'Sun Pharma',        15, 'For high blood pressure'),
('Pantoprazole 40mg',      'Antacid',       'Tablet',    'Torrent Pharma',    20, 'Proton pump inhibitor'),
('Vitamin D3 60000 IU',    'Supplement',    'Capsule',   'Abbott India',      10, 'Weekly vitamin D supplement');

-- ============================================================
-- SAMPLE DATA — Supplier (10 records)
-- ============================================================
INSERT INTO Supplier (name, contact_number, email, city, state, gst_number) VALUES
('MedSupply India Pvt Ltd',   '9876543210', 'medsupply@gmail.com',      'Bangalore', 'Karnataka', 'GST29AAACM1234A1Z5'),
('HealthCare Distributors',   '9845001122', 'healthcare@yahoo.com',     'Mumbai',    'Maharashtra','GST27AABCH5678B2Y3'),
('PharmaLink Solutions',      '9901234567', 'pharmalink@gmail.com',     'Chennai',   'Tamil Nadu', 'GST33AACCP9012C3X1'),
('Apollo Medical Supplies',   '9812345678', 'apollo.sup@gmail.com',     'Hyderabad', 'Telangana',  'GST36AAAAP3456D4W2'),
('BioMed Traders',            '9923456789', 'biomed@hotmail.com',       'Pune',      'Maharashtra','GST27AABCB7890E5V4'),
('Karnataka Drug House',      '9734567890', 'kdh@gmail.com',            'Belagavi',  'Karnataka',  'GST29AAACK2345F6U6'),
('National Pharma Corp',      '9645678901', 'national@gmail.com',       'Delhi',     'Delhi',      'GST07AAACP6789G7T7'),
('Southern Medical Agency',   '9556789012', 'southern@gmail.com',       'Kochi',     'Kerala',     'GST32AABCS1234H8S8'),
('Sunrise Drug Distributors', '9467890123', 'sunrise@gmail.com',        'Ahmedabad', 'Gujarat',    'GST24AAASD5678I9R9'),
('Vijay Medical Stores',      '9378901234', 'vijay.med@gmail.com',      'Mysuru',    'Karnataka',  'GST29AAACV9012J0Q0');

-- ============================================================
-- SAMPLE DATA — Users (5 records)
-- ============================================================
INSERT INTO Users (username, password, role, full_name, email) VALUES
('admin01',  'admin@123',  'admin', 'Store Owner Ramesh',     'ramesh@medtracker.com'),
('admin02',  'admin@456',  'admin', 'Manager Suresh',          'suresh@medtracker.com'),
('staff01',  'staff@123',  'staff', 'Pharmacist Ravi Kumar',   'ravi@medtracker.com'),
('staff02',  'staff@456',  'staff', 'Counter Staff Meena',     'meena@medtracker.com'),
('staff03',  'staff@789',  'staff', 'Pharmacist Priya Singh',  'priya@medtracker.com');

-- ============================================================
-- SAMPLE DATA — Batch (12 records — mix of expired, near-expiry, valid)
-- ============================================================
INSERT INTO Batch (medicine_id, supplier_id, batch_number, purchase_date, manufacture_date, expiry_date, quantity_purchased, quantity_remaining, unit_price) VALUES
(1,  1,  'PARA-2024-001', '2024-01-15', '2024-01-01', '2026-01-01',  500, 120, 1.20),
(1,  6,  'PARA-2024-002', '2024-06-01', '2024-05-01', '2024-12-01',  300,  80, 1.10),
(2,  2,  'AMOX-2024-001', '2024-03-10', '2024-02-01', '2026-02-01',  200,  95, 8.50),
(3,  4,  'METF-2024-001', '2024-02-20', '2024-01-15', '2025-06-01',  400, 210, 3.20),
(4,  3,  'ATOR-2024-001', '2024-04-05', '2024-03-01', '2026-03-01',  150,  88, 12.50),
(5,  5,  'CETI-2024-001', '2024-05-15', '2024-04-01', '2025-04-01',  250, 180, 2.80),
(6,  7,  'OMEP-2024-001', '2024-01-20', '2024-01-01', '2025-01-01',  180,  45, 6.40),
(7,  8,  'AZIT-2024-001', '2024-07-01', '2024-06-01', '2026-06-01',  100,  70, 22.00),
(8,  9,  'AMLO-2024-001', '2024-03-25', '2024-03-01', '2026-03-01',  200, 155, 5.75),
(9,  10, 'PANT-2024-001', '2024-08-10', '2024-07-01', '2026-07-01',  300, 240, 7.20),
(10, 1,  'VITD-2024-001', '2024-09-01', '2024-08-01', '2025-08-01',   80,  35, 45.00),
(2,  2,  'AMOX-2025-001', '2025-01-10', '2024-12-01', '2027-12-01',  250, 200, 9.00);

-- ============================================================
-- SAMPLE DATA — Stock (10 records — one per medicine)
-- ============================================================
INSERT INTO Stock (medicine_id, current_quantity) VALUES
(1,  200),
(2,  295),
(3,  210),
(4,   88),
(5,  180),
(6,   45),
(7,   70),
(8,  155),
(9,  240),
(10,  35);

-- ============================================================
-- SAMPLE DATA — Alert (manually add some for demo)
-- ============================================================
INSERT INTO Alert (medicine_id, batch_id, alert_type, alert_message, is_resolved) VALUES
(6,  7,  'EXPIRY_WARNING',  'WARNING: Batch OMEP-2024-001 expiring soon — check and return to supplier', FALSE),
(4,  NULL,'LOW_STOCK',       'LOW STOCK: Atorvastatin 10mg has only 88 units. Minimum required: 10. Reorder soon.', FALSE),
(10, 11, 'EXPIRY_WARNING',  'WARNING: Batch VITD-2024-001 for Vitamin D3 expiring in under 90 days', FALSE),
(3,  4,  'EXPIRY_WARNING',  'WARNING: Batch METF-2024-001 for Metformin expiring on 2025-06-01', TRUE);

-- ============================================================
-- AGGREGATE + JOIN + SUBQUERY DEMO QUERIES
-- (These are for reference/demo — not executed at setup time)
-- ============================================================

-- Q1: Total stock value per medicine (JOIN + Aggregate)
-- SELECT m.name, SUM(b.quantity_remaining * b.unit_price) AS stock_value
-- FROM Medicine m JOIN Batch b ON m.medicine_id = b.medicine_id
-- GROUP BY m.name ORDER BY stock_value DESC;

-- Q2: Supplier who supplied most batches (JOIN + COUNT + GROUP BY)
-- SELECT s.name, COUNT(b.batch_id) AS total_batches
-- FROM Supplier s JOIN Batch b ON s.supplier_id = b.supplier_id
-- GROUP BY s.name ORDER BY total_batches DESC LIMIT 1;

-- Q3: Medicines with NO active (non-expired) batch (Subquery)
-- SELECT name FROM Medicine
-- WHERE medicine_id NOT IN (
--     SELECT DISTINCT medicine_id FROM Batch WHERE expiry_date >= CURDATE()
-- );

-- Q4: Average purchase price per category (AVG + GROUP BY)
-- SELECT m.category, AVG(b.unit_price) AS avg_price
-- FROM Medicine m JOIN Batch b ON m.medicine_id = b.medicine_id
-- GROUP BY m.category;

-- Q5: Count of each alert type (COUNT + GROUP BY)
-- SELECT alert_type, COUNT(*) AS total FROM Alert GROUP BY alert_type;

SELECT 'Database setup complete!' AS Status;
