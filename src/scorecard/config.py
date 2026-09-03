"""
Configuration Module for Supplier Risk & Tariff-Impact Scorecard
================================================================
Defines system-wide constants, scoring weights, RAG thresholds, alert limits,
and file path defaults.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RiskWeights:
    """Weights for the composite supplier risk score. Sum must equal 1.0."""
    on_time: float = 0.30
    lead_time_volatility: float = 0.20
    tariff_exposure: float = 0.25
    defect_rate: float = 0.25

    def __post_init__(self):
        total = self.on_time + self.lead_time_volatility + self.tariff_exposure + self.defect_rate
        if not abs(total - 1.0) < 1e-6:
            raise ValueError(f"Risk weights must sum to 1.0, got {total}")


@dataclass(frozen=True)
class RAGThresholds:
    """Thresholds for RAG (Red/Yellow/Green) risk category segmentation."""
    red_threshold: float = 30.0    # Composite Score >= 30 -> Red (Critical / High Risk)
    yellow_threshold: float = 15.0 # Composite Score >= 15 -> Yellow (Medium / Moderate Risk)
                                   # Composite Score < 15  -> Green (Low Risk)


@dataclass(frozen=True)
class AlertThresholds:
    """Thresholds for flagging period-over-period supplier performance changes."""
    risk_score_delta_alert: float = 5.0      # Trigger alert if score increases by >= 5.0 pts
    on_time_drop_alert_pct: float = 0.05      # Trigger alert if on-time drops by >= 5.0% (0.05)
    defect_rate_spike_pct: float = 0.02       # Trigger alert if defect rate rises by >= 2.0% (0.02)
    tariff_exposure_jump_pct: float = 0.05    # Trigger alert if tariff exposure jumps by >= 5.0% (0.05)


@dataclass
class ScorecardConfig:
    """Master configuration container for data pipeline execution."""
    data_dir: Path = Path("data")
    output_dir: Path = Path("output")
    sql_dir: Path = Path("sql")
    powerbi_dir: Path = Path("powerbi")
    excel_dir: Path = Path("excel")
    lead_time_stdev_cap_days: float = 20.0  # Max lead-time standard deviation for 100% component score
    weights: RiskWeights = field(default_factory=RiskWeights)
    rag: RAGThresholds = field(default_factory=RAGThresholds)
    alerts: AlertThresholds = field(default_factory=AlertThresholds)

    @classmethod
    def default(cls) -> "ScorecardConfig":
        return cls()
