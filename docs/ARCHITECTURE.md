# Architecture Documentation

## End-to-End System Architecture

The **Supplier Risk & Tariff-Impact Scorecard** is architected as a multi-tier data engineering and business intelligence platform designed to ingest raw procurement data, perform rigorous cleaning and deduplication, derive supply-chain risk metrics, simulate tariff scenarios, and distribute analytical models to SQL databases, Excel workbooks, and Power BI dashboards.

```
+-------------------------------------------------------------------------------+
|                             RAW DATA SOURCES                                  |
|   Coupa Supplier Portal CSVs (Suppliers, Purchase Orders, Defects, Tariffs)   |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                       DATA INGESTION & VALIDATION                             |
|    - Schema validation via Pydantic (`scorecard.models`)                      |
|    - Missing column detection & type coercion                                 |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                      DATA CLEANING & DEDUPLICATION                            |
|    - Duplicate PO detection (first-occurrence indexing)                       |
|    - Date parsing & lead-time calculation                                     |
|    - Text casing standardization (Incoterms, Freight Modes)                   |
|    - Financial enrichment (Base Spend, Landed Cost, Tariff Dollars)           |
+-------------------------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
+------------------------------------+  +---------------------------------------+
|        SQL DIAGNOSTIC LAYER        |  |          CORE ANALYTIC ENGINES        |
|  - SQLite relational database      |  |  - RiskScoringEngine (KPIs & Score)   |
|  - `clean_purchase_orders` view    |  |  - TariffScenarioEngine (What-If Sim) |
|  - Parity-verified SQL analytics   |  |  - HistoryTracker (MoM Diff & Alerts) |
+------------------------------------+  +---------------------------------------+
                                                         |
         +-----------------------------------------------+
         |
         v
+-------------------------------------------------------------------------------+
|                             DELIVERABLE OUTPUTS                               |
|  1. Power BI Export (`powerbi_ready_export.csv`) + DAX Measures               |
|  2. Live Excel Scorecard (`Supplier_Risk_Tariff_Scorecard.xlsx`)              |
|  3. Executive Markdown & JSON Briefing Reports                                |
|  4. Historical Snapshot Store (`scorecard_history.json`)                      |
+-------------------------------------------------------------------------------+
```

---

## Component Breakdown

### 1. Ingestion & Validation Layer (`src/scorecard/ingestion.py`, `models.py`)
- Ingests raw procurement CSVs (`suppliers.csv`, `purchase_orders.csv`, `tariff_reference.csv`, `tariff_scenarios.csv`, `quality_defects.csv`).
- Validates data formats and mandatory column constraints.
- Rejects corrupt or incomplete schemas early in the pipeline.

### 2. Cleaning & Transformation Layer (`src/scorecard/cleaning.py`)
- Employs an expanding-window deduplication rule (`Is_First_Occurrence`) to eliminate duplicate submissions without breaking audit trails.
- Standardizes date timestamps and computes `Lead_Time_Days = Actual_Delivery_Date - PO_Date`.
- Flags on-time delivery for completed orders: `Actual_Delivery_Date <= Promised_Delivery_Date`.
- Merges tariff reference schedules by `(Country, HS_Code)` to calculate baseline landed costs.

### 3. Relational SQL Diagnostic Layer (`sql/`)
- Relational schema defined in `sql/schema.sql`.
- Data quality audits in `sql/diagnostics.sql` isolating duplicate keys, missing invoice costs, and inconsistent categorical strings.
- Analytical queries in `sql/analytics_kpis.sql` providing SQL implementations of delivery reliability, lead time variability, landed costs, and composite risk scoring.

### 4. Risk Scoring & Scenario Engine (`src/scorecard/risk_engine.py`, `scenario_engine.py`)
- Implements transparent, explainable composite risk scoring across 4 weighted pillars: On-Time Delivery (30%), Lead-Time Volatility (20%), Tariff Exposure (25%), and Quality/Defects (25%).
- Categorizes suppliers into RAG tiers (Green < 15, Yellow 15–29.9, Red $\ge 30$).
- Models multi-scenario trade policy shifts (+10%, +25%, Section 122 Sunset, Universal 50%).

### 5. Historical Tracking & Change Detection (`src/scorecard/history_tracker.py`)
- Persists point-in-time scoring runs to a JSON history log.
- Performs period-over-period diffing and raises automated alerts upon RAG tier migration or critical metric deterioration.

### 6. Business Intelligence & Reporting Layer (`src/scorecard/reporting.py`, `powerbi/`, `excel/`)
- Exports flattened, deduplicated datasets for Power BI dashboard consumption.
- Openpyxl-automated generation of interactive Excel workbooks with live dynamic formula modeling and scenario dropdowns.
