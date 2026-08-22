"""Management summary generator for executive reporting."""

from datetime import date
from typing import Optional
from analytics.insight_models import (
    BusinessInsight,
    Recommendation,
    ManagementSummary,
    Priority,
)


class ManagementSummaryGenerator:
    """Generate concise management-level summaries."""

    @staticmethod
    def generate_summary(
        period_start: date,
        period_end: date,
        insights: list[BusinessInsight],
        recommendations: list[Recommendation],
        data_completeness_pct: float = 100.0,
        generated_at: Optional[date] = None,
    ) -> ManagementSummary:
        """
        Generate an executive-level management summary.

        Args:
            period_start: Start of analysis period
            period_end: End of analysis period
            insights: List of BusinessInsight objects
            recommendations: List of Recommendation objects
            data_completeness_pct: Percentage of data available (0-100)
            generated_at: Date summary was generated

        Returns:
            ManagementSummary ready for executive review
        """
        if generated_at is None:
            generated_at = date.today()

        critical_insights = [i for i in insights if i.priority == Priority.CRITICAL]
        high_insights = [i for i in insights if i.priority == Priority.HIGH]
        info_insights = [i for i in insights if i.priority == Priority.INFO]

        executive_summary = ManagementSummaryGenerator._build_executive_summary(
            critical_insights,
            high_insights,
            info_insights,
            period_start,
            period_end,
        )

        critical_issues = ManagementSummaryGenerator._format_critical_issues(
            critical_insights
        )
        high_priority_items = ManagementSummaryGenerator._format_high_priority_items(
            high_insights
        )
        key_opportunities = ManagementSummaryGenerator._format_opportunities(
            info_insights
        )

        top_recommendations = ManagementSummaryGenerator._format_top_recommendations(
            recommendations
        )

        health_score = ManagementSummaryGenerator._calculate_health_score(
            critical_insights,
            high_insights,
            data_completeness_pct,
        )

        return ManagementSummary(
            period_start=period_start,
            period_end=period_end,
            executive_summary=executive_summary,
            critical_issues=critical_issues,
            high_priority_items=high_priority_items,
            key_opportunities=key_opportunities,
            top_recommendations=top_recommendations,
            overall_health_score=health_score,
            data_completeness_pct=data_completeness_pct,
            timestamp=generated_at,
        )

    @staticmethod
    def _build_executive_summary(
        critical: list[BusinessInsight],
        high: list[BusinessInsight],
        info: list[BusinessInsight],
        period_start: date,
        period_end: date,
    ) -> str:
        """Build a concise executive summary."""
        issues_count = len(critical) + len(high)
        opportunities_count = len(info)

        if issues_count == 0 and opportunities_count == 0:
            return f"Analysis period {period_start} to {period_end}: All metrics within healthy ranges."

        summary_parts = []

        if critical:
            summary_parts.append(
                f"⚠️ {len(critical)} critical issue(s) require immediate attention."
            )

        if high:
            summary_parts.append(
                f"🔴 {len(high)} high-priority issue(s) need near-term resolution."
            )

        if info:
            summary_parts.append(f"✅ {len(info)} opportunity/opportunity area(s) identified.")

        return " ".join(summary_parts)

    @staticmethod
    def _format_critical_issues(critical_insights: list[BusinessInsight]) -> list[str]:
        """Format critical issues for management."""
        if not critical_insights:
            return []

        return [
            f"• {insight.title}: {insight.description}"
            for insight in critical_insights[:5]
        ]

    @staticmethod
    def _format_high_priority_items(high_insights: list[BusinessInsight]) -> list[str]:
        """Format high-priority items for management."""
        if not high_insights:
            return []

        return [
            f"• {insight.title}: {insight.description}" for insight in high_insights[:5]
        ]

    @staticmethod
    def _format_opportunities(info_insights: list[BusinessInsight]) -> list[str]:
        """Format opportunities for management."""
        if not info_insights:
            return []

        return [
            f"• {insight.title}: {insight.description}" for insight in info_insights[:5]
        ]

    @staticmethod
    def _format_top_recommendations(
        recommendations: list[Recommendation],
    ) -> list[str]:
        """Format top recommendations sorted by priority."""
        if not recommendations:
            return ["No recommendations at this time."]

        sorted_recs = sorted(
            recommendations,
            key=lambda r: (
                0 if r.priority == Priority.CRITICAL
                else 1 if r.priority == Priority.HIGH
                else 2 if r.priority == Priority.MEDIUM
                else 3 if r.priority == Priority.LOW
                else 4
            ),
        )

        return [
            f"• {rec.action} ({rec.priority.value.upper()}) - Owner: {rec.owner}"
            for rec in sorted_recs[:5]
        ]

    @staticmethod
    def _calculate_health_score(
        critical_insights: list[BusinessInsight],
        high_insights: list[BusinessInsight],
        data_completeness_pct: float,
    ) -> float:
        """
        Calculate overall business health score (0-100).

        Score components:
        - Start at 100
        - Deduct 20 for each critical issue
        - Deduct 5 for each high-priority issue
        - Apply data completeness adjustment
        """
        score = 100.0

        score -= len(critical_insights) * 20
        score -= len(high_insights) * 5

        score = max(0, min(100, score))

        data_adjustment = (data_completeness_pct / 100) * 100
        score = (score * 0.9) + (data_adjustment * 0.1)

        return round(score, 1)

    @staticmethod
    def format_for_management_report(summary: ManagementSummary) -> str:
        """Format summary for a management report."""
        lines = [
            "=" * 80,
            "BUSINESS PERFORMANCE SUMMARY",
            "=" * 80,
            f"\nAnalysis Period: {summary.period_start} to {summary.period_end}",
            f"Generated: {summary.timestamp}",
            f"\nOverall Health Score: {summary.overall_health_score}/100",
            f"Data Completeness: {summary.data_completeness_pct:.0f}%",
            "\n" + "-" * 80,
            "EXECUTIVE SUMMARY",
            "-" * 80,
            summary.executive_summary,
        ]

        if summary.critical_issues:
            lines.extend(
                [
                    "\n" + "-" * 80,
                    "CRITICAL ISSUES (Immediate Action Required)",
                    "-" * 80,
                ]
            )
            lines.extend(summary.critical_issues)

        if summary.high_priority_items:
            lines.extend(
                [
                    "\n" + "-" * 80,
                    "HIGH-PRIORITY ITEMS (30-Day Action)",
                    "-" * 80,
                ]
            )
            lines.extend(summary.high_priority_items)

        if summary.key_opportunities:
            lines.extend(
                [
                    "\n" + "-" * 80,
                    "KEY OPPORTUNITIES",
                    "-" * 80,
                ]
            )
            lines.extend(summary.key_opportunities)

        if summary.top_recommendations:
            lines.extend(
                [
                    "\n" + "-" * 80,
                    "RECOMMENDED ACTIONS",
                    "-" * 80,
                ]
            )
            lines.extend(summary.top_recommendations)

        lines.append("\n" + "=" * 80)

        return "\n".join(lines)
