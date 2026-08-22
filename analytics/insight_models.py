"""Pydantic models for insights and recommendations."""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class InsightCategory(str, Enum):
    """Categories of business insights."""
    SALES = "sales"
    ADVERTISING = "advertising"
    PROFITABILITY = "profitability"
    RETURNS = "returns"
    CANCELLATIONS = "cancellations"
    PLATFORM = "platform"
    PRODUCT = "product"
    TREND = "trend"
    ANOMALY = "anomaly"


class Priority(str, Enum):
    """Priority levels for insights and recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class BusinessInsight:
    """A single business insight with evidence."""

    insight_id: str
    category: InsightCategory
    priority: Priority

    title: str
    description: str

    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None

    sku: Optional[str] = None
    product_name: Optional[str] = None
    platform_id: Optional[str] = None
    platform_name: Optional[str] = None

    evidence: list[str] = field(default_factory=list)
    finding_sources: list[str] = field(default_factory=list)

    confidence_pct: float = 100.0
    business_impact: str = ""

    def add_evidence(self, evidence: str) -> None:
        """Add a piece of supporting evidence."""
        if evidence not in self.evidence:
            self.evidence.append(evidence)

    def add_finding_source(self, finding_id: str) -> None:
        """Track the source finding that triggered this insight."""
        if finding_id not in self.finding_sources:
            self.finding_sources.append(finding_id)


@dataclass
class Recommendation:
    """An evidence-based business recommendation."""

    recommendation_id: str
    action: str

    rationale: str
    expected_impact: str

    owner: str
    priority: Priority

    sku: Optional[str] = None
    product_name: Optional[str] = None
    platform_id: Optional[str] = None
    platform_name: Optional[str] = None

    evidence: list[str] = field(default_factory=list)
    insight_sources: list[str] = field(default_factory=list)

    confidence_pct: float = 100.0
    timeline: Optional[str] = None

    estimated_financial_impact_inr: Optional[float] = None
    risk_level: str = "medium"

    def add_evidence(self, evidence: str) -> None:
        """Add supporting evidence for this recommendation."""
        if evidence not in self.evidence:
            self.evidence.append(evidence)

    def add_insight_source(self, insight_id: str) -> None:
        """Track the source insight that triggered this recommendation."""
        if insight_id not in self.insight_sources:
            self.insight_sources.append(insight_id)


@dataclass
class ManagementSummary:
    """Executive-level summary of insights and recommendations."""

    period_start: date
    period_end: date

    executive_summary: str

    critical_issues: list[str]
    high_priority_items: list[str]
    key_opportunities: list[str]

    top_recommendations: list[str]

    overall_health_score: float
    data_completeness_pct: float

    timestamp: Optional[date] = None


@dataclass
class InsightRecommendationResult:
    """Complete result from Insight & Recommendation Agent."""

    analysis_period_start: date
    analysis_period_end: date
    generated_at: date

    insights: list[BusinessInsight]
    recommendations: list[Recommendation]

    management_summary: ManagementSummary

    overall_confidence: str
    data_completeness: float
    issues_count: int = 0
    opportunities_count: int = 0

    def __post_init__(self):
        """Calculate derived fields."""
        self.issues_count = len(
            [i for i in self.insights if i.priority in (Priority.CRITICAL, Priority.HIGH)]
        )
        self.opportunities_count = len(
            [i for i in self.insights if i.priority == Priority.INFO]
        )

    def critical_insights(self) -> list[BusinessInsight]:
        """Get all critical insights."""
        return [i for i in self.insights if i.priority == Priority.CRITICAL]

    def high_insights(self) -> list[BusinessInsight]:
        """Get all high-priority insights."""
        return [i for i in self.insights if i.priority == Priority.HIGH]

    def insights_by_category(self, category: InsightCategory) -> list[BusinessInsight]:
        """Get insights filtered by category."""
        return [i for i in self.insights if i.category == category]

    def recommendations_by_priority(self, priority: Priority) -> list[Recommendation]:
        """Get recommendations filtered by priority."""
        return [r for r in self.recommendations if r.priority == priority]
