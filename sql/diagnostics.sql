-- =============================================================================
-- Supplier Risk & Tariff-Impact Scorecard: Data Quality Audit & Clean Views
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 0. DATA QUALITY AUDIT (Auditing raw ingestion data)
-- -----------------------------------------------------------------------------

-- 0a. Check duplicate PO entries (simulating manual entry re-submissions)
SELECT PO_ID, COUNT(*) AS occurrences
FROM purchase_orders
GROUP BY PO_ID
HAVING COUNT(*) > 1;

-- 0b. Identify records missing Unit_Cost_USD (pending invoice reconciliation)
SELECT COUNT(*) AS missing_unit_cost_rows
FROM purchase_orders
WHERE Unit_Cost_USD IS NULL;

-- 0c. Inspect text casing consistency
SELECT DISTINCT Incoterm FROM purchase_orders;
SELECT DISTINCT Freight_Mode FROM purchase_orders;
SELECT DISTINCT Product_Category FROM purchase_orders;

-- 0d. Deduplicated View: clean_purchase_orders
-- Retains the first occurrence per PO_ID, identical to Excel and Python pipelines.
DROP VIEW IF EXISTS clean_purchase_orders;
CREATE VIEW clean_purchase_orders AS
SELECT * FROM purchase_orders
WHERE rowid IN (
    SELECT MIN(rowid) 
    FROM purchase_orders 
    GROUP BY PO_ID
);
