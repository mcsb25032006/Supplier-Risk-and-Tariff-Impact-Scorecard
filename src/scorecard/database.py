"""
SQLite Database Management Module
=================================
Initializes the SQLite relational database, loads raw and clean tables,
builds deduplicated views, and executes diagnostic and analytical queries.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

logger = logging.getLogger("scorecard.database")


class DatabaseManager:
    """Manages SQLite database initialization, data loading, views, and queries."""

    def __init__(self, db_path: Path | str = "sql/supplier_scorecard.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Returns a connection to the SQLite database with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_database(
        self,
        schema_file: Path | str = "sql/schema.sql"
    ) -> None:
        """Executes DDL statements from the schema file."""
        schema_p = Path(schema_file)
        if not schema_p.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_p}")

        with open(schema_p, "r", encoding="utf-8") as f:
            sql_script = f.read()

        with self.get_connection() as conn:
            conn.executescript(sql_script)
            conn.commit()

        logger.info(f"Database schema initialized at {self.db_path}")

    def load_data_frames(
        self,
        suppliers: pd.DataFrame,
        purchase_orders: pd.DataFrame,
        tariff_reference: pd.DataFrame,
        tariff_scenarios: pd.DataFrame,
        quality_defects: pd.DataFrame
    ) -> None:
        """Loads Pandas dataframes into SQLite tables."""
        with self.get_connection() as conn:
            suppliers.to_sql("suppliers", conn, if_exists="replace", index=False)
            purchase_orders.to_sql("purchase_orders", conn, if_exists="replace", index=False)
            tariff_reference.to_sql("tariff_reference", conn, if_exists="replace", index=False)
            tariff_scenarios.to_sql("tariff_scenarios", conn, if_exists="replace", index=False)
            quality_defects.to_sql("quality_defects", conn, if_exists="replace", index=False)
            conn.commit()

        logger.info("All raw data tables successfully written to SQLite database.")

    def create_views(self, diagnostics_file: Path | str = "sql/diagnostics.sql") -> None:
        """Executes diagnostic and view creation statements from diagnostics.sql."""
        diag_p = Path(diagnostics_file)
        if diag_p.exists():
            with open(diag_p, "r", encoding="utf-8") as f:
                sql_script = f.read()
            with self.get_connection() as conn:
                conn.executescript(sql_script)
                conn.commit()
            logger.info("Diagnostic views successfully created in SQLite database.")

    def run_query(self, query: str) -> pd.DataFrame:
        """Executes a SQL query and returns results as a Pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)
