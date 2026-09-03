# Execution & Reproduction Guide

Step-by-step instructions to set up, build, execute, test, and verify the **Supplier Risk & Tariff-Impact Scorecard** repository from a clean environment.

---

## 1. Prerequisites
- **Python**: Version 3.10, 3.11, 3.12, or 3.13
- **Git** (optional for source tracking)
- **Power BI Desktop** (for `.pbix` dashboard exploration)
- **Microsoft Excel** or compatible spreadsheet software (for `.xlsx` inspection)

---

## 2. Environment Setup

### Create Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 3. Dataset Generation & Database Build

```bash
# 1. Generate clean raw simulated datasets into data/
python scripts/generate_dataset.py

# 2. Build and initialize SQLite relational database
python scripts/build_database.py

# 3. Generate interactive Excel workbook with live formulas
python scripts/build_excel.py

# 4. Generate SVG process flow and scorecard preview diagrams
python scripts/build_diagram.py
python scripts/build_hero_preview.py
```

---

## 4. Run the Core Python Data Pipeline

```bash
# Run end-to-end pipeline (Data -> Cleaning -> Risk Scoring -> Scenarios -> Reporting)
python -m scorecard.pipeline --data-dir data --output-dir output
```

### Automated Monthly Refresh Job
```bash
# Execute automated monthly refresh simulation
python automation/monthly_scorecard_refresh.py --data-dir data --output-dir output --snapshot-tag 2026-07
```

---

## 5. Automated Test Suite Execution

Run the complete `pytest` validation suite:
```bash
pytest -v
```

Expected output:
```
tests/test_data_validation.py::test_ingestion_valid_directory PASSED
tests/test_data_validation.py::test_ingestion_missing_directory PASSED
tests/test_data_validation.py::test_schema_missing_column PASSED
tests/test_data_validation.py::test_cleaning_deduplication PASSED
tests/test_risk_engine.py::test_risk_scoring_sample PASSED
tests/test_risk_engine.py::test_edge_case_zero_delivered_pos PASSED
tests/test_risk_engine.py::test_weights_sum_validation PASSED
tests/test_scenario_engine.py::test_scenario_simulations PASSED
tests/test_history_tracker.py::test_history_tracker_snapshot_and_alerts PASSED
tests/test_sql_reconciliation.py::test_sql_kpi_parity PASSED
tests/test_pipeline_integration.py::test_full_pipeline_execution PASSED
```

---

## 6. Power BI Dashboard Setup

1. Launch **Microsoft Power BI Desktop**.
2. Click **Get Data** $\rightarrow$ **Text/CSV** $\rightarrow$ Select `powerbi/powerbi_ready_export.csv`.
3. Click **Transform Data**, verify data types as documented in `powerbi/DAX_walkthrough.md`, and click **Close & Apply**.
4. Import `data/tariff_scenarios.csv` as a disconnected parameter table.
5. Create a new measure group and paste the DAX definitions from `powerbi/DAX_measures.dax`.
6. Construct the 4 dashboard tabs using the layout instructions in `powerbi/DAX_walkthrough.md`.
