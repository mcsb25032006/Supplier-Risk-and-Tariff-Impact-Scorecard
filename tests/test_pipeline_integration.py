"""
Integration Tests: End-to-End Scorecard Pipeline
=================================================
Validates full pipeline execution from raw ingestion to report outputs.
"""

import pytest
from pathlib import Path

from scorecard.config import ScorecardConfig
from scorecard.pipeline import ScorecardPipeline


def test_full_pipeline_execution(tmp_path, project_root):
    data_dir = project_root / "data"
    output_dir = tmp_path / "output"
    sql_dir = tmp_path / "sql"
    powerbi_dir = tmp_path / "powerbi"

    # Copy schema and diagnostics SQL files
    sql_dir.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy(project_root / "sql" / "schema.sql", sql_dir / "schema.sql")
    shutil.copy(project_root / "sql" / "diagnostics.sql", sql_dir / "diagnostics.sql")

    config = ScorecardConfig(
        data_dir=data_dir,
        output_dir=output_dir,
        sql_dir=sql_dir,
        powerbi_dir=powerbi_dir,
    )

    pipeline = ScorecardPipeline(config)
    results = pipeline.run(snapshot_tag="test-run")

    assert "scorecard" in results
    assert "scenarios" in results
    assert "audit_metrics" in results
    assert len(results["scorecard"]) == 3

    # Check generated files
    assert (output_dir / "supplier_scorecard_summary.csv").exists()
    assert (output_dir / "tariff_scenario_results.csv").exists()
    assert (output_dir / "executive_briefing_report.md").exists()
    assert (output_dir / "scorecard_history.json").exists()
    assert (powerbi_dir / "powerbi_ready_export.csv").exists()
    assert (sql_dir / "supplier_scorecard.db").exists()
