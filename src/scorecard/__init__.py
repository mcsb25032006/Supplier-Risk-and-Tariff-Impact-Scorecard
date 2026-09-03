"""
Supplier Risk & Tariff-Impact Scorecard Package
================================================
A production-grade Python package for procurement intelligence, landed-cost
modeling, tariff exposure analysis, supplier risk scoring, scenario modeling,
and Power BI export generation.
"""

__version__ = "1.0.0"
__author__ = "Procurement Intelligence & Data Architecture Team"

from .config import ScorecardConfig
from .ingestion import DataIngestion
from .cleaning import DataCleaner
from .risk_engine import RiskScoringEngine
from .scenario_engine import TariffScenarioEngine
from .history_tracker import HistoryTracker
from .database import DatabaseManager
from .reporting import ReportGenerator
from .pipeline import ScorecardPipeline

__all__ = [
    "ScorecardConfig",
    "DataIngestion",
    "DataCleaner",
    "RiskScoringEngine",
    "TariffScenarioEngine",
    "HistoryTracker",
    "DatabaseManager",
    "ReportGenerator",
    "ScorecardPipeline",
]
