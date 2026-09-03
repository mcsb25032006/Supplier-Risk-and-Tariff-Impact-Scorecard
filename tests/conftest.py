"""
Pytest Configuration & Shared Fixtures
=======================================
Provides reusable fixtures for mock procurement data, configuration,
and database connections.
"""

import pytest
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from scorecard.config import ScorecardConfig, RiskWeights, RAGThresholds, AlertThresholds
from scorecard.ingestion import DataIngestion
from scorecard.cleaning import DataCleaner
from scorecard.risk_engine import RiskScoringEngine
from scorecard.scenario_engine import TariffScenarioEngine
from scorecard.history_tracker import HistoryTracker
from scorecard.database import DatabaseManager


@pytest.fixture
def project_root():
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def sample_config(tmp_path):
    return ScorecardConfig(
        data_dir=tmp_path / "data",
        output_dir=tmp_path / "output",
        sql_dir=tmp_path / "sql",
        powerbi_dir=tmp_path / "powerbi",
        excel_dir=tmp_path / "excel",
    )


@pytest.fixture
def sample_datasets():
    """Generates a controlled in-memory dataset for unit testing."""
    suppliers = pd.DataFrame([
        {
            "Supplier_ID": "SUP-001",
            "Supplier_Name": "Domestic Alpha",
            "Country": "United States",
            "Region": "Domestic",
            "City": "Dallas, TX",
            "Primary_Category": "GPU Servers",
            "Onboarded_Date": "2023-01-01",
            "USMCA_Qualifying": "N/A",
        },
        {
            "Supplier_ID": "SUP-002",
            "Supplier_Name": "Nearshore Beta",
            "Country": "Mexico",
            "Region": "Nearshore",
            "City": "Monterrey, MX",
            "Primary_Category": "Network Switches",
            "Onboarded_Date": "2023-05-01",
            "USMCA_Qualifying": "Y",
        },
        {
            "Supplier_ID": "SUP-003",
            "Supplier_Name": "Offshore Gamma",
            "Country": "China",
            "Region": "Offshore",
            "City": "Shenzhen, CN",
            "Primary_Category": "PDU / MEP Equipment",
            "Onboarded_Date": "2022-06-01",
            "USMCA_Qualifying": "N/A",
        },
    ])

    tariff_ref = pd.DataFrame([
        {"Country": "United States", "HS_Code": "8471.50", "Base_Effective_Rate": 0.00},
        {"Country": "Mexico", "HS_Code": "8517.62", "Base_Effective_Rate": 0.00},
        {"Country": "China", "HS_Code": "8537.10", "Base_Effective_Rate": 0.35},
    ])

    tariff_scenarios = pd.DataFrame([
        {"Scenario_Name": "Current (Jul 2026)", "Adjustment_Type": "Additive", "Adjustment_Value": 0.0, "Description": "Baseline"},
        {"Scenario_Name": "+10% escalation", "Adjustment_Type": "Additive", "Adjustment_Value": 0.10, "Description": "+10% Tariff"},
        {"Scenario_Name": "Universal 50%", "Adjustment_Type": "Absolute", "Adjustment_Value": 0.50, "Description": "50% Absolute"},
    ])

    # Construct deterministic PO records
    po_records = [
        # SUP-001: 2 delivered, 100% on-time, lead times 10 & 12 (stdev=1), 0 defects, 0 tariff
        {"PO_ID": "PO-100", "Supplier_ID": "SUP-001", "Product_Category": "GPU Servers", "HS_Code": "8471.50",
         "PO_Date": "2025-01-01", "Quantity": 10, "Unit_Cost_USD": 1000.0, "Incoterm": "FOB", "Freight_Mode": "Truck",
         "Promised_Delivery_Date": "2025-01-15", "Actual_Delivery_Date": "2025-01-11", "Customs_Clearance_Days": 0, "Defect_Flag": "N", "PO_Status": "Delivered"},
        {"PO_ID": "PO-101", "Supplier_ID": "SUP-001", "Product_Category": "GPU Servers", "HS_Code": "8471.50",
         "PO_Date": "2025-01-01", "Quantity": 10, "Unit_Cost_USD": 1000.0, "Incoterm": "FOB", "Freight_Mode": "Truck",
         "Promised_Delivery_Date": "2025-01-15", "Actual_Delivery_Date": "2025-01-13", "Customs_Clearance_Days": 0, "Defect_Flag": "N", "PO_Status": "Delivered"},

        # SUP-002: 2 delivered, 50% on-time, lead times 15 & 25 (stdev=5), 0 defects, 0 tariff
        {"PO_ID": "PO-200", "Supplier_ID": "SUP-002", "Product_Category": "Network Switches", "HS_Code": "8517.62",
         "PO_Date": "2025-01-01", "Quantity": 5, "Unit_Cost_USD": 500.0, "Incoterm": "FOB", "Freight_Mode": "Truck",
         "Promised_Delivery_Date": "2025-01-15", "Actual_Delivery_Date": "2025-01-16", "Customs_Clearance_Days": 2, "Defect_Flag": "N", "PO_Status": "Delivered"},
        {"PO_ID": "PO-201", "Supplier_ID": "SUP-002", "Product_Category": "Network Switches", "HS_Code": "8517.62",
         "PO_Date": "2025-01-01", "Quantity": 5, "Unit_Cost_USD": 500.0, "Incoterm": "FOB", "Freight_Mode": "Truck",
         "Promised_Delivery_Date": "2025-01-30", "Actual_Delivery_Date": "2025-01-26", "Customs_Clearance_Days": 2, "Defect_Flag": "N", "PO_Status": "Delivered"},

        # SUP-003: 2 delivered, 0% on-time, lead times 30 & 50 (stdev=10), 1 defect (50%), 35% tariff
        {"PO_ID": "PO-300", "Supplier_ID": "SUP-003", "Product_Category": "PDU / MEP Equipment", "HS_Code": "8537.10",
         "PO_Date": "2025-01-01", "Quantity": 20, "Unit_Cost_USD": 200.0, "Incoterm": "CIF", "Freight_Mode": "Ocean",
         "Promised_Delivery_Date": "2025-01-25", "Actual_Delivery_Date": "2025-01-31", "Customs_Clearance_Days": 5, "Defect_Flag": "Y", "PO_Status": "Delivered"},
        {"PO_ID": "PO-301", "Supplier_ID": "SUP-003", "Product_Category": "PDU / MEP Equipment", "HS_Code": "8537.10",
         "PO_Date": "2025-01-01", "Quantity": 20, "Unit_Cost_USD": 200.0, "Incoterm": "CIF", "Freight_Mode": "Ocean",
         "Promised_Delivery_Date": "2025-02-10", "Actual_Delivery_Date": "2025-02-20", "Customs_Clearance_Days": 7, "Defect_Flag": "N", "PO_Status": "Delivered"},

        # In-transit & Duplicate rows to test cleaning
        {"PO_ID": "PO-400", "Supplier_ID": "SUP-001", "Product_Category": "GPU Servers", "HS_Code": "8471.50",
         "PO_Date": "2025-06-01", "Quantity": 5, "Unit_Cost_USD": 1000.0, "Incoterm": "FOB", "Freight_Mode": "Truck",
         "Promised_Delivery_Date": "2025-06-20", "Actual_Delivery_Date": "", "Customs_Clearance_Days": 0, "Defect_Flag": "N", "PO_Status": "In Transit"},
        {"PO_ID": "PO-100", "Supplier_ID": "SUP-001", "Product_Category": "GPU Servers", "HS_Code": "8471.50",
         "PO_Date": "2025-01-01", "Quantity": 10, "Unit_Cost_USD": 1000.0, "Incoterm": "FOB", "Freight_Mode": "Truck",
         "Promised_Delivery_Date": "2025-01-15", "Actual_Delivery_Date": "2025-01-11", "Customs_Clearance_Days": 0, "Defect_Flag": "N", "PO_Status": "Delivered"},
    ]
    purchase_orders = pd.DataFrame(po_records)

    quality_defects = pd.DataFrame([
        {"Defect_ID": "DEF-0001", "PO_ID": "PO-300", "Supplier_ID": "SUP-003", "Defect_Type": "Functional Failure", "Defect_Qty": 2, "Detected_Date": "2025-02-02", "Resolution": "Replaced"}
    ])

    return {
        "suppliers": suppliers,
        "tariff_reference": tariff_ref,
        "tariff_scenarios": tariff_scenarios,
        "purchase_orders": purchase_orders,
        "quality_defects": quality_defects,
    }
