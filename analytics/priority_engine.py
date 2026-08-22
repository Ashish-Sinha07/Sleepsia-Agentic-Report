"""Priority determination engine based on business rules."""

from analytics.insight_models import Priority
from analytics.business_rules import BusinessRules


class PriorityEngine:
    """
    Deterministic priority assignment based on business rules and metrics.

    Priority levels:
    - CRITICAL: Immediate action required (unprofitable, quality crisis, revenue collapse)
    - HIGH: Significant concern (poor advertising ROI, high returns/cancellations)
    - MEDIUM: Monitor closely (volatility, minor inefficiencies, emerging trends)
    - LOW: Positive trends (margin improvement, growth opportunity)
    - INFO: Informational (reference points, stable metrics)
    """

    def __init__(self, business_rules: BusinessRules):
        """Initialize with business rules."""
        self.rules = business_rules

    def determine_profitability_priority(
        self,
        margin_pct: float,
        platform: str = None,
        product: str = None,
    ) -> Priority:
        """Determine priority for profitability issues."""
        if margin_pct < 0:
            return Priority.CRITICAL

        passes, threshold = self.rules.evaluate_profit_margin(margin_pct, platform, product)
        if not passes:
            return Priority.HIGH

        if margin_pct >= threshold + 10:
            return Priority.INFO

        return Priority.MEDIUM

    def determine_advertising_priority(
        self,
        roas: float,
        acos_pct: float,
        platform: str = None,
        product: str = None,
    ) -> Priority:
        """Determine priority for advertising efficiency issues."""
        roas_passes, roas_threshold = self.rules.evaluate_roas(roas, platform, product)
        acos_passes, acos_threshold = self.rules.evaluate_acos(acos_pct, platform, product)

        if not roas_passes or not acos_passes:
            return Priority.MEDIUM

        if roas >= roas_threshold * 1.5 and acos_pct <= acos_threshold * 0.5:
            return Priority.INFO

        return Priority.LOW

    def determine_quality_priority(
        self,
        return_rate_pct: float,
        cancellation_rate_pct: float,
        platform: str = None,
        product: str = None,
    ) -> Priority:
        """Determine priority for quality issues."""
        returns_pass, returns_threshold = self.rules.evaluate_return_rate(
            return_rate_pct, platform, product
        )
        cancels_pass, cancels_threshold = self.rules.evaluate_cancellation_rate(
            cancellation_rate_pct, platform, product
        )

        if not returns_pass or not cancels_pass:
            if return_rate_pct > returns_threshold * 2 or cancellation_rate_pct > cancels_threshold * 2:
                return Priority.CRITICAL

            return Priority.HIGH

        return Priority.MEDIUM

    def determine_trend_priority(
        self,
        trend_direction: str,
        trend_strength: float,
    ) -> Priority:
        """Determine priority for trend-based insights."""
        if trend_direction == "downward":
            if trend_strength > 0.25:
                return Priority.CRITICAL
            elif trend_strength > 0.1:
                return Priority.HIGH
            else:
                return Priority.MEDIUM

        if trend_direction == "upward":
            if trend_strength > 0.25:
                return Priority.INFO
            else:
                return Priority.LOW

        return Priority.MEDIUM

    def determine_anomaly_priority(
        self,
        deviation_std_deviations: float,
        is_negative_anomaly: bool,
    ) -> Priority:
        """Determine priority for statistical anomalies."""
        if is_negative_anomaly:
            if deviation_std_deviations > 3:
                return Priority.CRITICAL
            elif deviation_std_deviations > 2:
                return Priority.HIGH
            else:
                return Priority.MEDIUM

        return Priority.INFO

    def determine_growth_priority(
        self,
        growth_pct: float,
        max_growth_threshold: float = None,
    ) -> Priority:
        """Determine priority for growth metrics."""
        if max_growth_threshold is None:
            max_growth_threshold = self.rules.maximum_advertising_spend_growth_pct

        if growth_pct < self.rules.minimum_revenue_growth_pct:
            return Priority.HIGH

        if growth_pct > max_growth_threshold:
            return Priority.MEDIUM

        if growth_pct > 0:
            return Priority.LOW

        return Priority.INFO
