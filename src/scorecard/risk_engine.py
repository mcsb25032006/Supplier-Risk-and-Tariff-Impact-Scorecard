"""
Supplier Risk Scoring Engine
============================
Computes transparent, explainable supplier risk scores and RAG categories
grounded in delivery reliability, lead-time volatility, tariff exposure, and quality.

Formulas:
- On-Time Rate: On-Time POs / Delivered POs
- Lead-Time Volatility: Population Standard Deviation (capped at 20 days = 100 pts)
- Tariff Exposure: (Landed Spend - Base Spend) / Base Spend
- Defect Rate: POs with Defect / Delivered POs

Composite Risk Score (0-100 scale, lower is better):
    Score = 0.30 * (1 - On_Time_Rate) * 100
          + 0.20 * min(Lead_Time_StDev / 20 * 100, 100)
          + 0.25 * Tariff_Exposure_Pct * 100
          + 0.25 * Defect_Rate_Pct * 100

RAG Classification:
- Green (Low Risk): Score < 15.0
- Yellow (Moderate Risk): 15.0 <= Score < 30.0
- Red (High / Critical Risk): Score >= 30.0
"""

import logging
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from .config import ScorecardConfig

logger = logging.getLogger("scorecard.risk_engine")


class RiskScoringEngine:
    """Calculates granular supplier performance metrics and composite risk scores."""

    def __init__(self, config: ScorecardConfig = None):
        self.config = config or ScorecardConfig.default()

    def compute_supplier_scorecard(
        self,
        suppliers: pd.DataFrame,
        clean_purchase_orders: pd.DataFrame
    ) -> pd.DataFrame:
        """Computes comprehensive KPI metrics and risk scores for each supplier."""
        po = clean_purchase_orders.copy()
        delivered = po[po["PO_Status"] == "Delivered"].copy()

        rows = []
        for _, sup in suppliers.iterrows():
            sid = sup["Supplier_ID"]
            sname = sup["Supplier_Name"]
            country = sup["Country"]
            region = sup["Region"]
            cat = sup["Primary_Category"]

            sup_delivered = delivered[delivered["Supplier_ID"] == sid]
            sup_all = po[po["Supplier_ID"] == sid]

            n_delivered = len(sup_delivered)
            n_in_transit = len(sup_all[sup_all["PO_Status"] == "In Transit"])

            if n_delivered > 0:
                on_time_pos = int(sup_delivered["On_Time_Flag"].sum())
                on_time_rate = float(on_time_pos / n_delivered)
                avg_lead_time = float(sup_delivered["Lead_Time_Days"].mean())
                median_lead_time = float(sup_delivered["Lead_Time_Days"].median())
                # Population standard deviation ddof=0 matching SQL & Excel SUMPRODUCT formulas
                lead_time_stdev = float(sup_delivered["Lead_Time_Days"].std(ddof=0)) if n_delivered > 1 else 0.0
                defect_pos = int((sup_delivered["Defect_Flag"] == "Y").sum())
                defect_rate = float(defect_pos / n_delivered)
                avg_customs = float(sup_delivered["Customs_Clearance_Days"].mean())
            else:
                on_time_pos = 0
                on_time_rate = 0.0
                avg_lead_time = 0.0
                median_lead_time = 0.0
                lead_time_stdev = 0.0
                defect_pos = 0
                defect_rate = 0.0
                avg_customs = 0.0

            base_spend = float(sup_delivered["Base_Spend_USD"].sum(skipna=True))
            landed_spend = float(sup_delivered["Landed_Spend_USD"].sum(skipna=True))
            tariff_dollars = landed_spend - base_spend
            tariff_exposure = float(tariff_dollars / base_spend) if base_spend > 0 else 0.0

            # Component scoring
            c_ontime = (1.0 - on_time_rate) * 100.0
            c_leadtime = min((lead_time_stdev / self.config.lead_time_stdev_cap_days) * 100.0, 100.0)
            c_tariff = tariff_exposure * 100.0
            c_defect = defect_rate * 100.0

            weights = self.config.weights
            raw_score = (
                weights.on_time * c_ontime
                + weights.lead_time_volatility * c_leadtime
                + weights.tariff_exposure * c_tariff
                + weights.defect_rate * c_defect
            )
            composite_score = round(raw_score, 1)

            # RAG Status determination
            if composite_score >= self.config.rag.red_threshold:
                rag = "Red"
            elif composite_score >= self.config.rag.yellow_threshold:
                rag = "Yellow"
            else:
                rag = "Green"

            rows.append({
                "Supplier_ID": sid,
                "Supplier_Name": sname,
                "Country": country,
                "Region": region,
                "Primary_Category": cat,
                "Delivered_POs": n_delivered,
                "In_Transit_POs": n_in_transit,
                "On_Time_POs": on_time_pos,
                "On_Time_Rate": round(on_time_rate, 4),
                "Avg_Lead_Time_Days": round(avg_lead_time, 1),
                "Median_Lead_Time_Days": round(median_lead_time, 1),
                "Lead_Time_StDev_Days": round(lead_time_stdev, 1),
                "Total_Base_Spend": round(base_spend, 2),
                "Total_Landed_Spend": round(landed_spend, 2),
                "Tariff_Dollars": round(tariff_dollars, 2),
                "Tariff_Exposure_Pct": round(tariff_exposure, 4),
                "Defect_POs": defect_pos,
                "Defect_Rate_Pct": round(defect_rate, 4),
                "Avg_Customs_Days": round(avg_customs, 1),
                "Composite_Risk_Score": composite_score,
                "RAG_Status": rag,
            })

        scorecard_df = pd.DataFrame(rows).sort_values("Composite_Risk_Score").reset_index(drop=True)
        logger.info(f"Scorecard calculated for {len(scorecard_df)} suppliers.")
        return scorecard_df
