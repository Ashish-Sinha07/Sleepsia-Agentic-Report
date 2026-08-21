"""Input model for Analysis Agent - contains all pre-calculated metrics."""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from analytics.models import (
    ProductMetrics,
    PlatformMetrics,
    DailyMetrics,
    TrendMetrics,
    PerformanceFinding,
)


@dataclass
class MetricComparison:
    """Comparison of current metric to previous period."""
    metric_name: str
    current_value: float
    previous_value: Optional[float] = None
    change_amount: Optional[float] = None
    change_percent: Optional[float] = None

    def summary(self) -> str:
        """Human-readable summary of comparison."""
        if self.previous_value is None:
            return f"{self.metric_name}: {self.current_value:.2f} (no prior data)"

        if self.change_percent is not None:
            direction = "↑" if self.change_percent > 0 else "↓"
            return f"{self.metric_name}: {self.current_value:.2f} ({direction} {abs(self.change_percent):.1f}%)"

        return f"{self.metric_name}: {self.current_value:.2f} (from {self.previous_value:.2f})"


@dataclass
class AnalysisInput:
    """
    Complete input for the Analysis Agent.
    Contains all pre-calculated metrics and comparisons.
    """

    analysis_date: date
    analysis_type: str  # "product", "platform", "daily", "portfolio"

    product_metrics: Optional[ProductMetrics] = None
    platform_metrics: Optional[PlatformMetrics] = None
    daily_metrics: Optional[DailyMetrics] = None

    previous_day_metrics: Optional[dict] = None
    metrics_7day: Optional[dict] = None
    metrics_30day: Optional[dict] = None

    current_day_comparisons: list[MetricComparison] = None
    week_comparisons: list[MetricComparison] = None
    month_comparisons: list[MetricComparison] = None

    trend_metrics: Optional[TrendMetrics] = None

    detected_anomalies: list[str] = None
    rule_based_findings: list[PerformanceFinding] = None

    context_notes: Optional[str] = None

    def __post_init__(self):
        """Initialize list fields."""
        if self.current_day_comparisons is None:
            self.current_day_comparisons = []
        if self.week_comparisons is None:
            self.week_comparisons = []
        if self.month_comparisons is None:
            self.month_comparisons = []
        if self.detected_anomalies is None:
            self.detected_anomalies = []
        if self.rule_based_findings is None:
            self.rule_based_findings = []

    def to_prompt_context(self) -> str:
        """Format input as context for the LLM prompt."""
        lines = []

        if self.product_metrics:
            lines.append(f"Product: {self.product_metrics.product_name} ({self.product_metrics.sku})")
            lines.append(f"  Units Sold: {self.product_metrics.units_sold}")
            lines.append(f"  Net Sales: ₹{self.product_metrics.net_sales_inr:,.2f}")
            lines.append(f"  Ad Spend: ₹{self.product_metrics.ad_spend_inr:,.2f}")
            lines.append(f"  ROAS: {self.product_metrics.roas:.2f}x")
            lines.append(f"  ACOS: {self.product_metrics.acos_pct:.1f}%")
            lines.append(f"  Profit Margin: {self.product_metrics.profit_margin_pct:.1f}%")
            lines.append(f"  Status: {self.product_metrics.profitability_status}")
            lines.append("")

        if self.platform_metrics:
            lines.append(f"Platform: {self.platform_metrics.platform_name}")
            lines.append(f"  Total Units: {self.platform_metrics.total_units_sold}")
            lines.append(f"  Total Sales: ₹{self.platform_metrics.total_net_sales_inr:,.2f}")
            lines.append(f"  Platform ROAS: {self.platform_metrics.platform_roas:.2f}x")
            lines.append(f"  Overall Margin: {self.platform_metrics.overall_profit_margin_pct:.1f}%")
            lines.append(f"  Product Count: {self.platform_metrics.product_count}")
            lines.append("")

        if self.current_day_comparisons:
            lines.append("Day-over-Day Changes:")
            for comp in self.current_day_comparisons:
                lines.append(f"  • {comp.summary()}")
            lines.append("")

        if self.week_comparisons:
            lines.append("7-Day Trend:")
            for comp in self.week_comparisons:
                lines.append(f"  • {comp.summary()}")
            lines.append("")

        if self.month_comparisons:
            lines.append("30-Day Trend:")
            for comp in self.month_comparisons:
                lines.append(f"  • {comp.summary()}")
            lines.append("")

        if self.trend_metrics:
            lines.append(f"Trend Analysis ({self.trend_metrics.metric_name}):")
            lines.append(f"  Direction: {self.trend_metrics.trend_direction}")
            lines.append(f"  Strength: {self.trend_metrics.trend_strength * 100:.1f}%")
            lines.append(f"  Average Daily: {self.trend_metrics.average_daily:.2f}")
            lines.append(f"  Min/Max: {self.trend_metrics.min_daily:.2f} / {self.trend_metrics.max_daily:.2f}")
            if self.trend_metrics.day_7_average:
                lines.append(f"  7-Day Avg: {self.trend_metrics.day_7_average:.2f}")
            if self.trend_metrics.day_30_average:
                lines.append(f"  30-Day Avg: {self.trend_metrics.day_30_average:.2f}")
            lines.append("")

        if self.detected_anomalies:
            lines.append("Detected Anomalies:")
            for anomaly in self.detected_anomalies:
                lines.append(f"  • {anomaly}")
            lines.append("")

        if self.rule_based_findings:
            critical = [f for f in self.rule_based_findings if f.severity == "critical"]
            high = [f for f in self.rule_based_findings if f.severity == "high"]

            if critical:
                lines.append("Critical Issues:")
                for finding in critical:
                    lines.append(f"  • {finding.description}")
                lines.append("")

            if high:
                lines.append("High-Priority Issues:")
                for finding in high:
                    lines.append(f"  • {finding.description}")
                lines.append("")

        if self.context_notes:
            lines.append(f"Context: {self.context_notes}")
            lines.append("")

        return "\n".join(lines)
