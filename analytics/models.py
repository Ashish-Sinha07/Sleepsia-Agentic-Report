"""Pydantic models for business metrics and analysis."""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from enum import Enum


class TimeGrain(str, Enum):
    """Supported time grains for analysis."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class MetricComparison:
    """Comparison of a metric to previous period."""
    current_value: float
    previous_value: Optional[float] = None
    change_amount: Optional[float] = None
    change_percent: Optional[float] = None

    def __post_init__(self):
        if self.previous_value is not None and self.previous_value != 0:
            self.change_amount = self.current_value - self.previous_value
            self.change_percent = (self.change_amount / self.previous_value) * 100


@dataclass
class ProductMetrics:
    """Metrics for a single product."""
    sku: str
    product_name: str

    units_sold: int
    gross_sales_inr: float
    net_sales_inr: float
    discount_inr: float

    ad_spend_inr: float
    ad_attributed_units: int
    ad_attributed_sales_inr: float

    organic_units: int
    organic_sales_inr: float
    organic_share_pct: float

    roas: float
    acos_pct: float

    product_cost_inr: float
    platform_fee_inr: float
    shipping_cost_inr: float
    payment_fee_inr: float
    other_cost_inr: float
    total_cost_inr: float

    units_returned: int
    refund_amount_inr: float
    return_rate_pct: float

    units_cancelled: int
    cancellation_rate_pct: float

    contribution_inr: float
    profit_margin_pct: float
    profitability_status: str


@dataclass
class PlatformMetrics:
    """Aggregated metrics for a platform."""
    platform_id: str
    platform_name: str

    total_orders: int
    total_units_sold: int
    total_gross_sales_inr: float
    total_net_sales_inr: float
    total_discount_inr: float

    total_ad_spend_inr: float
    total_ad_attributed_units: int
    total_ad_attributed_sales_inr: float

    total_organic_units: int
    total_organic_sales_inr: float

    platform_roas: float
    platform_acos_pct: float

    total_product_cost_inr: float
    total_platform_fee_inr: float
    total_shipping_cost_inr: float
    total_payment_fee_inr: float
    total_other_cost_inr: float
    total_cost_inr: float

    total_returns: int
    total_refund_inr: float
    overall_return_rate_pct: float

    total_cancellations: int
    overall_cancellation_rate_pct: float

    total_contribution_inr: float
    overall_profit_margin_pct: float

    product_count: int
    top_product_sku: Optional[str] = None
    top_product_sales_inr: Optional[float] = None


@dataclass
class DailyMetrics:
    """Daily aggregated metrics across all products and platforms."""
    date: date

    total_orders: int
    total_units_sold: int
    total_gross_sales_inr: float
    total_net_sales_inr: float

    total_ad_spend_inr: float
    total_ad_attributed_units: int
    total_ad_attributed_sales_inr: float

    total_organic_units: int
    total_organic_sales_inr: float

    total_cost_inr: float
    total_contribution_inr: float
    overall_profit_margin_pct: float

    total_returns: int
    total_refund_inr: float

    total_cancellations: int


@dataclass
class TrendMetrics:
    """Trend analysis over a time period."""
    metric_name: str
    period_start: date
    period_end: date
    days: int

    average_daily: float
    min_daily: float
    max_daily: float

    day_7_average: Optional[float] = None
    day_30_average: Optional[float] = None

    trend_direction: str = "stable"
    trend_strength: float = 0.0


@dataclass
class PerformanceFinding:
    """A single business insight or anomaly."""
    finding_type: str
    severity: str
    sku: Optional[str] = None
    platform_id: Optional[str] = None
    metric_name: str = ""
    metric_value: float = 0.0
    threshold: Optional[float] = None
    description: str = ""
    recommendation: str = ""


@dataclass
class AnalysisResult:
    """Complete analysis result from the Data Analysis Agent."""
    period_start: date
    period_end: date
    analysis_type: str

    summary: str
    key_metrics: dict

    performance_findings: list[PerformanceFinding]

    anomalies_detected: list[str]
    risks_identified: list[str]
    opportunities: list[str]

    recommended_actions: list[str]

    confidence: str
    data_completeness: float
