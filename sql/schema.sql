-- =============================================================================
-- Supplier Risk & Tariff-Impact Scorecard: Relational Database Schema
-- Compatible with SQLite, PostgreSQL, Snowflake, and SQL Server
-- =============================================================================

DROP TABLE IF EXISTS quality_defects;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS tariff_scenarios;
DROP TABLE IF EXISTS tariff_reference;
DROP TABLE IF EXISTS suppliers;

-- 1. Suppliers Master Table
CREATE TABLE suppliers (
    Supplier_ID         VARCHAR(20) PRIMARY KEY,
    Supplier_Name       VARCHAR(100) NOT NULL,
    Country             VARCHAR(50) NOT NULL,
    Region              VARCHAR(30) NOT NULL,
    City                VARCHAR(50),
    Primary_Category    VARCHAR(50) NOT NULL,
    Onboarded_Date      DATE NOT NULL,
    USMCA_Qualifying    VARCHAR(10) NOT NULL
);

-- 2. Tariff Reference Table
CREATE TABLE tariff_reference (
    Country                 VARCHAR(50) NOT NULL,
    HS_Code                 VARCHAR(20) NOT NULL,
    Product_Category        VARCHAR(50) NOT NULL,
    Base_MFN_Rate           DECIMAL(5,4) NOT NULL,
    Section_301_Rate        DECIMAL(5,4) NOT NULL,
    Section_122_Surcharge   DECIMAL(5,4) NOT NULL,
    USMCA_Qualifying        VARCHAR(10) NOT NULL,
    Base_Effective_Rate     DECIMAL(5,4) NOT NULL,
    PRIMARY KEY (Country, HS_Code)
);

-- 3. Tariff Scenarios Table
CREATE TABLE tariff_scenarios (
    Scenario_Name       VARCHAR(100) PRIMARY KEY,
    Adjustment_Type     VARCHAR(20) NOT NULL,
    Adjustment_Value    DECIMAL(5,4) NOT NULL,
    Description         TEXT
);

-- 4. Purchase Orders Table (Simulated Coupa export)
CREATE TABLE purchase_orders (
    PO_ID                   VARCHAR(30) NOT NULL,
    Supplier_ID             VARCHAR(20) NOT NULL,
    Product_Category        VARCHAR(50) NOT NULL,
    HS_Code                 VARCHAR(20) NOT NULL,
    PO_Date                 DATE NOT NULL,
    Quantity                INTEGER NOT NULL,
    Unit_Cost_USD           DECIMAL(12,2),
    Incoterm                VARCHAR(20),
    Freight_Mode            VARCHAR(30),
    Promised_Delivery_Date  DATE NOT NULL,
    Actual_Delivery_Date    DATE,
    Customs_Clearance_Days  INTEGER NOT NULL,
    Defect_Flag             VARCHAR(5) NOT NULL,
    PO_Status               VARCHAR(30) NOT NULL,
    FOREIGN KEY (Supplier_ID) REFERENCES suppliers(Supplier_ID)
);

-- 5. Quality Defects Table
CREATE TABLE quality_defects (
    Defect_ID       VARCHAR(30) PRIMARY KEY,
    PO_ID           VARCHAR(30) NOT NULL,
    Supplier_ID     VARCHAR(20) NOT NULL,
    Defect_Type     VARCHAR(100) NOT NULL,
    Defect_Qty      INTEGER NOT NULL,
    Detected_Date   DATE NOT NULL,
    Resolution      VARCHAR(50) NOT NULL,
    FOREIGN KEY (Supplier_ID) REFERENCES suppliers(Supplier_ID)
);

CREATE INDEX idx_po_supplier ON purchase_orders(Supplier_ID);
CREATE INDEX idx_po_dates ON purchase_orders(PO_Date, Promised_Delivery_Date, Actual_Delivery_Date);
