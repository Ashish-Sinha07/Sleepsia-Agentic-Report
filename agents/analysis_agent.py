"""Data Analysis Agent - receives validated metrics and produces business insights."""

from datetime import date
from typing import Optional
from analytics.models import (
    ProductMetrics,
    PlatformMetrics,
    DailyMetrics,
    TrendMetrics,
    PerformanceFinding,
    AnalysisResult,
)


class DataAnalysisAgent:
    """
    Analyzes deterministically calculated metrics and produces business insights.

    CRITICAL CONSTRAINT: This agent NEVER calculates or invents financial metrics.
    All numbers come from the MetricsEngine or source data.
    The agent's role is to:
    1. Identify patterns and anomalies in pre-calculated metrics
    2. Summarize performance trends
    3. Explain likely business drivers based on data
    4. Recommend actions based on observed patterns
    5. Flag risks and opportunities
    """

    THRESHOLDS = {
        "healthy_margin": 15.0,
        "at_risk_margin": 0.0,
        "high_return_rate": 15.0,
        "high_cancellation_rate": 10.0,
        "poor_roas": 2.0,
        "poor_acos": 50.0,


        
        "high_organic_share": 70.0,
    }

    def analyze_product_performance(
        self,
        product_metrics: ProductMetrics,
        benchmark_metrics: Optional[ProductMetrics] = None,
    ) -> list[PerformanceFinding]:
        """Identify anomalies and insights for a single product."""
        findings = []

        if product_metrics.profit_margin_pct < self.THRESHOLDS["at_risk_margin"]:
            findings.append(
                PerformanceFinding(
                    finding_type="profitability",
                    severity="critical",
                    sku=product_metrics.sku,
                    metric_name="profit_margin_pct",
                    metric_value=product_metrics.profit_margin_pct,
                    threshold=self.THRESHOLDS["at_risk_margin"],
                    description=f"{product_metrics.product_name} is unprofitable with {product_metrics.profit_margin_pct:.2f}% margin",
                    recommendation="Review pricing, costs, or promotional activity. Consider increasing MSRP or reducing platform fees.",
                )
            )

        if product_metrics.return_rate_pct > self.THRESHOLDS["high_return_rate"]:
            findings.append(
                PerformanceFinding(
                    finding_type="quality",
                    severity="high",
                    sku=product_metrics.sku,
                    metric_name="return_rate_pct",
                    metric_value=product_metrics.return_rate_pct,
                    threshold=self.THRESHOLDS["high_return_rate"],
                    description=f"{product_metrics.product_name} has high return rate of {product_metrics.return_rate_pct:.2f}%",
                    recommendation="Investigate product quality, fit, or description accuracy. High returns erode profitability.",
                )
            )

        if product_metrics.cancellation_rate_pct > self.THRESHOLDS["high_cancellation_rate"]:
            findings.append(
                PerformanceFinding(
                    finding_type="fulfillment",
                    severity="high",
                    sku=product_metrics.sku,
                    metric_name="cancellation_rate_pct",
                    metric_value=product_metrics.cancellation_rate_pct,
                    threshold=self.THRESHOLDS["high_cancellation_rate"],
                    description=f"{product_metrics.product_name} has cancellation rate of {product_metrics.cancellation_rate_pct:.2f}%",
                    recommendation="Review fulfillment speed, inventory availability, or payment processing issues.",
                )
            )

        if product_metrics.ad_spend_inr > 0 and product_metrics.roas < self.THRESHOLDS["poor_roas"]:
            findings.append(
                PerformanceFinding(
                    finding_type="advertising",
                    severity="medium",
                    sku=product_metrics.sku,
                    metric_name="roas",
                    metric_value=product_metrics.roas,
                    threshold=self.THRESHOLDS["poor_roas"],
                    description=f"{product_metrics.product_name} has low ROAS of {product_metrics.roas:.2f}x",
                    recommendation="Review ad targeting, creative quality, or bid strategy. Consider reducing ad spend or improving landing pages.",
                )
            )

        if product_metrics.ad_spend_inr > 0 and product_metrics.acos_pct > self.THRESHOLDS["poor_acos"]:
            findings.append(
                PerformanceFinding(
                    finding_type="advertising",
                    severity="medium",
                    sku=product_metrics.sku,
                    metric_name="acos_pct",
                    metric_value=product_metrics.acos_pct,
                    threshold=self.THRESHOLDS["poor_acos"],
                    description=f"{product_metrics.product_name} has high ACOS of {product_metrics.acos_pct:.2f}%",
                    recommendation="High ad costs relative to sales. Optimize campaigns or reduce bid amounts.",
                )
            )

        if product_metrics.organic_share_pct > self.THRESHOLDS["high_organic_share"]:
            findings.append(
                PerformanceFinding(
                    finding_type="channel_mix",
                    severity="low",
                    sku=product_metrics.sku,
                    metric_name="organic_share_pct",
                    metric_value=product_metrics.organic_share_pct,
                    threshold=self.THRESHOLDS["high_organic_share"],
                    description=f"{product_metrics.product_name} has {product_metrics.organic_share_pct:.2f}% organic sales (low ad dependency)",
                    recommendation="Opportunity: This product has strong organic demand. Potential to reduce ad spend and improve margin.",
                )
            )

        return findings

    def analyze_platform_performance(
        self,
        platform_metrics: PlatformMetrics,
    ) -> list[PerformanceFinding]:
        """Identify anomalies and insights for a platform."""
        findings = []

        if platform_metrics.overall_profit_margin_pct < self.THRESHOLDS["at_risk_margin"]:
            findings.append(
                PerformanceFinding(
                    finding_type="platform_profitability",
                    severity="critical",
                    platform_id=platform_metrics.platform_id,
                    metric_name="platform_profit_margin_pct",
                    metric_value=platform_metrics.overall_profit_margin_pct,
                    threshold=self.THRESHOLDS["at_risk_margin"],
                    description=f"{platform_metrics.platform_name} is unprofitable with {platform_metrics.overall_profit_margin_pct:.2f}% margin",
                    recommendation="Platform is losing money. Review platform fee structure, product selection, or pricing strategy.",
                )
            )

        if platform_metrics.overall_return_rate_pct > self.THRESHOLDS["high_return_rate"]:
            findings.append(
                PerformanceFinding(
                    finding_type="platform_quality",
                    severity="high",
                    platform_id=platform_metrics.platform_id,
                    metric_name="overall_return_rate_pct",
                    metric_value=platform_metrics.overall_return_rate_pct,
                    threshold=self.THRESHOLDS["high_return_rate"],
                    description=f"{platform_metrics.platform_name} has platform-wide return rate of {platform_metrics.overall_return_rate_pct:.2f}%",
                    recommendation="Investigate product quality or platform-specific shipping/packaging issues.",
                )
            )

        if platform_metrics.platform_roas > 0 and platform_metrics.platform_roas < self.THRESHOLDS["poor_roas"]:
            findings.append(
                PerformanceFinding(
                    finding_type="platform_advertising",
                    severity="medium",
                    platform_id=platform_metrics.platform_id,
                    metric_name="platform_roas",
                    metric_value=platform_metrics.platform_roas,
                    threshold=self.THRESHOLDS["poor_roas"],
                    description=f"{platform_metrics.platform_name} advertising has ROAS of {platform_metrics.platform_roas:.2f}x",
                    recommendation="Platform-wide advertising efficiency is low. Review campaigns across all products.",
                )
            )

        return findings

    def analyze_daily_trend(
        self,
        trend_metrics: TrendMetrics,
        lookback_days: int = 7,
    ) -> list[PerformanceFinding]:
        """Identify trend anomalies and insights."""
        findings = []

        if trend_metrics.trend_direction == "downward" and trend_metrics.trend_strength > 0.1:
            findings.append(
                PerformanceFinding(
                    finding_type="trend",
                    severity="high",
                    metric_name=trend_metrics.metric_name,
                    metric_value=trend_metrics.trend_strength,
                    description=f"{trend_metrics.metric_name} shows downward trend (declining {trend_metrics.trend_strength*100:.1f}%)",
                    recommendation="Investigate causes of declining performance. Check for seasonal patterns, competitive activity, or operational issues.",
                )
            )

        if trend_metrics.trend_direction == "upward" and trend_metrics.trend_strength > 0.1:
            findings.append(
                PerformanceFinding(
                    finding_type="trend",
                    severity="low",
                    metric_name=trend_metrics.metric_name,
                    metric_value=trend_metrics.trend_strength,
                    description=f"{trend_metrics.metric_name} shows positive upward trend (growing {trend_metrics.trend_strength*100:.1f}%)",
                    recommendation="Capitalize on positive momentum. Analyze what's driving growth and replicate.",
                )
            )

        volatility = trend_metrics.max_daily - trend_metrics.min_daily
        if volatility > trend_metrics.average_daily * 0.5:
            findings.append(
                PerformanceFinding(
                    finding_type="volatility",
                    severity="medium",
                    metric_name=trend_metrics.metric_name,
                    metric_value=volatility,
                    description=f"{trend_metrics.metric_name} shows high volatility (range: {trend_metrics.min_daily:.0f} to {trend_metrics.max_daily:.0f})",
                    recommendation="Monitor closely for unusual fluctuations. May indicate supply chain, demand, or promotional irregularities.",
                )
            )

        return findings

    def detect_anomalies(
        self,
        metrics_list: list[ProductMetrics | PlatformMetrics],
    ) -> list[str]:
        """Detect statistical anomalies in metric distributions."""
        anomalies = []

        if not metrics_list:
            return anomalies

        margins = [m.profit_margin_pct if isinstance(m, ProductMetrics) else m.overall_profit_margin_pct
                   for m in metrics_list if (m.profit_margin_pct if isinstance(m, ProductMetrics) else m.overall_profit_margin_pct) is not None]

        if margins:
            mean_margin = sum(margins) / len(margins)
            std_dev = (sum((x - mean_margin) ** 2 for x in margins) / len(margins)) ** 0.5

            for m, margin in zip(metrics_list, margins):
                if std_dev > 0 and abs(margin - mean_margin) > 2 * std_dev:
                    sku = m.sku if isinstance(m, ProductMetrics) else m.platform_id
                    anomalies.append(
                        f"Statistical outlier: {sku} profit margin ({margin:.2f}%) deviates significantly from average ({mean_margin:.2f}%)"
                    )

        return anomalies

    def generate_analysis_result(
        self,
        period_start: date,
        period_end: date,
        analysis_type: str,
        findings: list[PerformanceFinding],
        anomalies: list[str],
        key_metrics: dict,
    ) -> AnalysisResult:
        """Synthesize findings into a management-ready analysis result."""

        critical_findings = [f for f in findings if f.severity == "critical"]
        high_findings = [f for f in findings if f.severity == "high"]
        opportunities = [f for f in findings if f.finding_type in ("channel_mix", "trend") and f.severity == "low"]

        risks = [f.description for f in critical_findings + high_findings]
        opps = [f.description for f in opportunities]

        recommendations = list(set(f.recommendation for f in findings if f.recommendation))[:5]

        summary = f"Analysis of {analysis_type} from {period_start} to {period_end}. "
        summary += f"Found {len(critical_findings)} critical, {len(high_findings)} high-severity issues. "
        if opps:
            summary += f"Identified {len(opportunities)} opportunities."
        else:
            summary += "No immediate opportunities identified."

        return AnalysisResult(
            period_start=period_start,
            period_end=period_end,
            analysis_type=analysis_type,
            summary=summary,
            key_metrics=key_metrics,
            performance_findings=findings,
            anomalies_detected=anomalies,
            risks_identified=risks,
            opportunities=opps,
            recommended_actions=recommendations,
            confidence="high" if len(findings) > 0 else "medium",
            data_completeness=1.0,
        )
