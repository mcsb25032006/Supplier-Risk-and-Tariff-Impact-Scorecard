# Data Model Documentation

## Entity-Relationship Overview

The data model reflects a modern enterprise ERP/Procurement architecture (modeled on Coupa Purchase-to-Pay exports).

```
+-------------------+             +-----------------------+
|     suppliers     | 1         * |    purchase_orders    |
+-------------------+-------------+-----------------------+
| PK Supplier_ID    |             | PK PO_ID              |
|    Supplier_Name  |             | FK Supplier_ID        |
|    Country        |             |    Product_Category   |
|    Region         |             |    HS_Code            |
|    City           |             |    PO_Date            |
|    Primary_Cat    |             |    Quantity           |
|    Onboarded_Date |             |    Unit_Cost_USD      |
|    USMCA_Qual     |             |    Incoterm           |
+-------------------+             |    Freight_Mode       |
                                  |    Promised_Deliv_Date|
                                  |    Actual_Deliv_Date  |
                                  |    Customs_Days       |
                                  |    Defect_Flag        |
                                  |    PO_Status          |
                                  +-----------------------+
                                              | 1
                                              |
                                              | *
+-------------------+             +-----------------------+
| tariff_reference  |             |    quality_defects    |
+-------------------+             +-----------------------+
| PK Country        |             | PK Defect_ID          |
| PK HS_Code        |             | FK PO_ID              |
|    Product_Cat    |             | FK Supplier_ID        |
|    Base_MFN_Rate  |             |    Defect_Type        |
|    Sec_301_Rate   |             |    Defect_Qty         |
|    Sec_122_Surch  |             |    Detected_Date      |
|    Base_Eff_Rate  |             |    Resolution         |
+-------------------+             +-----------------------+
```

---

## Data Dictionary

### 1. `suppliers` (Supplier Master)
| Column Name | Data Type | Constraint | Description | Example |
|:---|:---|:---|:---|:---|
| `Supplier_ID` | String | Primary Key | Unique supplier identifier | `SUP-001` |
| `Supplier_Name` | String | Not Null | Legal business entity name | `TitanForge Components` |
| `Country` | String | Not Null | Origin manufacturing country | `United States` |
| `Region` | String | Enum | Geographic procurement region (`Domestic`, `Nearshore`, `Offshore`) | `Domestic` |
| `City` | String | Nullable | Manufacturing facility city | `Columbus, OH` |
| `Primary_Category` | String | Not Null | Primary component category supplied | `GPU Servers` |
| `Onboarded_Date` | Date | Not Null | Vendor onboarding effective date | `2023-03-14` |
| `USMCA_Qualifying` | String | Enum (`Y`, `N`, `N/A`) | Free-trade agreement qualification | `N/A` |

### 2. `purchase_orders` (Transaction & Shipment Log)
| Column Name | Data Type | Constraint | Description | Example |
|:---|:---|:---|:---|:---|
| `PO_ID` | String | Not Null | Purchase order identifier | `PO-1042` |
| `Supplier_ID` | String | Foreign Key | Reference to `suppliers.Supplier_ID` | `SUP-002` |
| `Product_Category` | String | Not Null | Commodity line item | `Network Switches` |
| `HS_Code` | String | Not Null | Harmonized System trade tariff code | `8517.62` |
| `PO_Date` | Date | Not Null | Order issuance date | `2025-04-12` |
| `Quantity` | Integer | > 0 | Units ordered | `16` |
| `Unit_Cost_USD` | Decimal | Nullable | Quoted unit purchase cost | `$4,250.00` |
| `Incoterm` | String | Standard | International Commercial Terms | `FOB` |
| `Freight_Mode` | String | Standard | Logistics transport method | `Truck` |
| `Promised_Delivery_Date` | Date | Not Null | Contractual supplier promised date | `2025-04-30` |
| `Actual_Delivery_Date` | Date | Nullable | Warehouse receipt date (blank if In Transit) | `2025-04-28` |
| `Customs_Clearance_Days`| Integer| >= 0 | Days held in customs clearance | `2` |
| `Defect_Flag` | String | Enum (`Y`, `N`)| Quality inspection defect indicator | `N` |
| `PO_Status` | String | Enum | Order lifecycle status (`Delivered`, `In Transit`) | `Delivered` |

### 3. `tariff_reference` (Trade Policy Schedule)
| Column Name | Data Type | Description | Example |
|:---|:---|:---|:---|
| `Country` | String | Origin country | `China` |
| `HS_Code` | String | Harmonized System code | `8471.50` |
| `Product_Category` | String | Product description | `GPU Servers` |
| `Base_MFN_Rate` | Decimal | Most-Favored-Nation standard tariff rate | `0.00` |
| `Section_301_Rate` | Decimal | Trade Act Section 301 China tariff rate | `0.25` (25%) |
| `Section_122_Surcharge` | Decimal | Section 122 balance of payments surcharge | `0.10` (10%) |
| `Base_Effective_Rate` | Decimal | Net baseline effective tariff rate | `0.35` (35%) |

### 4. `tariff_scenarios` (What-If Parameters)
| Column Name | Data Type | Description | Example |
|:---|:---|:---|:---|
| `Scenario_Name` | String | Scenario identifier | `+10% escalation` |
| `Adjustment_Type` | String | `Additive` or `Absolute` override | `Additive` |
| `Adjustment_Value` | Decimal | Tariff rate delta or absolute rate | `0.10` |
| `Description` | String | Policy scenario narrative | `Moderate trade penalty increase` |

### 5. `quality_defects` (Defect Audit Log)
| Column Name | Data Type | Description | Example |
|:---|:---|:---|:---|
| `Defect_ID` | String | Primary defect tracking identifier | `DEF-0004` |
| `PO_ID` | String | Associated purchase order | `PO-1088` |
| `Supplier_ID` | String | Associated supplier | `SUP-003` |
| `Defect_Type` | String | Failure classification (`DOA`, `Functional Failure`, etc.) | `Functional Failure` |
| `Defect_Qty` | Integer | Number of defective units | `3` |
| `Detected_Date` | Date | Date defect was discovered | `2025-05-10` |
| `Resolution` | String | Disposition (`Replaced`, `Credited`, `Returned`, `Pending`)| `Replaced` |
