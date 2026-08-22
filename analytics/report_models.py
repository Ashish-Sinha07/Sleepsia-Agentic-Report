"""Pydantic models for report generation."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
from enum import Enum


class ReportType(str, Enum):
    """Supported report types."""
    PRODUCT_PLATFORM_DAILY = "product_platform_daily"
    PRODUCT_DAILY = "product_daily"
    PLATFORM_DAILY = "platform_daily"
    MANAGEMENT_DAILY_SUMMARY = "management_daily_summary"


@dataclass
class MetricWithSource:
    """A metric value with source reference."""
    value: float
    source: str
    unit: str = ""
    previous_value: Optional[float] = None
    change_pct: Optional[float] = None


@dataclass
class KeyMetric:
    """Key performance metric for a report section."""
    name: str
    value: float
    unit: str
    threshold: Optional[float] = None
    status: Optional[str] = None
    previous_value: Optional[float] = None


@dataclass
class ProductSection:
    """Report section for a single product."""
    sku: str
    product_name: str

    units_sold: int
    net_sales_inr: float

    ad_spend_inr: float
    roas: float
    acos_pct: float

    organic_share_pct: float

    profit_margin_pct: float
    profitability_status: str

    return_rate_pct: float
    cancellation_rate_pct: float

    key_metrics: list[KeyMetric] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)


@dataclass
class PlatformSection:
    """Report section for a single platform."""
    platform_id: str
    platform_name: str

    total_units_sold: int
    total_net_sales_inr: float

    total_ad_spend_inr: float
    platform_roas: float
    platform_acos_pct: float

    total_organic_sales_inr: float
    organic_share_pct: float

    overall_profit_margin_pct: float

    product_count: int
    top_product: Optional[str] = None

    key_metrics: list[KeyMetric] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)


@dataclass
class AdvertisingSection:
    """Advertising performance section."""
    total_ad_spend_inr: float
    total_attributed_sales_inr: float
    overall_roas: float
    overall_acos_pct: float

    impressions: int
    clicks: int
    ctr_pct: float

    attributed_units: int
    attributed_orders: int

    cpc_inr: Optional[float] = None
    cps_inr: Optional[float] = None


@dataclass
class ProfitabilitySection:
    """Profitability analysis section."""
    total_net_sales_inr: float
    total_cost_inr: float
    total_contribution_inr: float
    overall_profit_margin_pct: float

    products_healthy: int
    products_at_risk: int
    products_unprofitable: int

    cost_breakdown: dict[str, float] = field(default_factory=dict)


@dataclass
class QualitySection:
    """Returns and cancellations section."""
    total_units_sold: int
    total_units_returned: int
    total_refund_amount_inr: float
    overall_return_rate_pct: float

    total_units_cancelled: int
    overall_cancellation_rate_pct: float


@dataclass
class OverallMetrics:
    """Overall business metrics for the report."""
    report_date: date

    total_orders: int
    total_units_sold: int
    total_net_sales_inr: float
    total_gross_sales_inr: float

    total_ad_spend_inr: float
    total_organic_sales_inr: float
    organic_share_pct: float

    total_cost_inr: float
    total_contribution_inr: float
    overall_profit_margin_pct: float

    total_return_rate_pct: float
    total_cancellation_rate_pct: float

    product_count: int
    platform_count: int


@dataclass
class Insight:
    """Report insight."""
    title: str
    description: str
    priority: str
    category: str


@dataclass
class Recommendation:
    """Report recommendation."""
    action: str
    rationale: str
    owner: str
    priority: str
    timeline: Optional[str] = None


@dataclass
class Report:
    """Canonical report object - the main output of report generation."""

    report_id: str
    report_date: date
    report_type: ReportType

    title: str
    executive_summary: str

    overall_metrics: OverallMetrics

    product_sections: list[ProductSection] = field(default_factory=list)
    platform_sections: list[PlatformSection] = field(default_factory=list)

    advertising_section: Optional[AdvertisingSection] = None
    profitability_section: Optional[ProfitabilitySection] = None
    quality_section: Optional[QualitySection] = None

    insights: list[Insight] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)

    generated_at: datetime = field(default_factory=datetime.now)

    data_completeness_pct: float = 100.0
    notes: Optional[str] = None
