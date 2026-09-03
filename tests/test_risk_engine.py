"""
Unit Tests: Supplier Risk Scoring Engine
========================================
Tests KPI calculations, lead time variance, landed costs, risk weights,
RAG thresholds, and edge cases.
"""

import pytest
import pandas as pd
import numpy as np

from scorecard.config import ScorecardConfig, RiskWeights
from scorecard.cleaning import DataCleaner
from scorecard.risk_engine import RiskScoringEngine


def test_risk_scoring_sample(sample_datasets):
    cleaner = DataCleaner()
    sup, clean_po, tref, tscen, qdef, _ = cleaner.clean_datasets(
        suppliers=sample_datasets["suppliers"],
        purchase_orders=sample_datasets["purchase_orders"],
        tariff_reference=sample_datasets["tariff_reference"],
        tariff_scenarios=sample_datasets["tariff_scenarios"],
        quality_defects=sample_datasets["quality_defects"]
    )

    engine = RiskScoringEngine()
    scorecard = engine.compute_supplier_scorecard(sup, clean_po)

    assert len(scorecard) == 3

    # Check SUP-001 (Domestic Alpha): 100% on-time, 0% tariff, 0% defect
    sup1 = scorecard[scorecard["Supplier_ID"] == "SUP-001"].iloc[0]
    assert sup1["Delivered_POs"] == 2
    assert sup1["On_Time_Rate"] == 1.0
    assert sup1["Defect_Rate_Pct"] == 0.0
    assert sup1["Tariff_Exposure_Pct"] == 0.0
    assert sup1["RAG_Status"] == "Green"

    # Check SUP-003 (Offshore Gamma): 0% on-time, 35% tariff, 50% defect -> High risk
    sup3 = scorecard[scorecard["Supplier_ID"] == "SUP-003"].iloc[0]
    assert sup3["On_Time_Rate"] == 0.0
    assert sup3["Tariff_Exposure_Pct"] == 0.35
    assert sup3["Defect_Rate_Pct"] == 0.50
    assert sup3["Composite_Risk_Score"] >= 30.0
    assert sup3["RAG_Status"] == "Red"


def test_edge_case_zero_delivered_pos():
    """Validates behavior when a supplier has 0 delivered POs (e.g. all in-transit or new supplier)."""
    suppliers = pd.DataFrame([
        {
            "Supplier_ID": "SUP-999",
            "Supplier_Name": "New Supplier",
            "Country": "United States",
            "Region": "Domestic",
            "City": "Austin, TX",
            "Primary_Category": "GPU Servers",
            "Onboarded_Date": "2026-01-01",
            "USMCA_Qualifying": "N/A",
        }
    ])

    empty_po = pd.DataFrame(columns=[
        "PO_ID", "Supplier_ID", "Product_Category", "HS_Code", "PO_Date", "Quantity",
        "Unit_Cost_USD", "Incoterm", "Freight_Mode", "Promised_Delivery_Date", "Actual_Delivery_Date",
        "Customs_Clearance_Days", "Defect_Flag", "PO_Status", "Lead_Time_Days", "On_Time_Flag",
        "Country", "Region", "Base_Effective_Rate", "Base_Spend_USD", "Landed_Cost_Per_Unit",
        "Landed_Spend_USD", "Tariff_Dollars"
    ])

    engine = RiskScoringEngine()
    scorecard = engine.compute_supplier_scorecard(suppliers, empty_po)

    assert len(scorecard) == 1
    row = scorecard.iloc[0]
    assert row["Delivered_POs"] == 0
    assert row["Total_Landed_Spend"] == 0.0
    assert row["Composite_Risk_Score"] >= 0.0


def test_weights_sum_validation():
    """Ensures RiskWeights enforces exact sum of 1.0."""
    with pytest.raises(ValueError, match="must sum to 1.0"):
        RiskWeights(on_time=0.50, lead_time_volatility=0.50, tariff_exposure=0.50, defect_rate=0.50)
