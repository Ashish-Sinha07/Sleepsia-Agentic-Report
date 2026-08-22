"""Business rules configuration for alerts and recommendations."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BusinessRules:
    """
    Configurable business thresholds for alerts and recommendations.
    All thresholds are deterministic and can be overridden by platform or product.
    """

    minimum_roas: float = 2.0
    maximum_acos_pct: float = 50.0
    minimum_profit_margin_pct: float = 15.0
    maximum_return_rate_pct: float = 15.0
    maximum_cancellation_rate_pct: float = 10.0
    maximum_advertising_spend_growth_pct: float = 30.0
    minimum_revenue_growth_pct: float = -20.0

    platform_overrides: dict[str, "BusinessRules"] = field(default_factory=dict)
    product_overrides: dict[str, "BusinessRules"] = field(default_factory=dict)

    def get_threshold(
        self,
        threshold_name: str,
        platform: Optional[str] = None,
        product: Optional[str] = None,
    ) -> float:
        """
        Get a threshold value with optional platform/product overrides.

        Args:
            threshold_name: Name of threshold (e.g., 'minimum_roas', 'maximum_acos_pct')
            platform: Optional platform ID for platform-specific override
            product: Optional product SKU for product-specific override

        Returns:
            The appropriate threshold value
        """
        if product and product in self.product_overrides:
            rules = self.product_overrides[product]
            if hasattr(rules, threshold_name):
                return getattr(rules, threshold_name)

        if platform and platform in self.platform_overrides:
            rules = self.platform_overrides[platform]
            if hasattr(rules, threshold_name):
                return getattr(rules, threshold_name)

        return getattr(self, threshold_name)

    def evaluate_roas(
        self,
        roas: float,
        platform: Optional[str] = None,
        product: Optional[str] = None,
    ) -> tuple[bool, float]:
        """
        Evaluate if ROAS meets minimum threshold.

        Returns:
            (passes, threshold_value)
        """
        threshold = self.get_threshold("minimum_roas", platform, product)
        return roas >= threshold, threshold

    def evaluate_acos(
        self,
        acos_pct: float,
        platform: Optional[str] = None,
        product: Optional[str] = None,
    ) -> tuple[bool, float]:
        """
        Evaluate if ACOS is within maximum threshold.

        Returns:
            (passes, threshold_value)
        """
        threshold = self.get_threshold("maximum_acos_pct", platform, product)
        return acos_pct <= threshold, threshold

    def evaluate_profit_margin(
        self,
        margin_pct: float,
        platform: Optional[str] = None,
        product: Optional[str] = None,
    ) -> tuple[bool, float]:
        """
        Evaluate if profit margin meets minimum threshold.

        Returns:
            (passes, threshold_value)
        """
        threshold = self.get_threshold("minimum_profit_margin_pct", platform, product)
        return margin_pct >= threshold, threshold

    def evaluate_return_rate(
        self,
        return_rate_pct: float,
        platform: Optional[str] = None,
        product: Optional[str] = None,
    ) -> tuple[bool, float]:
        """
        Evaluate if return rate is within maximum threshold.

        Returns:
            (passes, threshold_value)
        """
        threshold = self.get_threshold("maximum_return_rate_pct", platform, product)
        return return_rate_pct <= threshold, threshold

    def evaluate_cancellation_rate(
        self,
        cancellation_rate_pct: float,
        platform: Optional[str] = None,
        product: Optional[str] = None,
    ) -> tuple[bool, float]:
        """
        Evaluate if cancellation rate is within maximum threshold.

        Returns:
            (passes, threshold_value)
        """
        threshold = self.get_threshold(
            "maximum_cancellation_rate_pct", platform, product
        )
        return cancellation_rate_pct <= threshold, threshold
