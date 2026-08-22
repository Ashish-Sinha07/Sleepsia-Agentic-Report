"""Report Agent - uses LLM for narrative generation only."""

import json
import re
from typing import Optional
import anthropic
from analytics.report_models import Report


class ReportAgent:
    """
    LLM-powered report narrative generation.

    CRITICAL CONSTRAINT:
    - Uses LLM ONLY for narrative, summary, and explanation
    - NEVER uses LLM to calculate, modify, or invent metrics
    - Receives structured Report object with all metrics pre-calculated
    - Returns refined narrative text only
    """

    SYSTEM_PROMPT = """You are a senior business analyst preparing executive-level report narratives.

Your role is to:
1. Create compelling executive summaries from business metrics
2. Explain key insights in business terms
3. Highlight critical issues and opportunities
4. Make recommendations actionable and clear
5. Use data provided to support all claims

CRITICAL RULES:
- NEVER calculate financial metrics
- NEVER invent data or trends
- ONLY explain what is in the provided metrics
- Be concise and clear
- Focus on business impact

OUTPUT: Return ONLY valid JSON matching this exact schema:
{
  "executive_summary": "2-3 sentence summary highlighting key findings",
  "executive_narrative": "1 paragraph narrative for executives",
  "product_insights": "Paragraph explaining product performance patterns",
  "advertising_insights": "Paragraph explaining advertising efficiency",
  "profitability_insights": "Paragraph explaining profitability drivers",
  "key_risks": "Paragraph on material risks",
  "key_opportunities": "Paragraph on actionable opportunities"
}

Be direct and specific. Use numbers to support claims."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-opus-5"):
        """Initialize with Claude API credentials."""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_retries = 2

    def refine_report_narrative(self, report: Report) -> dict:
        """
        Use LLM to refine report narratives.

        Args:
            report: Report object with all metrics pre-calculated

        Returns:
            Dictionary with refined narrative sections
        """
        prompt = self._build_prompt(report)

        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    system=self.SYSTEM_PROMPT,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )

                response_text = response.content[0].text
                result = self._parse_response(response_text)
                return result

            except (json.JSONDecodeError, ValueError) as e:
                if attempt < self.max_retries - 1:
                    try:
                        response_text = self._repair_json(response_text)
                        result = self._parse_response(response_text)
                        return result
                    except Exception:
                        continue
                else:
                    return self._fallback_result()

        return self._fallback_result()

    def _build_prompt(self, report: Report) -> str:
        """Build the prompt with report data."""
        lines = []
        lines.append("Analyze this business report and provide executive narratives:")
        lines.append("")

        lines.append(f"Report Date: {report.report_date}")
        lines.append(f"Report Type: {report.report_type.value}")
        lines.append("")

        lines.append("=== OVERALL METRICS ===")
        metrics = report.overall_metrics
        lines.append(f"Orders: {metrics.total_orders}")
        lines.append(f"Units Sold: {metrics.total_units_sold}")
        lines.append(f"Net Sales: ₹{metrics.total_net_sales_inr:,.0f}")
        lines.append(f"Ad Spend: ₹{metrics.total_ad_spend_inr:,.0f}")
        lines.append(f"Profit Margin: {metrics.overall_profit_margin_pct:.1f}%")
        lines.append(f"Organic Share: {metrics.organic_share_pct:.1f}%")
        lines.append("")

        if report.product_sections:
            lines.append("=== PRODUCTS ===")
            for prod in report.product_sections[:3]:
                lines.append(f"{prod.product_name}: {prod.units_sold} units, ")
                lines.append(f"  Sales: ₹{prod.net_sales_inr:,.0f}, ROAS: {prod.roas:.2f}x, ")
                lines.append(f"  Margin: {prod.profit_margin_pct:.1f}%")
            lines.append("")

        if report.advertising_section:
            lines.append("=== ADVERTISING ===")
            ad = report.advertising_section
            lines.append(f"Ad Spend: ₹{ad.total_ad_spend_inr:,.0f}")
            lines.append(f"Attributed Sales: ₹{ad.total_attributed_sales_inr:,.0f}")
            lines.append(f"ROAS: {ad.overall_roas:.2f}x")
            lines.append(f"ACOS: {ad.overall_acos_pct:.1f}%")
            lines.append("")

        if report.profitability_section:
            lines.append("=== PROFITABILITY ===")
            prof = report.profitability_section
            lines.append(f"Total Sales: ₹{prof.total_net_sales_inr:,.0f}")
            lines.append(f"Total Cost: ₹{prof.total_cost_inr:,.0f}")
            lines.append(f"Contribution: ₹{prof.total_contribution_inr:,.0f}")
            lines.append(f"Profit Margin: {prof.overall_profit_margin_pct:.1f}%")
            lines.append(f"Product Health: {prof.products_healthy} healthy, ")
            lines.append(f"  {prof.products_at_risk} at-risk, {prof.products_unprofitable} unprofitable")
            lines.append("")

        if report.quality_section:
            lines.append("=== QUALITY ===")
            qual = report.quality_section
            lines.append(f"Return Rate: {qual.overall_return_rate_pct:.1f}%")
            lines.append(f"Cancellation Rate: {qual.overall_cancellation_rate_pct:.1f}%")
            lines.append("")

        if report.insights:
            lines.append("=== INSIGHTS ===")
            for insight in report.insights[:5]:
                lines.append(f"{insight.title} ({insight.priority}): {insight.description}")
            lines.append("")

        if report.recommendations:
            lines.append("=== RECOMMENDATIONS ===")
            for rec in report.recommendations[:5]:
                lines.append(f"{rec.action} - {rec.owner}")
            lines.append("")

        lines.append("Provide executive narratives for this report.")

        return "\n".join(lines)

    def _parse_response(self, response_text: str) -> dict:
        """Parse and validate LLM response."""
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")

        json_str = json_match.group(0)
        data = json.loads(json_str)

        return {
            "executive_summary": data.get("executive_summary", ""),
            "executive_narrative": data.get("executive_narrative", ""),
            "product_insights": data.get("product_insights", ""),
            "advertising_insights": data.get("advertising_insights", ""),
            "profitability_insights": data.get("profitability_insights", ""),
            "key_risks": data.get("key_risks", ""),
            "key_opportunities": data.get("key_opportunities", ""),
        }

    def _repair_json(self, response_text: str) -> str:
        """Attempt to repair malformed JSON."""
        response_text = re.sub(r",\s*}", "}", response_text)
        response_text = response_text.replace("True", "true")
        response_text = response_text.replace("False", "false")
        response_text = response_text.replace("None", "null")
        return response_text

    def _fallback_result(self) -> dict:
        """Return fallback result when LLM fails."""
        return {
            "executive_summary": "Business analysis available.",
            "executive_narrative": "Review metrics in the detailed sections.",
            "product_insights": "See product performance section.",
            "advertising_insights": "See advertising section.",
            "profitability_insights": "See profitability analysis.",
            "key_risks": "Review critical insights section.",
            "key_opportunities": "Review opportunities section.",
        }
