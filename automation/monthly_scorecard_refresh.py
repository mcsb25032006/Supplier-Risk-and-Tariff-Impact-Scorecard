"""
Monthly Supplier Scorecard Refresh
===================================
Automated monthly refresh job that ingests new purchase orders, recomputes
all supplier risk metrics, updates history, and flags period-over-period RAG migrations.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root and src directory to python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from scorecard.config import ScorecardConfig
from scorecard.pipeline import ScorecardPipeline


def main():
    parser = argparse.ArgumentParser(description="Monthly Supplier Risk Scorecard Refresh Automation")
    parser.add_argument("--data-dir", default=str(project_root / "data"), help="Directory containing source CSVs")
    parser.add_argument("--output-dir", default=str(project_root / "output"), help="Output directory")
    parser.add_argument("--snapshot-tag", default=datetime.now().strftime("%Y-%m"), help="Snapshot period tag")
    args = parser.parse_args()

    config = ScorecardConfig(
        data_dir=Path(args.data_dir),
        output_dir=Path(args.output_dir),
        sql_dir=project_root / "sql",
        powerbi_dir=project_root / "powerbi",
        excel_dir=project_root / "excel",
    )

    pipeline = ScorecardPipeline(config)
    results = pipeline.run(snapshot_tag=args.snapshot_tag)

    print(f"\n[SUCCESS] Supplier Scorecard Refreshed for Period: {args.snapshot_tag}")
    print("-" * 75)
    summary_table = results["scorecard"][[
        "Supplier_Name", "Country", "On_Time_Rate", "Total_Landed_Spend", "Composite_Risk_Score", "RAG_Status"
    ]]
    print(summary_table.to_string(index=False))
    print("-" * 75)

    alerts = results["history_results"].get("alerts", [])
    if alerts:
        print("\n[RAG & METRIC ALERTS DETECTED]:")
        for a in alerts:
            print(f"  * {a}")
    else:
        print("\nNo performance alert triggers or RAG migrations detected.")


if __name__ == "__main__":
    main()
