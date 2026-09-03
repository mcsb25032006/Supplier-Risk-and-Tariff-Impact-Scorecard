"""
Historical Risk & Performance Change Tracking Module
=====================================================
Maintains snapshots of supplier performance over time and detects significant
shifts in risk scores, on-time delivery, defect rates, and tariff exposures.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from .config import ScorecardConfig

logger = logging.getLogger("scorecard.history_tracker")


class HistoryTracker:
    """Manages snapshot history storage, period-over-period diffing, and automated alerts."""

    def __init__(self, output_dir: Path | str = "output", config: ScorecardConfig = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.output_dir / "scorecard_history.json"
        self.config = config or ScorecardConfig.default()

    def load_history(self) -> List[Dict[str, Any]]:
        """Loads historical snapshot runs from disk."""
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load history from {self.history_file}: {e}")
            return []

    def record_and_diff_snapshot(
        self,
        current_scorecard: pd.DataFrame,
        snapshot_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """Records the current scorecard and compares against the previous snapshot to detect changes."""
        tag = snapshot_tag or datetime.now().strftime("%Y-%m-%d")
        history = self.load_history()

        alerts: List[str] = []
        detailed_diffs: List[Dict[str, Any]] = []

        if history:
            prior_run = history[-1]
            prior_records = {r["Supplier_ID"]: r for r in prior_run.get("scorecard", [])}

            for _, curr in current_scorecard.iterrows():
                sid = curr["Supplier_ID"]
                sname = curr["Supplier_Name"]
                prior = prior_records.get(sid)

                if prior:
                    curr_score = float(curr["Composite_Risk_Score"])
                    prior_score = float(prior.get("Composite_Risk_Score", 0.0))
                    score_delta = round(curr_score - prior_score, 1)

                    curr_rag = curr["RAG_Status"]
                    prior_rag = prior.get("RAG_Status")

                    curr_ontime = float(curr["On_Time_Rate"])
                    prior_ontime = float(prior.get("On_Time_Rate", 0.0))
                    ontime_delta = round(curr_ontime - prior_ontime, 4)

                    curr_defect = float(curr["Defect_Rate_Pct"])
                    prior_defect = float(prior.get("Defect_Rate_Pct", 0.0))
                    defect_delta = round(curr_defect - prior_defect, 4)

                    diff_entry = {
                        "Supplier_ID": sid,
                        "Supplier_Name": sname,
                        "Prior_Risk_Score": prior_score,
                        "Current_Risk_Score": curr_score,
                        "Risk_Score_Delta": score_delta,
                        "Prior_RAG": prior_rag,
                        "Current_RAG": curr_rag,
                        "RAG_Changed": curr_rag != prior_rag,
                        "On_Time_Rate_Delta": ontime_delta,
                        "Defect_Rate_Delta": defect_delta,
                    }
                    detailed_diffs.append(diff_entry)

                    # Check RAG tier change
                    if curr_rag != prior_rag:
                        alerts.append(
                            f"RAG STATUS MIGRATION: {sname} ({sid}) moved from {prior_rag} -> {curr_rag} "
                            f"(Risk Score: {prior_score} -> {curr_score})"
                        )

                    # Check risk score increase alert
                    if score_delta >= self.config.alerts.risk_score_delta_alert:
                        alerts.append(
                            f"RISK SCORE SURGE: {sname} risk score increased by +{score_delta} pts "
                            f"(from {prior_score} to {curr_score})"
                        )

                    # Check on-time drop
                    if ontime_delta <= -self.config.alerts.on_time_drop_alert_pct:
                        alerts.append(
                            f"DELIVERY DETERIORATION: {sname} on-time rate dropped by {abs(ontime_delta)*100:.1f}% "
                            f"(from {prior_ontime*100:.1f}% to {curr_ontime*100:.1f}%)"
                        )

                    # Check defect rate spike
                    if defect_delta >= self.config.alerts.defect_rate_spike_pct:
                        alerts.append(
                            f"QUALITY WARNING: {sname} defect rate increased by +{defect_delta*100:.1f}% "
                            f"(from {prior_defect*100:.1f}% to {curr_defect*100:.1f}%)"
                        )

        # Append new snapshot to history
        new_entry = {
            "snapshot_tag": tag,
            "recorded_at": datetime.now().isoformat(),
            "scorecard": current_scorecard.to_dict("records"),
        }
        history.append(new_entry)

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        logger.info(f"Snapshot '{tag}' recorded. {len(alerts)} alerts identified.")

        return {
            "snapshot_tag": tag,
            "total_snapshots": len(history),
            "alerts": alerts,
            "diffs": detailed_diffs,
        }
