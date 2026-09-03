"""
Unit Tests: Tariff Scenario Simulation Engine
=============================================
Tests what-if tariff calculations, domestic exemption rules, additive vs absolute adjustments.
"""

import pytest
import pandas as pd

from scorecard.cleaning import DataCleaner
from scorecard.risk_engine import RiskScoringEngine
from scorecard.scenario_engine import TariffScenarioEngine


def test_scenario_simulations(sample_datasets):
    cleaner = DataCleaner()
    sup, clean_po, tref, tscen, qdef, _ = cleaner.clean_datasets(
        suppliers=sample_datasets["suppliers"],
        purchase_orders=sample_datasets["purchase_orders"],
        tariff_reference=sample_datasets["tariff_reference"],
        tariff_scenarios=sample_datasets["tariff_scenarios"],
        quality_defects=sample_datasets["quality_defects"]
    )

    risk_engine = RiskScoringEngine()
    scorecard = risk_engine.compute_supplier_scorecard(sup, clean_po)

    scenario_engine = TariffScenarioEngine()
    scen_results = scenario_engine.run_all_scenarios(scorecard, tscen)

    assert len(scen_results) == len(tscen) * len(scorecard)

    # 1. Domestic (US) supplier MUST always have 0% tariff across ALL scenarios
    us_results = scen_results[scen_results["Country"] == "United States"]
    for _, row in us_results.iterrows():
        assert row["Scenario_Tariff_Rate_Pct"] == 0.0
        assert row["Delta_Spend_USD"] == 0.0

    # 2. Universal 50% scenario on Offshore (China)
    china_univ = scen_results[
        (scen_results["Country"] == "China") & 
        (scen_results["Scenario_Name"] == "Universal 50%")
    ].iloc[0]
    assert china_univ["Scenario_Tariff_Rate_Pct"] == 50.0

    # 3. Test matrix generation
    matrix = scenario_engine.generate_scenario_summary_matrix(scen_results)
    assert len(matrix) == len(tscen)
    assert "Total_Procurement_Spend_USD" in matrix.columns
