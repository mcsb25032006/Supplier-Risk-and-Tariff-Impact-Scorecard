-- =============================================================================
-- Supplier Risk & Tariff-Impact Scorecard: Analytical & Diagnostic SQL Queries
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. On-Time Delivery Performance by Supplier (Delivered POs only)
-- -----------------------------------------------------------------------------
SELECT
    s.Supplier_Name,
    s.Country,
    s.Region,
    COUNT(*) AS delivered_pos,
    SUM(CASE WHEN julianday(p.Actual_Delivery_Date) <= julianday(p.Promised_Delivery_Date) THEN 1 ELSE 0 END) AS on_time_pos,
    ROUND(100.0 * SUM(CASE WHEN julianday(p.Actual_Delivery_Date) <= julianday(p.Promised_Delivery_Date) THEN 1 ELSE 0 END) / COUNT(*), 2) AS on_time_rate_pct
FROM clean_purchase_orders p
JOIN suppliers s ON p.Supplier_ID = s.Supplier_ID
WHERE p.PO_Status = 'Delivered'
GROUP BY s.Supplier_Name, s.Country, s.Region
ORDER BY on_time_rate_pct DESC;


-- -----------------------------------------------------------------------------
-- 2. Lead Time Average, Median, and Volatility (Standard Deviation)
-- -----------------------------------------------------------------------------
WITH lead_times AS (
    SELECT
        p.Supplier_ID,
        (julianday(p.Actual_Delivery_Date) - julianday(p.PO_Date)) AS lead_time_days
    FROM clean_purchase_orders p
    WHERE p.PO_Status = 'Delivered'
)
SELECT
    s.Supplier_Name,
    COUNT(*) AS n_pos,
    ROUND(AVG(lt.lead_time_days), 1) AS avg_lead_time_days,
    ROUND(SQRT(AVG(lead_time_days * lead_time_days) - AVG(lead_time_days) * AVG(lead_time_days)), 1) AS lead_time_stdev_days
FROM lead_times lt
JOIN suppliers s ON lt.Supplier_ID = s.Supplier_ID
GROUP BY s.Supplier_Name
ORDER BY lead_time_stdev_days DESC;


-- -----------------------------------------------------------------------------
-- 3. Quoted Unit Cost vs Total Landed Cost per Unit
-- -----------------------------------------------------------------------------
WITH landed AS (
    SELECT
        p.PO_ID,
        p.Supplier_ID,
        s.Country,
        p.Product_Category,
        p.HS_Code,
        p.Unit_Cost_USD,
        p.Quantity,
        t.Base_Effective_Rate,
        p.Unit_Cost_USD * (1 + t.Base_Effective_Rate) AS landed_cost_per_unit
    FROM clean_purchase_orders p
    JOIN suppliers s ON p.Supplier_ID = s.Supplier_ID
    JOIN tariff_reference t ON s.Country = t.Country AND p.HS_Code = t.HS_Code
    WHERE p.Unit_Cost_USD IS NOT NULL AND p.PO_Status = 'Delivered'
)
SELECT
    s.Supplier_Name,
    ROUND(AVG(l.Unit_Cost_USD), 2) AS avg_quoted_unit_cost,
    ROUND(AVG(l.Base_Effective_Rate) * 100, 1) AS avg_tariff_rate_pct,
    ROUND(AVG(l.landed_cost_per_unit), 2) AS avg_landed_cost_per_unit,
    ROUND(SUM(l.Unit_Cost_USD * l.Quantity), 2) AS total_base_spend,
    ROUND(SUM(l.landed_cost_per_unit * l.Quantity), 2) AS total_landed_spend,
    ROUND(SUM((l.landed_cost_per_unit - l.Unit_Cost_USD) * l.Quantity), 2) AS total_tariff_dollars
FROM landed l
JOIN suppliers s ON l.Supplier_ID = s.Supplier_ID
GROUP BY s.Supplier_Name
ORDER BY total_landed_spend DESC;


-- -----------------------------------------------------------------------------
-- 4. Defect and Quality Metrics by Supplier
-- -----------------------------------------------------------------------------
SELECT
    s.Supplier_Name,
    COUNT(DISTINCT p.PO_ID) AS delivered_pos,
    SUM(CASE WHEN p.Defect_Flag = 'Y' THEN 1 ELSE 0 END) AS defect_pos,
    ROUND(100.0 * SUM(CASE WHEN p.Defect_Flag = 'Y' THEN 1 ELSE 0 END) / COUNT(DISTINCT p.PO_ID), 2) AS defect_rate_pct,
    COALESCE(SUM(qd.Defect_Qty), 0) AS total_defect_units
FROM clean_purchase_orders p
JOIN suppliers s ON p.Supplier_ID = s.Supplier_ID
LEFT JOIN quality_defects qd ON p.PO_ID = qd.PO_ID
WHERE p.PO_Status = 'Delivered'
GROUP BY s.Supplier_Name
ORDER BY defect_rate_pct DESC;


-- -----------------------------------------------------------------------------
-- 5. Comprehensive Composite Supplier Risk Score in SQL
-- Recreates the Python / Excel / DAX formula:
-- Risk = 0.30*(1-OnTime)*100 + 0.20*MIN(StDev/20*100,100) + 0.25*(TariffExp)*100 + 0.25*(DefectRate)*100
-- -----------------------------------------------------------------------------
WITH supplier_metrics AS (
    SELECT
        s.Supplier_ID,
        s.Supplier_Name,
        s.Country,
        COUNT(*) AS delivered_pos,
        SUM(CASE WHEN julianday(p.Actual_Delivery_Date) <= julianday(p.Promised_Delivery_Date) THEN 1.0 ELSE 0.0 END) / COUNT(*) AS on_time_rate,
        AVG(julianday(p.Actual_Delivery_Date) - julianday(p.PO_Date)) AS avg_lead_time,
        SQRT(AVG((julianday(p.Actual_Delivery_Date) - julianday(p.PO_Date))*(julianday(p.Actual_Delivery_Date) - julianday(p.PO_Date))) - 
             AVG(julianday(p.Actual_Delivery_Date) - julianday(p.PO_Date))*AVG(julianday(p.Actual_Delivery_Date) - julianday(p.PO_Date))) AS lead_time_stdev,
        SUM(p.Unit_Cost_USD * p.Quantity) AS base_spend,
        SUM(p.Unit_Cost_USD * (1 + t.Base_Effective_Rate) * p.Quantity) AS landed_spend,
        SUM(CASE WHEN p.Defect_Flag = 'Y' THEN 1.0 ELSE 0.0 END) / COUNT(*) AS defect_rate
    FROM clean_purchase_orders p
    JOIN suppliers s ON p.Supplier_ID = s.Supplier_ID
    JOIN tariff_reference t ON s.Country = t.Country AND p.HS_Code = t.HS_Code
    WHERE p.PO_Status = 'Delivered' AND p.Unit_Cost_USD IS NOT NULL
    GROUP BY s.Supplier_ID, s.Supplier_Name, s.Country
),
scored AS (
    SELECT
        Supplier_ID,
        Supplier_Name,
        Country,
        ROUND(on_time_rate * 100, 1) AS on_time_pct,
        ROUND(avg_lead_time, 1) AS avg_lead_time_days,
        ROUND(lead_time_stdev, 1) AS lead_time_stdev_days,
        ROUND(base_spend, 2) AS base_spend,
        ROUND(landed_spend, 2) AS landed_spend,
        ROUND(100.0 * (landed_spend - base_spend) / base_spend, 1) AS tariff_exposure_pct,
        ROUND(defect_rate * 100, 1) AS defect_rate_pct,
        ROUND(
            0.30 * (1.0 - on_time_rate) * 100.0 +
            0.20 * (CASE WHEN (lead_time_stdev / 20.0 * 100.0) > 100.0 THEN 100.0 ELSE (lead_time_stdev / 20.0 * 100.0) END) +
            0.25 * ((landed_spend - base_spend) / base_spend * 100.0) +
            0.25 * (defect_rate * 100.0),
            1
        ) AS composite_risk_score
    FROM supplier_metrics
)
SELECT
    Supplier_ID,
    Supplier_Name,
    Country,
    on_time_pct,
    avg_lead_time_days,
    lead_time_stdev_days,
    base_spend,
    landed_spend,
    tariff_exposure_pct,
    defect_rate_pct,
    composite_risk_score,
    CASE
        WHEN composite_risk_score >= 30.0 THEN 'Red'
        WHEN composite_risk_score >= 15.0 THEN 'Yellow'
        ELSE 'Green'
    END AS rag_status
FROM scored
ORDER BY composite_risk_score ASC;
