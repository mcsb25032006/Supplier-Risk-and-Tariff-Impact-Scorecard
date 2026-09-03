"""
Integration Tests: SQL Query Reconciliation & Parity
=====================================================
Executes SQL queries against SQLite database and asserts 100% mathematical
consistency with Python risk engine calculations.
"""

import pytest
import sqlite3
import pandas as pd
from pathlib import Path

from scorecard.ingestion import DataIngestion
from scorecard.cleaning import DataCleaner
from scorecard.risk_engine import RiskScoringEngine
from scorecard.database import DatabaseManager


def test_sql_kpi_parity(project_root):
    data_dir = project_root / "data"
    sql_dir = project_root / "sql"
    db_path = sql_dir / "supplier_scorecard.db"

    # 1. Ingest and compute with Python
    ingestion = DataIngestion(data_dir)
    datasets = ingestion.load_all()

    cleaner = DataCleaner()
    sup, clean_po, tref, tscen, qdef, _ = cleaner.clean_datasets(
        suppliers=datasets["suppliers"],
        purchase_orders=datasets["purchase_orders"],
        tariff_reference=datasets["tariff_reference"],
        tariff_scenarios=datasets["tariff_scenarios"],
        quality_defects=datasets["quality_defects"]
    )

    risk_engine = RiskScoringEngine()
    py_scorecard = risk_engine.compute_supplier_scorecard(sup, clean_po)

    # 2. Query SQLite database
    db_manager = DatabaseManager(db_path)
    # Ensure fresh DB state
    db_manager.initialize_database(sql_dir / "schema.sql")
    db_manager.load_data_frames(sup, datasets["purchase_orders"], tref, tscen, qdef)
    db_manager.create_views(sql_dir / "diagnostics.sql")

    # SQL query for On-Time Delivery
    sql_ontime = """
    SELECT
        s.Supplier_ID,
        COUNT(*) AS delivered_pos,
        SUM(CASE WHEN julianday(p.Actual_Delivery_Date) <= julianday(p.Promised_Delivery_Date) THEN 1 ELSE 0 END) AS on_time_pos,
        ROUND(1.0 * SUM(CASE WHEN julianday(p.Actual_Delivery_Date) <= julianday(p.Promised_Delivery_Date) THEN 1 ELSE 0 END) / COUNT(*), 4) AS on_time_rate
    FROM clean_purchase_orders p
    JOIN suppliers s ON p.Supplier_ID = s.Supplier_ID
    WHERE p.PO_Status = 'Delivered'
    GROUP BY s.Supplier_ID
    ORDER BY s.Supplier_ID;
    """
    df_sql_ontime = db_manager.run_query(sql_ontime)

    py_sorted = py_scorecard.sort_values("Supplier_ID").reset_index(drop=True)
    sql_sorted = df_sql_ontime.sort_values("Supplier_ID").reset_index(drop=True)

    for i in range(len(py_sorted)):
        py_row = py_sorted.iloc[i]
        sql_row = sql_sorted.iloc[i]

        assert py_row["Supplier_ID"] == sql_row["Supplier_ID"]
        assert py_row["Delivered_POs"] == sql_row["delivered_pos"]
        assert py_row["On_Time_POs"] == sql_row["on_time_pos"]
        assert abs(py_row["On_Time_Rate"] - sql_row["on_time_rate"]) < 1e-3
