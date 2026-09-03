"""
End-to-End Scorecard Pipeline Orchestrator
==========================================
Executes the full pipeline:
Ingest -> Clean -> Risk Score -> Tariff Scenarios -> Database Load -> History Diff -> Export & Reporting.
"""

import argparse
import logging
from pathlib import Path
from typing import Dict, Any

from .config import ScorecardConfig
from .ingestion import DataIngestion
from .cleaning import DataCleaner
from .risk_engine import RiskScoringEngine
from .scenario_engine import TariffScenarioEngine
from .history_tracker import HistoryTracker
from .database import DatabaseManager
from .reporting import ReportGenerator

logger = logging.getLogger("scorecard.pipeline")


class ScorecardPipeline:
    """Orchestrates the end-to-end data processing, modeling, and reporting workflow."""

    def __init__(self, config: ScorecardConfig = None):
        self.config = config or ScorecardConfig.default()
        self.ingestion = DataIngestion(self.config.data_dir)
        self.cleaner = DataCleaner()
        self.risk_engine = RiskScoringEngine(self.config)
        self.scenario_engine = TariffScenarioEngine()
        self.history_tracker = HistoryTracker(self.config.output_dir, self.config)
        self.db_manager = DatabaseManager(self.config.sql_dir / "supplier_scorecard.db")
        self.reporter = ReportGenerator(self.config)

    def run(self, snapshot_tag: str = None) -> Dict[str, Any]:
        """Runs all pipeline stages sequentially."""
        logger.info("Starting Supplier Risk & Tariff-Impact Scorecard pipeline...")

        # 1. Ingestion
        raw_data = self.ingestion.load_all()

        # 2. Cleaning & Standardization
        sup, clean_po, tref, tscen, qdef, audit_metrics = self.cleaner.clean_datasets(
            suppliers=raw_data["suppliers"],
            purchase_orders=raw_data["purchase_orders"],
            tariff_reference=raw_data["tariff_reference"],
            tariff_scenarios=raw_data["tariff_scenarios"],
            quality_defects=raw_data["quality_defects"]
        )

        # 3. Risk Scoring & KPI computation
        scorecard_df = self.risk_engine.compute_supplier_scorecard(sup, clean_po)

        # 4. Scenario Simulation
        scenario_results_df = self.scenario_engine.run_all_scenarios(scorecard_df, tscen)
        scenario_matrix_df = self.scenario_engine.generate_scenario_summary_matrix(scenario_results_df)

        # 5. Database Loading & View Creation
        self.db_manager.load_data_frames(sup, raw_data["purchase_orders"], tref, tscen, qdef)
        self.db_manager.create_views(self.config.sql_dir / "diagnostics.sql")

        # 6. History Tracking & Change Detection
        history_results = self.history_tracker.record_and_diff_snapshot(scorecard_df, snapshot_tag)

        # 7. Reporting & Power BI Export
        pbi_export_path = self.reporter.export_powerbi_dataset(clean_po, self.config.powerbi_dir)
        markdown_report = self.reporter.generate_markdown_report(
            scorecard_df=scorecard_df,
            scenario_matrix_df=scenario_matrix_df,
            audit_metrics=audit_metrics,
            history_results=history_results,
            output_path=self.config.output_dir / "executive_briefing_report.md"
        )

        # Save summary CSVs to output directory
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        scorecard_df.to_csv(self.config.output_dir / "supplier_scorecard_summary.csv", index=False)
        scenario_results_df.to_csv(self.config.output_dir / "tariff_scenario_results.csv", index=False)

        logger.info("Pipeline execution completed successfully.")

        return {
            "scorecard": scorecard_df,
            "scenarios": scenario_results_df,
            "scenario_matrix": scenario_matrix_df,
            "audit_metrics": audit_metrics,
            "history_results": history_results,
            "pbi_export_path": pbi_export_path,
        }


def main():
    parser = argparse.ArgumentParser(description="Run Supplier Risk & Tariff-Impact Scorecard Pipeline")
    parser.add_argument("--data-dir", default="data", help="Directory containing input CSV files")
    parser.add_argument("--output-dir", default="output", help="Directory to write output reports")
    parser.add_argument("--snapshot-tag", default=None, help="Tag for historical snapshot tracking")
    args = parser.parse_args()

    config = ScorecardConfig(
        data_dir=Path(args.data_dir),
        output_dir=Path(args.output_dir),
    )
    pipeline = ScorecardPipeline(config)
    results = pipeline.run(snapshot_tag=args.snapshot_tag)

    print("\n" + "=" * 80)
    print("SUPPLIER RISK & TARIFF-IMPACT SCORECARD RESULTS")
    print("=" * 80)
    sc = results["scorecard"][["Supplier_Name", "Country", "On_Time_Rate", "Avg_Lead_Time_Days", "Total_Landed_Spend", "Composite_Risk_Score", "RAG_Status"]]
    print(sc.to_string(index=False))
    print("=" * 80)


if __name__ == "__main__":
    main()
