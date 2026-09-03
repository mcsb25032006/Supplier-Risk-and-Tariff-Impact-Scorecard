"""
Unit Tests: Data Validation & Ingestion
=======================================
Validates CSV schema enforcement, missing column handling, and Pydantic validation.
"""

import pytest
import pandas as pd
from pathlib import Path

from scorecard.ingestion import DataIngestion
from scorecard.cleaning import DataCleaner
from scorecard.models import SupplierModel, PurchaseOrderModel, TariffReferenceModel


def test_ingestion_valid_directory(project_root):
    data_dir = project_root / "data"
    ingestion = DataIngestion(data_dir)
    datasets = ingestion.load_all()

    assert "suppliers" in datasets
    assert "purchase_orders" in datasets
    assert "tariff_reference" in datasets
    assert "tariff_scenarios" in datasets
    assert "quality_defects" in datasets
    assert len(datasets["suppliers"]) >= 3
    assert len(datasets["purchase_orders"]) >= 300


def test_ingestion_missing_directory():
    ingestion = DataIngestion("non_existent_dir_123")
    with pytest.raises(FileNotFoundError):
        ingestion.load_all()


def test_schema_missing_column(tmp_path):
    # Write incomplete suppliers.csv
    incomplete_sup = pd.DataFrame([{"Supplier_ID": "SUP-001"}])
    incomplete_sup.to_csv(tmp_path / "suppliers.csv", index=False)
    for name in ["purchase_orders.csv", "tariff_reference.csv", "tariff_scenarios.csv", "quality_defects.csv"]:
        pd.DataFrame({"test": [1]}).to_csv(tmp_path / name, index=False)

    ingestion = DataIngestion(tmp_path)
    with pytest.raises(ValueError, match="missing required columns"):
        ingestion.load_all()


def test_cleaning_deduplication(sample_datasets):
    cleaner = DataCleaner()
    sup, clean_po, tref, tscen, qdef, audit = cleaner.clean_datasets(
        suppliers=sample_datasets["suppliers"],
        purchase_orders=sample_datasets["purchase_orders"],
        tariff_reference=sample_datasets["tariff_reference"],
        tariff_scenarios=sample_datasets["tariff_scenarios"],
        quality_defects=sample_datasets["quality_defects"]
    )

    # In sample_datasets, there were 8 total rows with 1 duplicate (PO-100 appeared twice)
    assert audit["raw_po_count"] == 8
    assert audit["duplicate_po_count"] == 1
    assert audit["clean_po_count"] == 7
    assert len(clean_po) == 7
    assert clean_po["PO_ID"].nunique() == 7
