"""
Tariff Scenario Simulation Engine
=================================
Evaluates the financial and landed-cost impact of potential trade policy and
tariff adjustments across multiple suppliers and product categories.
"""

import logging
from typing import List, Dict, Any
import pandas as pd
import numpy as np

logger = logging.getLogger("scorecard.scenario_engine")


class TariffScenarioEngine:
    """Simulates what-if tariff adjustments on procurement spend and landed cost."""

    def __init__(self):
        pass

    def run_all_scenarios(
        self,
        scorecard_df: pd.DataFrame,
        tariff_scenarios_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Executes all tariff scenarios across suppliers and calculates landed spend deltas."""
        scenario_results = []

        for _, scen in tariff_scenarios_df.iterrows():
            scen_name = scen["Scenario_Name"]
            adj_type = scen["Adjustment_Type"]
            adj_val = float(scen["Adjustment_Value"])
            desc = scen["Description"]

            for _, sup in scorecard_df.iterrows():
                sid = sup["Supplier_ID"]
                sname = sup["Supplier_Name"]
                country = sup["Country"]
                base_spend = sup["Total_Base_Spend"]
                current_tariff_exp = sup["Tariff_Exposure_Pct"]
                current_landed_spend = sup["Total_Landed_Spend"]

                # Domestic (US) remains 0% across all scenarios
                if country == "United States":
                    scenario_rate = 0.0
                else:
                    if adj_type == "Additive":
                        scenario_rate = max(0.0, current_tariff_exp + adj_val)
                    elif adj_type == "Absolute":
                        scenario_rate = adj_val
                    else:
                        scenario_rate = current_tariff_exp

                scenario_landed_spend = base_spend * (1.0 + scenario_rate)
                delta_vs_current = scenario_landed_spend - current_landed_spend
                pct_delta = (delta_vs_current / current_landed_spend) * 100.0 if current_landed_spend > 0 else 0.0

                scenario_results.append({
                    "Scenario_Name": scen_name,
                    "Scenario_Description": desc,
                    "Supplier_ID": sid,
                    "Supplier_Name": sname,
                    "Country": country,
                    "Base_Spend_USD": round(base_spend, 2),
                    "Current_Tariff_Rate_Pct": round(current_tariff_exp * 100.0, 2),
                    "Scenario_Tariff_Rate_Pct": round(scenario_rate * 100.0, 2),
                    "Current_Landed_Spend_USD": round(current_landed_spend, 2),
                    "Scenario_Landed_Spend_USD": round(scenario_landed_spend, 2),
                    "Delta_Spend_USD": round(delta_vs_current, 2),
                    "Delta_Spend_Pct": round(pct_delta, 2),
                })

        df_out = pd.DataFrame(scenario_results)
        logger.info(f"Simulated {len(tariff_scenarios_df)} scenarios across {len(scorecard_df)} suppliers.")
        return df_out

    def generate_scenario_summary_matrix(self, scenario_df: pd.DataFrame) -> pd.DataFrame:
        """Pivots scenario results into a portfolio executive comparison table."""
        pivot = scenario_df.pivot_table(
            index="Scenario_Name",
            columns="Supplier_Name",
            values="Scenario_Landed_Spend_USD",
            aggfunc="sum"
        )
        pivot["Total_Procurement_Spend_USD"] = pivot.sum(axis=1)
        return pivot.reset_index()
