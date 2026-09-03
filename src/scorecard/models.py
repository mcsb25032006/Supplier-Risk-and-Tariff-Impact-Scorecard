"""
Data Models and Validation Schemas
==================================
Pydantic schemas ensuring input data integrity and structured typing.
"""

from typing import Optional, Literal
from datetime import date
from pydantic import BaseModel, Field, field_validator


class SupplierModel(BaseModel):
    Supplier_ID: str
    Supplier_Name: str
    Country: str
    Region: Literal["Domestic", "Nearshore", "Offshore"]
    City: str
    Primary_Category: str
    Onboarded_Date: date
    USMCA_Qualifying: Literal["Y", "N", "N/A"]


class TariffReferenceModel(BaseModel):
    Country: str
    HS_Code: str
    Product_Category: str
    Base_MFN_Rate: float = Field(ge=0.0, le=1.0)
    Section_301_Rate: float = Field(ge=0.0, le=1.0)
    Section_122_Surcharge: float = Field(ge=0.0, le=1.0)
    USMCA_Qualifying: Literal["Y", "N", "N/A"]
    Base_Effective_Rate: float = Field(ge=0.0, le=1.0)


class TariffScenarioModel(BaseModel):
    Scenario_Name: str
    Adjustment_Type: Literal["Additive", "Absolute"]
    Adjustment_Value: float
    Description: str


class PurchaseOrderModel(BaseModel):
    PO_ID: str
    Supplier_ID: str
    Product_Category: str
    HS_Code: str
    PO_Date: date
    Quantity: int = Field(gt=0)
    Unit_Cost_USD: Optional[float] = Field(default=None, ge=0.0)
    Incoterm: str
    Freight_Mode: str
    Promised_Delivery_Date: date
    Actual_Delivery_Date: Optional[date] = None
    Customs_Clearance_Days: int = Field(ge=0)
    Defect_Flag: Literal["Y", "N"]
    PO_Status: Literal["Delivered", "In Transit", "Open", "Cancelled"]


class QualityDefectModel(BaseModel):
    Defect_ID: str
    PO_ID: str
    Supplier_ID: str
    Defect_Type: str
    Defect_Qty: int = Field(gt=0)
    Detected_Date: date
    Resolution: Literal["Replaced", "Credited", "Returned", "Pending"]


class SupplierKPIResult(BaseModel):
    Supplier_ID: str
    Supplier_Name: str
    Country: str
    Region: str
    Primary_Category: str
    Delivered_POs: int
    In_Transit_POs: int
    On_Time_POs: int
    On_Time_Rate: float
    Avg_Lead_Time_Days: float
    Median_Lead_Time_Days: float
    Lead_Time_StDev_Days: float
    Total_Base_Spend: float
    Total_Landed_Spend: float
    Tariff_Dollars: float
    Tariff_Exposure_Pct: float
    Defect_POs: int
    Defect_Rate_Pct: float
    Avg_Customs_Days: float
    Composite_Risk_Score: float
    RAG_Status: Literal["Green", "Yellow", "Red"]
