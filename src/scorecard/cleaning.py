"""
Data Cleaning and Preprocessing Module
======================================
Cleans procurement data, normalizes text casing, handles missing values,
parses dates, and flags/removes duplicate purchase orders while recording an audit log.
"""

import logging
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger("scorecard.cleaning")


class DataCleaner:
    """Cleans and standardizes raw procurement datasets."""

    def __init__(self):
        self.audit_log: Dict[str, Any] = {}

    def clean_datasets(
        self,
        suppliers: pd.DataFrame,
        purchase_orders: pd.DataFrame,
        tariff_reference: pd.DataFrame,
        tariff_scenarios: pd.DataFrame,
        quality_defects: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """Performs end-to-end cleaning on all datasets and returns cleaned frames + audit metrics."""
        po = purchase_orders.copy()
        sup = suppliers.copy()
        tref = tariff_reference.copy()
        tscen = tariff_scenarios.copy()
        qdef = quality_defects.copy()

        # Audit initial statistics
        raw_count = len(po)
        unique_pos = po["PO_ID"].nunique()
        duplicate_count = raw_count - unique_pos
        missing_costs = po["Unit_Cost_USD"].isna().sum()
        in_transit_count = (po["PO_Status"] == "In Transit").sum()

        logger.info(
            f"Audit: {raw_count} raw POs, {unique_pos} unique POs, "
            f"{duplicate_count} duplicate rows, {missing_costs} missing costs, {in_transit_count} in transit."
        )

        # 1. Deduplicate POs (retaining first occurrence, consistent with SQL/Excel)
        po["Is_First_Occurrence"] = (~po["PO_ID"].duplicated(keep="first")).astype(int)
        clean_po = po[po["Is_First_Occurrence"] == 1].copy()

        # 2. Parse and standardize dates
        clean_po["PO_Date"] = pd.to_datetime(clean_po["PO_Date"])
        clean_po["Promised_Delivery_Date"] = pd.to_datetime(clean_po["Promised_Delivery_Date"])
        clean_po["Actual_Delivery_Date"] = pd.to_datetime(clean_po["Actual_Delivery_Date"], errors="coerce")

        # 3. Normalize string casings
        for col in ["Incoterm", "Freight_Mode", "Product_Category", "PO_Status", "Defect_Flag"]:
            if col in clean_po.columns:
                clean_po[col] = clean_po[col].astype(str).str.strip()
                if col == "Incoterm":
                    clean_po[col] = clean_po[col].str.upper()
                elif col in ["Freight_Mode", "PO_Status"]:
                    clean_po[col] = clean_po[col].str.title()
                elif col == "Defect_Flag":
                    clean_po[col] = clean_po[col].str.upper()

        # 4. Compute Lead Time (Days)
        clean_po["Lead_Time_Days"] = (clean_po["Actual_Delivery_Date"] - clean_po["PO_Date"]).dt.days
        clean_po["Lead_Time_Days"] = clean_po["Lead_Time_Days"].fillna(0).astype(int)

        # 5. Determine On-Time Flag for Delivered POs
        clean_po["On_Time_Flag"] = np.where(
            clean_po["PO_Status"] == "Delivered",
            (clean_po["Actual_Delivery_Date"] <= clean_po["Promised_Delivery_Date"]).astype(int),
            np.nan
        )

        # 6. Merge Supplier Country & Tariff Rates
        clean_po = clean_po.merge(sup[["Supplier_ID", "Country", "Region"]], on="Supplier_ID", how="left")
        clean_po = clean_po.merge(
            tref[["Country", "HS_Code", "Base_Effective_Rate"]],
            on=["Country", "HS_Code"],
            how="left"
        )
        clean_po["Base_Effective_Rate"] = clean_po["Base_Effective_Rate"].fillna(0.0)

        # 7. Financial Calculations (Base Spend, Landed Cost Per Unit, Landed Spend, Tariff Dollars)
        clean_po["Base_Spend_USD"] = clean_po["Unit_Cost_USD"] * clean_po["Quantity"]
        clean_po["Landed_Cost_Per_Unit"] = clean_po["Unit_Cost_USD"] * (1 + clean_po["Base_Effective_Rate"])
        clean_po["Landed_Spend_USD"] = clean_po["Landed_Cost_Per_Unit"] * clean_po["Quantity"]
        clean_po["Tariff_Dollars"] = clean_po["Landed_Spend_USD"] - clean_po["Base_Spend_USD"]

        self.audit_log = {
            "raw_po_count": int(raw_count),
            "clean_po_count": int(len(clean_po)),
            "duplicate_po_count": int(duplicate_count),
            "missing_cost_count": int(missing_costs),
            "in_transit_count": int(in_transit_count),
            "delivered_count": int((clean_po["PO_Status"] == "Delivered").sum()),
        }

        return sup, clean_po, tref, tscen, qdef, self.audit_log
