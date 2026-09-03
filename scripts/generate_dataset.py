"""
Dataset Generator: Supplier Risk & Tariff-Impact Scorecard
==========================================================
Simulates a Coupa-style supplier portal export for a datacenter hardware
buyer (GPU servers, network switches, PDU/MEP equipment) sourcing from
three suppliers across three geographies.

Grounded in real July 2026 tariff conditions:
- China: ~35% effective (10% Section 122 + 25% Section 301); Section 122 sunsets ~Jul 24, 2026
- Mexico: USMCA-qualifying goods ~0% effective; non-qualifying line pays non-preferential rate
- United States: Domestic, 0% tariff exposure

Realistic Coupa data quality characteristics:
- Missing unit costs (pending invoice reconciliation)
- Duplicate PO entries (manual entry re-submissions)
- Inconsistent text casing
- In-transit orders without actual delivery dates
"""

import os
from pathlib import Path
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def generate_all_data(output_dir: str = "data", seed: int = 42) -> dict[str, pd.DataFrame]:
    random.seed(seed)
    np.random.seed(seed)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------------------
    # 1. SUPPLIER MASTER
    # ---------------------------------------------------------------------------
    suppliers = pd.DataFrame([
        {
            "Supplier_ID": "SUP-001",
            "Supplier_Name": "TitanForge Components",
            "Country": "United States",
            "Region": "Domestic",
            "City": "Columbus, OH",
            "Primary_Category": "GPU Servers",
            "Onboarded_Date": "2023-03-14",
            "USMCA_Qualifying": "N/A",
        },
        {
            "Supplier_ID": "SUP-002",
            "Supplier_Name": "Bajio Precision Systems",
            "Country": "Mexico",
            "Region": "Nearshore",
            "City": "Queretaro, MX",
            "Primary_Category": "Network Switches",
            "Onboarded_Date": "2024-01-22",
            "USMCA_Qualifying": "Y",
        },
        {
            "Supplier_ID": "SUP-003",
            "Supplier_Name": "Zhongxin Compute Manufacturing",
            "Country": "China",
            "Region": "Offshore",
            "City": "Shenzhen, CN",
            "Primary_Category": "PDU / MEP Equipment",
            "Onboarded_Date": "2022-09-01",
            "USMCA_Qualifying": "N/A",
        },
    ])

    # ---------------------------------------------------------------------------
    # 2. TARIFF REFERENCE TABLE
    # ---------------------------------------------------------------------------
    tariff_ref = pd.DataFrame([
        # United States - Domestic (0%)
        {
            "Country": "United States",
            "HS_Code": "8471.50",
            "Product_Category": "GPU Servers",
            "Base_MFN_Rate": 0.00,
            "Section_301_Rate": 0.00,
            "Section_122_Surcharge": 0.00,
            "USMCA_Qualifying": "N/A",
            "Base_Effective_Rate": 0.00,
        },
        {
            "Country": "United States",
            "HS_Code": "8517.62",
            "Product_Category": "Network Switches",
            "Base_MFN_Rate": 0.00,
            "Section_301_Rate": 0.00,
            "Section_122_Surcharge": 0.00,
            "USMCA_Qualifying": "N/A",
            "Base_Effective_Rate": 0.00,
        },
        {
            "Country": "United States",
            "HS_Code": "8537.10",
            "Product_Category": "PDU / MEP Equipment",
            "Base_MFN_Rate": 0.00,
            "Section_301_Rate": 0.00,
            "Section_122_Surcharge": 0.00,
            "USMCA_Qualifying": "N/A",
            "Base_Effective_Rate": 0.00,
        },
        # Mexico - USMCA-qualifying (0%) & Non-qualifying (2.5%)
        {
            "Country": "Mexico",
            "HS_Code": "8471.50",
            "Product_Category": "GPU Servers",
            "Base_MFN_Rate": 0.00,
            "Section_301_Rate": 0.00,
            "Section_122_Surcharge": 0.00,
            "USMCA_Qualifying": "Y",
            "Base_Effective_Rate": 0.00,
        },
        {
            "Country": "Mexico",
            "HS_Code": "8517.62",
            "Product_Category": "Network Switches",
            "Base_MFN_Rate": 0.00,
            "Section_301_Rate": 0.00,
            "Section_122_Surcharge": 0.00,
            "USMCA_Qualifying": "Y",
            "Base_Effective_Rate": 0.00,
        },
        {
            "Country": "Mexico",
            "HS_Code": "8537.10",
            "Product_Category": "PDU / MEP Equipment",
            "Base_MFN_Rate": 0.025,
            "Section_301_Rate": 0.00,
            "Section_122_Surcharge": 0.00,
            "USMCA_Qualifying": "N",
            "Base_Effective_Rate": 0.025,
        },
        # China - Section 122 (10%) + Section 301 (25%) = 35% effective
        {
            "Country": "China",
            "HS_Code": "8471.50",
            "Product_Category": "GPU Servers",
            "Base_MFN_Rate": 0.00,
            "Section_301_Rate": 0.25,
            "Section_122_Surcharge": 0.10,
            "USMCA_Qualifying": "N/A",
            "Base_Effective_Rate": 0.35,
        },
        {
            "Country": "China",
            "HS_Code": "8517.62",
            "Product_Category": "Network Switches",
            "Base_MFN_Rate": 0.00,
            "Section_301_Rate": 0.25,
            "Section_122_Surcharge": 0.10,
            "USMCA_Qualifying": "N/A",
            "Base_Effective_Rate": 0.35,
        },
        {
            "Country": "China",
            "HS_Code": "8537.10",
            "Product_Category": "PDU / MEP Equipment",
            "Base_MFN_Rate": 0.00,
            "Section_301_Rate": 0.25,
            "Section_122_Surcharge": 0.10,
            "USMCA_Qualifying": "N/A",
            "Base_Effective_Rate": 0.35,
        },
    ])

    # ---------------------------------------------------------------------------
    # 3. TARIFF SCENARIOS
    # ---------------------------------------------------------------------------
    tariff_scenarios = pd.DataFrame([
        {
            "Scenario_Name": "Current (Jul 2026)",
            "Adjustment_Type": "Additive",
            "Adjustment_Value": 0.00,
            "Description": "Baseline tariff rates: China ~35%, Mexico ~0%, US 0%",
        },
        {
            "Scenario_Name": "+10% escalation",
            "Adjustment_Type": "Additive",
            "Adjustment_Value": 0.10,
            "Description": "Moderate trade tension escalation (+10% tariff on offshore/nearshore non-US origins)",
        },
        {
            "Scenario_Name": "+25% escalation",
            "Adjustment_Type": "Additive",
            "Adjustment_Value": 0.25,
            "Description": "Aggressive trade penalty increase (+25% across foreign sourcing)",
        },
        {
            "Scenario_Name": "Section 122 sunset (China -10pt)",
            "Adjustment_Type": "Additive",
            "Adjustment_Value": -0.10,
            "Description": "Statutory sunset of Section 122 surcharge on China (-10% effective)",
        },
        {
            "Scenario_Name": "Universal 50% (worst case)",
            "Adjustment_Type": "Absolute",
            "Adjustment_Value": 0.50,
            "Description": "Universal blanket tariff rate of 50% on all foreign imports",
        },
    ])

    # ---------------------------------------------------------------------------
    # 4. PURCHASE ORDER PROFILES & SIMULATION
    # ---------------------------------------------------------------------------
    supplier_profiles = {
        "SUP-001": {
            "categories": ["GPU Servers", "PDU / MEP Equipment"],
            "unit_cost_range": {"GPU Servers": (18500, 24500), "PDU / MEP Equipment": (2200, 4100)},
            "lead_time_mean": 12,
            "lead_time_std": 3,
            "on_time_prob": 0.90,
            "defect_prob": 0.03,
            "incoterms": ["FOB", "DDP"],
            "freight": ["Truck", "Air"],
            "hs_map": {"GPU Servers": "8471.50", "PDU / MEP Equipment": "8537.10"},
            "customs_days_range": (0, 1),
        },
        "SUP-002": {
            "categories": ["Network Switches", "GPU Servers"],
            "unit_cost_range": {"Network Switches": (3100, 5200), "GPU Servers": (16200, 21800)},
            "lead_time_mean": 18,
            "lead_time_std": 4,
            "on_time_prob": 0.84,
            "defect_prob": 0.045,
            "incoterms": ["FOB", "CIF"],
            "freight": ["Truck", "Ocean"],
            "hs_map": {"Network Switches": "8517.62", "GPU Servers": "8471.50"},
            "customs_days_range": (1, 4),
        },
        "SUP-003": {
            "categories": ["PDU / MEP Equipment", "Network Switches", "GPU Servers"],
            "unit_cost_range": {"PDU / MEP Equipment": (1400, 2600), "Network Switches": (1900, 3400), "GPU Servers": (12800, 17600)},
            "lead_time_mean": 34,
            "lead_time_std": 9,
            "on_time_prob": 0.66,
            "defect_prob": 0.08,
            "incoterms": ["EXW", "FOB", "CIF"],
            "freight": ["Ocean", "Air"],
            "hs_map": {"PDU / MEP Equipment": "8537.10", "Network Switches": "8517.62", "GPU Servers": "8471.50"},
            "customs_days_range": (3, 12),
        },
    }

    start_date = datetime(2025, 1, 6)
    end_date = datetime(2026, 6, 28)
    n_target = 340

    rows = []
    po_counter = 1000
    date_span_days = (end_date - start_date).days

    for _ in range(n_target):
        supplier_id = random.choices(
            population=list(supplier_profiles.keys()),
            weights=[0.30, 0.32, 0.38],
            k=1
        )[0]
        profile = supplier_profiles[supplier_id]
        category = random.choice(profile["categories"])
        po_date = start_date + timedelta(days=random.randint(0, date_span_days))
        lead_time = max(3, int(np.random.normal(profile["lead_time_mean"], profile["lead_time_std"])))
        promised_delivery = po_date + timedelta(days=lead_time)

        on_time = random.random() < profile["on_time_prob"]
        if on_time:
            actual_delay = random.randint(-2, 0)
        else:
            actual_delay = random.randint(1, 21) if supplier_id != "SUP-003" else random.randint(2, 38)
        actual_delivery = promised_delivery + timedelta(days=actual_delay)

        in_transit = (end_date - po_date).days < 21 and actual_delivery > end_date
        if in_transit:
            actual_delivery_val = ""
            po_status = "In Transit"
        else:
            actual_delivery_val = actual_delivery.strftime("%Y-%m-%d")
            po_status = "Delivered"

        lo, hi = profile["unit_cost_range"][category]
        unit_cost = round(float(np.random.uniform(lo, hi)), 2)
        qty = random.choice([2, 4, 5, 8, 10, 12, 16, 20, 25, 40])

        defect_flag = "Y" if random.random() < profile["defect_prob"] and po_status == "Delivered" else "N"
        incoterm = random.choice(profile["incoterms"])
        freight = random.choice(profile["freight"])
        hs_code = profile["hs_map"][category]
        customs_lo, customs_hi = profile["customs_days_range"]
        customs_days = random.randint(customs_lo, customs_hi) if supplier_id != "SUP-001" else random.randint(0, 1)

        row = {
            "PO_ID": f"PO-{po_counter}",
            "Supplier_ID": supplier_id,
            "Product_Category": category,
            "HS_Code": hs_code,
            "PO_Date": po_date.strftime("%Y-%m-%d"),
            "Quantity": qty,
            "Unit_Cost_USD": unit_cost,
            "Incoterm": incoterm,
            "Freight_Mode": freight,
            "Promised_Delivery_Date": promised_delivery.strftime("%Y-%m-%d"),
            "Actual_Delivery_Date": actual_delivery_val,
            "Customs_Clearance_Days": customs_days,
            "Defect_Flag": defect_flag,
            "PO_Status": po_status,
        }
        rows.append(row)
        po_counter += 1

    po_df = pd.DataFrame(rows)

    # Inject casing variations on 5% of records (realistic Coupa manual entry variation)
    messy_idx = po_df.sample(frac=0.05, random_state=7).index
    for idx in messy_idx:
        field = random.choice(["Incoterm", "Freight_Mode", "Product_Category"])
        po_df.loc[idx, field] = str(po_df.loc[idx, field]).lower()

    # 4 duplicate PO entries
    dupe_rows = po_df.sample(n=4, random_state=11).copy()
    po_df = pd.concat([po_df, dupe_rows], ignore_index=True)

    # 6 missing unit costs (pending invoice reconciliation)
    missing_cost_idx = po_df.sample(n=6, random_state=13).index
    po_df.loc[missing_cost_idx, "Unit_Cost_USD"] = np.nan

    po_df = po_df.sort_values("PO_Date").reset_index(drop=True)

    # ---------------------------------------------------------------------------
    # 5. QUALITY DEFECT LOG
    # ---------------------------------------------------------------------------
    defect_types = ["DOA - Dead on Arrival", "Functional Failure", "Cosmetic Damage", "Packaging Damage", "Wrong Item Shipped"]
    resolutions = ["Replaced", "Credited", "Returned", "Pending"]

    defect_rows = []
    defect_id = 1
    for _, r in po_df[po_df["Defect_Flag"] == "Y"].iterrows():
        n_defects = random.randint(1, max(1, int(r["Quantity"] * 0.15)))
        detected = pd.to_datetime(r["Actual_Delivery_Date"]) + timedelta(days=random.randint(0, 5))
        defect_rows.append({
            "Defect_ID": f"DEF-{defect_id:04d}",
            "PO_ID": r["PO_ID"],
            "Supplier_ID": r["Supplier_ID"],
            "Defect_Type": random.choice(defect_types),
            "Defect_Qty": n_defects,
            "Detected_Date": detected.strftime("%Y-%m-%d"),
            "Resolution": random.choice(resolutions),
        })
        defect_id += 1

    defects_df = pd.DataFrame(defect_rows)

    # ---------------------------------------------------------------------------
    # Write to CSV
    # ---------------------------------------------------------------------------
    suppliers.to_csv(out_path / "suppliers.csv", index=False)
    tariff_ref.to_csv(out_path / "tariff_reference.csv", index=False)
    tariff_scenarios.to_csv(out_path / "tariff_scenarios.csv", index=False)
    po_df.to_csv(out_path / "purchase_orders.csv", index=False)
    defects_df.to_csv(out_path / "quality_defects.csv", index=False)

    return {
        "suppliers": suppliers,
        "tariff_reference": tariff_ref,
        "tariff_scenarios": tariff_scenarios,
        "purchase_orders": po_df,
        "quality_defects": defects_df,
    }


if __name__ == "__main__":
    data_map = generate_all_data("data")
    print("Dataset generation complete:")
    for name, df in data_map.items():
        print(f"  - {name}: {len(df)} rows")
