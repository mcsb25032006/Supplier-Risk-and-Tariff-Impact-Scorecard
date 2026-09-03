"""
Data Ingestion Module
=====================
Loads raw procurement CSV exports, validates columns, parses types, and logs
data quality issues.
"""

import logging
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("scorecard.ingestion")


class DataIngestion:
    """Manages ingestion of all source datasets with schema and column verification."""

    REQUIRED_FILES = {
        "suppliers": "suppliers.csv",
        "purchase_orders": "purchase_orders.csv",
        "tariff_reference": "tariff_reference.csv",
        "tariff_scenarios": "tariff_scenarios.csv",
        "quality_defects": "quality_defects.csv",
    }

    def __init__(self, data_dir: Path | str = "data"):
        self.data_dir = Path(data_dir)

    def load_all(self) -> Dict[str, pd.DataFrame]:
        """Loads all required CSV files from the configured directory."""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory '{self.data_dir}' does not exist.")

        datasets: Dict[str, pd.DataFrame] = {}
        for key, filename in self.REQUIRED_FILES.items():
            filepath = self.data_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"Required data file missing: {filepath}")

            df = pd.read_csv(filepath)
            datasets[key] = df
            logger.info(f"Loaded {key} ({len(df)} rows) from {filepath.name}")

        self._validate_schemas(datasets)
        return datasets

    def _validate_schemas(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """Validates that all essential columns exist across datasets."""
        expected_columns = {
            "suppliers": {"Supplier_ID", "Supplier_Name", "Country", "Region", "Primary_Category"},
            "purchase_orders": {
                "PO_ID", "Supplier_ID", "Product_Category", "HS_Code", "PO_Date",
                "Quantity", "Unit_Cost_USD", "Promised_Delivery_Date", "PO_Status", "Defect_Flag"
            },
            "tariff_reference": {"Country", "HS_Code", "Base_Effective_Rate"},
            "tariff_scenarios": {"Scenario_Name", "Adjustment_Type", "Adjustment_Value"},
            "quality_defects": {"Defect_ID", "PO_ID", "Supplier_ID", "Defect_Qty"},
        }

        for key, req_cols in expected_columns.items():
            df = datasets[key]
            missing = req_cols - set(df.columns)
            if missing:
                raise ValueError(f"Dataset '{key}' is missing required columns: {missing}")

        logger.info("All source dataset schemas successfully validated.")
