"""
Unit Tests: Historical Risk & Performance Change Tracking
==========================================================
Tests snapshot history persistence, period-over-period diffing, and alert generation.
"""

import pytest
import pandas as pd
from pathlib import Path

from scorecard.config import ScorecardConfig
from scorecard.history_tracker import HistoryTracker


def test_history_tracker_snapshot_and_alerts(tmp_path):
    config = ScorecardConfig(output_dir=tmp_path)
    tracker = HistoryTracker(tmp_path, config)

    # Initial period (Period 1)
    period1_df = pd.DataFrame([
        {"Supplier_ID": "SUP-001", "Supplier_Name": "Supplier A", "Composite_Risk_Score": 12.0, "RAG_Status": "Green", "On_Time_Rate": 0.90, "Defect_Rate_Pct": 0.02, "Tariff_Exposure_Pct": 0.0},
        {"Supplier_ID": "SUP-002", "Supplier_Name": "Supplier B", "Composite_Risk_Score": 25.0, "RAG_Status": "Yellow", "On_Time_Rate": 0.80, "Defect_Rate_Pct": 0.05, "Tariff_Exposure_Pct": 0.20},
    ])

    res1 = tracker.record_and_diff_snapshot(period1_df, snapshot_tag="2026-06")
    assert res1["total_snapshots"] == 1
    assert len(res1["alerts"]) == 0  # No alerts on first run

    # Subsequent period with deterioration on Supplier B (Period 2)
    period2_df = pd.DataFrame([
        {"Supplier_ID": "SUP-001", "Supplier_Name": "Supplier A", "Composite_Risk_Score": 12.5, "RAG_Status": "Green", "On_Time_Rate": 0.89, "Defect_Rate_Pct": 0.02, "Tariff_Exposure_Pct": 0.0},
        # Supplier B worsens: risk score jumps from 25 to 35 (RAG Yellow -> Red, On-time drops from 80% to 65%)
        {"Supplier_ID": "SUP-002", "Supplier_Name": "Supplier B", "Composite_Risk_Score": 35.0, "RAG_Status": "Red", "On_Time_Rate": 0.65, "Defect_Rate_Pct": 0.08, "Tariff_Exposure_Pct": 0.20},
    ])

    res2 = tracker.record_and_diff_snapshot(period2_df, snapshot_tag="2026-07")
    assert res2["total_snapshots"] == 2
    assert len(res2["alerts"]) >= 3  # RAG migration, Risk Surge, Delivery Deterioration
    assert any("RAG STATUS MIGRATION" in a for a in res2["alerts"])
    assert any("RISK SCORE SURGE" in a for a in res2["alerts"])
    assert any("DELIVERY DETERIORATION" in a for a in res2["alerts"])
