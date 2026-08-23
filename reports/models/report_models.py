"""
Sleepsia Report Data Models

This module defines the data contract between the Analytics layer and the Reporting layer.

The Analytics layer must provide data in these exact models. The Reporting layer consumes
these models and generates PDF and Excel reports.

No business logic or calculations should occur in this module - only data structure definitions.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


@dataclass
class ProductMetrics:
    """Product-level financial and operational metrics for a single SKU on a single platform."""

    sku: str
    product_name: str
    units_sold: int
    gross_revenue: Decimal
    returns_count: int
    returns_percentage: Decimal
    organic_units: int
    paid_units: int
    ad_spend: Decimal
    net_ad_cost: Decimal
    tacos_percentage: Decimal
    net_profit: Decimal
    margin_percentage: Decimal

    # Optional additional metrics
    platform: Optional[str] = None
    orders: Optional[int] = None
    return_amount: Optional[Decimal] = None


@dataclass
class PlatformSummary:
    """Platform-level aggregated metrics."""

    platform_name: str
    gross_revenue: Decimal
    returns_refunds: Decimal
    returns_percentage: Decimal
    net_revenue: Decimal
    fulfillment_otif: Decimal
    ad_spend: Decimal
    net_ad_cost: Decimal
    tacos_percentage: Decimal
    net_profit: Decimal
    margin_percentage: Decimal

    # Product breakdown for this platform
    products: List[ProductMetrics] = field(default_factory=list)

    # Operational metrics
    orders: Optional[int] = None
    units_sold: Optional[int] = None


@dataclass
class ConsolidatedProductMetrics:
    """Product-level metrics aggregated across all platforms."""

    sku: str
    product_name: str
    all_units: int
    total_gross: Decimal
    all_returns: int
    returns_percentage: Decimal
    organic_paid_split: str  # e.g., "2139/1457"
    total_ad_cost: Decimal
    net_ad_cost: Decimal
    tacos_percentage: Decimal
    net_profit: Decimal
    margin_percentage: Decimal
    stock_dos: Decimal  # Days of stock


@dataclass
class PnLStatement:
    """Consolidated Profit & Loss statement for the entire business."""

    total_gross_gmv: Decimal
    less_returns_refunds: Decimal
    less_returns_percentage: Decimal
    net_revenue: Decimal
    less_cogs: Decimal
    less_cogs_percentage: Decimal
    less_ad_spend: Decimal
    less_ad_spend_percentage: Decimal
    less_commission_logistics: Decimal
    less_commission_logistics_percentage: Decimal
    grand_net_operating_profit: Decimal
    margin_percentage: Decimal


@dataclass
class ChannelEfficiency:
    """Channel/platform efficiency metrics for ranking."""

    rank: int
    platform_name: str
    orders: int
    units: int
    gross_sales: Decimal
    sales_share_percentage: Decimal
    ad_cost: Decimal
    tacos_percentage: Decimal
    net_profit: Decimal
    margin_percentage: Decimal
    otif_percentage: Decimal


@dataclass
class ReportMetadata:
    """Metadata about the report generation."""

    report_type: str  # "Management Summary", "Platform Report", etc.
    audit_date: datetime
    organization: str  # "Sleepsia India"
    scope: str  # "Omni-Channel (All Channels)" or more specific
    status: str  # "Official Verified Ledger", etc.
    generated_at: datetime = field(default_factory=datetime.now)
    generated_by: Optional[str] = None
    report_period_start: Optional[datetime] = None
    report_period_end: Optional[datetime] = None


@dataclass
class ManagementSummary:
    """Executive summary with key findings and recommendations."""

    summary_text: str
    key_findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)


@dataclass
class OmniChannelReport:
    """
    Complete omni-channel report data.

    This is the main data contract. The Analytics layer provides this object,
    and the Reporting layer (PDF/Excel generators) consumes it.

    IMPORTANT: The Analytics layer must populate ALL fields according to
    the business rules defined in .claude/business-rules.md
    """

    # Report metadata
    metadata: ReportMetadata

    # Platform-level summaries (one for each active platform)
    platforms: List[PlatformSummary] = field(default_factory=list)

    # Consolidated product metrics across all platforms
    consolidated_products: List[ConsolidatedProductMetrics] = field(default_factory=list)

    # Consolidated P&L
    pnl: Optional[PnLStatement] = None

    # Channel efficiency ranking
    channel_efficiency: List[ChannelEfficiency] = field(default_factory=list)

    # Executive summary and recommendations
    management_summary: Optional[ManagementSummary] = None

    # Additional metadata
    total_channels: int = 0
    active_platforms: int = 0
    total_skus: int = 0
    currency: str = "INR"

    def validate(self) -> bool:
        """
        Validate that all required fields are populated.

        Returns True if valid, raises ValueError otherwise.
        """
        if not self.metadata:
            raise ValueError("Report metadata is required")
        if not self.platforms:
            raise ValueError("At least one platform summary is required")
        if not self.pnl:
            raise ValueError("P&L statement is required")
        if not self.consolidated_products:
            raise ValueError("Consolidated product metrics are required")

        return True


# Type aliases for clarity
ReportData = OmniChannelReport
AnalyticsResult = OmniChannelReport
