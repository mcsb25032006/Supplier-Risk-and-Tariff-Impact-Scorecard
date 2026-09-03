"""
Build SQLite Database Script
============================
Initializes the SQLite relational database at sql/supplier_scorecard.db
from schema.sql, loads data CSVs, and creates diagnostic views.
"""

from pathlib import Path
import sys

# Add project root and src directory
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from scorecard.ingestion import DataIngestion
from scorecard.database import DatabaseManager


def build_database():
    data_dir = project_root / "data"
    sql_dir = project_root / "sql"
    db_path = sql_dir / "supplier_scorecard.db"

    print(f"Building SQLite database at: {db_path}")
    ingestion = DataIngestion(data_dir)
    datasets = ingestion.load_all()

    db_manager = DatabaseManager(db_path)
    db_manager.initialize_database(sql_dir / "schema.sql")
    db_manager.load_data_frames(
        suppliers=datasets["suppliers"],
        purchase_orders=datasets["purchase_orders"],
        tariff_reference=datasets["tariff_reference"],
        tariff_scenarios=datasets["tariff_scenarios"],
        quality_defects=datasets["quality_defects"],
    )
    db_manager.create_views(sql_dir / "diagnostics.sql")
    print("Database build complete and verified.")


if __name__ == "__main__":
    build_database()
