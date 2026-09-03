# Power BI Implementation & DAX Architecture Guide

This guide details the complete process for ingesting the data model, configuring DAX measures, and creating the 4 core analytical views of the **Supplier Risk & Tariff-Impact Scorecard** in Microsoft Power BI Desktop.

---

## 1. Data Ingestion & Model Architecture

### Source Files
1. **Fact Table (`powerbi_ready_export.csv`)**:
   - 340 deduplicated purchase orders enriched with supplier metadata, baseline tariff rates, landed cost calculations, and lead-time metrics.
2. **Disconnected Parameter Table (`tariff_scenarios.csv`)**:
   - Contains scenario definitions (`Current (Jul 2026)`, `+10% escalation`, `+25% escalation`, `Section 122 sunset`, `Universal 50%`) used for dynamic what-if simulation slicers.

### Data Type Verifications
| Field Name | Source Column | Target Power BI Data Type | Format String |
|:---|:---|:---|:---|
| `PO_ID` | `PO_ID` | Text | Text |
| `PO_Date` | `PO_Date` | Date | `YYYY-MM-DD` |
| `Promised_Delivery_Date` | `Promised_Delivery_Date` | Date | `YYYY-MM-DD` |
| `Actual_Delivery_Date` | `Actual_Delivery_Date` | Date | `YYYY-MM-DD` |
| `Unit_Cost_USD` | `Unit_Cost_USD` | Decimal Number | `$#,##0.00` |
| `Base_Spend_USD` | `Base_Spend_USD` | Decimal Number | `$#,##0` |
| `Landed_Cost_Per_Unit` | `Landed_Cost_Per_Unit` | Decimal Number | `$#,##0.00` |
| `Landed_Spend_USD` | `Landed_Spend_USD` | Decimal Number | `$#,##0` |
| `Tariff_Dollars` | `Tariff_Dollars` | Decimal Number | `$#,##0` |
| `Base_Effective_Rate` | `Base_Effective_Rate` | Decimal Number | `0.0%` |
| `Lead_Time_Days` | `Lead_Time_Days` | Whole Number | `0` |
| `On_Time_Flag` | `On_Time_Flag` | Whole Number | `0` |

---

## 2. Core Dashboard Views & Visual Layouts

### View 1: Executive Overview
- **Header KPI Cards (4 Cards)**:
  1. `Total Landed Spend` (\$48.45M)
  2. `Total Tariff Exposure USD` (\$4.10M)
  3. `On-Time Rate` (81.0%)
  4. `Defect Rate` (5.0%)
- **Visuals**:
  - **Landed Spend Breakdown (Stacked Bar Chart)**: `Supplier_Name` on Y-Axis, `Base Spend` and `Tariff Dollars` on X-Axis. Visually demonstrates China's \$4.1M tariff burden.
  - **Supplier Risk Score Matrix (Table)**: `Supplier_Name`, `Country`, `On-Time Rate`, `Avg Lead Time`, `Landed Spend`, `Composite Risk Score`, `RAG Status` (with Conditional Formatting: Green/Yellow/Red background).

### View 2: Supplier Risk & Lead-Time Volatility
- **Lead-Time Distribution & Volatility (Scatter / Line Chart)**:
  - X-Axis: `Supplier_Name`
  - Y-Axis: `Avg Lead Time (Days)`
  - Error Bars / Bubble Size: `Lead Time StDev (Days)` (highlights China's ±15.4 day unpredictability vs US ±5.8 days).
- **Risk Score Component Radar / Decomposed Bar Chart**:
  - Displays the 4 weighted risk drivers per supplier.

### View 3: Tariff Impact & What-If Scenario Analysis
- **Scenario Slicer**: Dropdown bound to `Tariff_Scenarios[Scenario_Name]`.
- **Comparative Spend Matrix**:
  - Compares `Total Landed Spend` vs `Scenario Landed Spend` and `Scenario Delta vs Baseline Spend`.
- **Scenario Impact Bar Chart**:
  - Shows net financial impact of trade escalation scenarios (+10%, +25%, 50% Universal) on overall procurement cost.

### View 4: Supplier Detail & Historical Trends
- **Monthly Lead-Time Trend (Multi-Line Chart)**:
  - X-Axis: `PO_Year_Month`
  - Y-Axis: `Avg Lead Time (Days)`
  - Legend: `Supplier_Name`
- **Quality & Customs Clearance Breakdown**:
  - Displays `Defect Rate` and `Avg Customs Clearance Days` per origin country.

---

## 3. Parity Verification Across SQL, Excel, and Power BI

All calculations implemented in DAX strictly replicate the SQL queries in `sql/analytics_kpis.sql` and the Excel formulas in `excel/Supplier_Risk_Tariff_Scorecard.xlsx`:
1. **Deduplication Parity**: Evaluates delivered orders only where `Is_First_Occurrence = 1`.
2. **Lead Time Volatility**: Uses population standard deviation `STDEVX.P()`, matching SQLite variance and Excel `SUMPRODUCT` population formulas.
3. **Weighting & Normalization**: Normalizes lead-time volatility with a 20-day cap, weighting on-time at 30%, lead-time volatility at 20%, tariff exposure at 25%, and defect rate at 25%.
