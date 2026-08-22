"""Claude-powered Analysis Agent - LLM-driven business insights from pre-calculated metrics."""

import json
import re
from typing import Optional
from datetime import date
import anthropic
from pydantic import BaseModel, ValidationError

from analytics.models import AnalysisResult, PerformanceFinding
from analytics.analysis_input import AnalysisInput


class LLMAnalysisAgent:
    """
    Claude-powered business analysis agent.

    CRITICAL CONSTRAINTS:
    1. Never calculates financial metrics (receives them pre-calculated)
    2. Uses only supplied evidence for claims
    3. Distinguishes correlation from causation
    4. Returns structured JSON validated by Pydantic
    5. Safe retry/repair on malformed JSON
    6. Never overrides deterministic metrics
    """

    SYSTEM_PROMPT = """You are a senior business analyst for Sleepsia, a direct-to-consumer sleep product company.

Your role is to analyze pre-calculated business metrics and identify:
1. The most important performance changes
2. Key business drivers (using only supplied evidence)
3. Profitability concerns and risks
4. Cross-platform comparisons (where applicable)
5. Statistical anomalies
6. Actionable recommendations

CRITICAL RULES:
- NEVER calculate or invent financial metrics (margins, ROAS, contribution, etc.)
- ALL metrics are pre-calculated and validated
- NEVER claim causation without evidence (use "likely", "may be due to", "correlates with")
- ONLY use data provided in the input context
- If evidence is insufficient, say "Insufficient evidence to determine"
- Return ONLY valid JSON matching the specified schema
- Flag logical inconsistencies but never override the numbers

ANALYSIS FRAMEWORK:
1. Identify changes: Compare current vs. previous periods (day, week, month)
2. Prioritize: Rank findings by business impact (profitability, volume, quality)
3. Explain: Use metrics and trends to explain what happened
4. Recommend: Suggest actions based on evidence
5. Assess: Rate confidence based on data completeness

SEVERITY LEVELS:
- "critical": Immediate action required (negative margins, major quality issues, revenue collapse)
- "high": Significant concern (poor ROAS, high returns, platform underperformance)
- "medium": Monitor closely (volatility, minor inefficiencies)
- "low": Positive findings (organic growth, margin improvement)

CONFIDENCE LEVELS:
- "high": Multiple data points confirm finding, clear pattern visible
- "medium": Evidence exists but pattern is emerging, some uncertainty
- "low": Limited evidence, preliminary findings only

OUTPUT: Return ONLY a valid JSON object matching this schema:
{
  "period_start": "YYYY-MM-DD",
  "period_end": "YYYY-MM-DD",
  "analysis_type": "product|platform|daily|portfolio",
  "summary": "2-3 sentence executive summary",
  "key_metrics": {
    "metric_name": numeric_value
  },
  "performance_findings": [
    {
      "finding_type": "profitability|quality|advertising|trend|anomaly|comparison",
      "severity": "critical|high|medium|low",
      "sku": "SKU or null",
      "platform_id": "platform or null",
      "metric_name": "metric being analyzed",
      "metric_value": numeric_value,
      "threshold": numeric_or_null,
      "description": "what happened - be specific and data-driven",
      "recommendation": "what to do - actionable and evidence-based"
    }
  ],
  "anomalies_detected": ["specific anomalies found"],
  "risks_identified": ["list of business risks"],
  "opportunities": ["list of opportunities"],
  "recommended_actions": ["prioritized list of actions"],
  "confidence": "high|medium|low",
  "data_completeness": 0.0_to_1.0
}

Be concise. Insights should be 1-2 sentences each. Focus on material business impact."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-opus-5"):
        """Initialize with Claude API credentials."""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_retries = 3

    def analyze(self, analysis_input: AnalysisInput) -> AnalysisResult:
        """
        Analyze metrics using Claude and return structured result.

        Args:
            analysis_input: AnalysisInput with all pre-calculated metrics

        Returns:
            AnalysisResult with findings, recommendations, risks
        """
        prompt = self._build_prompt(analysis_input)

        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    system=self.SYSTEM_PROMPT,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )

                response_text = response.content[0].text

                result = self._parse_response(response_text, analysis_input)

                return result

            except (json.JSONDecodeError, ValidationError, ValueError) as e:
                if attempt < self.max_retries - 1:
                    try:
                        response_text = self._repair_json(response_text)
                        result = self._parse_response(response_text, analysis_input)
                        return result
                    except Exception:
                        continue
                else:
                    return self._fallback_result(analysis_input, str(e))

        return self._fallback_result(analysis_input, "Max retries exceeded")

    def _build_prompt(self, analysis_input: AnalysisInput) -> str:
        """Build the user prompt with context."""
        context = analysis_input.to_prompt_context()

        return f"""Analyze the following business metrics for Sleepsia:

{context}

Date: {analysis_input.analysis_date}
Analysis Type: {analysis_input.analysis_type}

Provide a comprehensive analysis as JSON. Focus on:
1. Most important changes from previous periods
2. Profitability concerns
3. Advertising efficiency
4. Quality metrics (returns, cancellations)
5. Trends and anomalies
6. Actionable recommendations

Remember: Use ONLY the data provided. Never invent metrics. Distinguish correlation from causation."""

    def _parse_response(self, response_text: str, analysis_input: AnalysisInput) -> AnalysisResult:
        """Parse and validate Claude's JSON response."""
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")

        json_str = json_match.group(0)
        data = json.loads(json_str)

        findings = []
        for finding_data in data.get("performance_findings", []):
            finding = PerformanceFinding(
                finding_type=finding_data.get("finding_type", ""),
                severity=finding_data.get("severity", "medium"),
                sku=finding_data.get("sku"),
                platform_id=finding_data.get("platform_id"),
                metric_name=finding_data.get("metric_name", ""),
                metric_value=finding_data.get("metric_value", 0.0),
                threshold=finding_data.get("threshold"),
                description=finding_data.get("description", ""),
                recommendation=finding_data.get("recommendation", ""),
            )
            findings.append(finding)

        result = AnalysisResult(
            period_start=analysis_input.analysis_date,
            period_end=analysis_input.analysis_date,
            analysis_type=data.get("analysis_type", analysis_input.analysis_type),
            summary=data.get("summary", "Analysis complete"),
            key_metrics=data.get("key_metrics", {}),
            performance_findings=findings,
            anomalies_detected=data.get("anomalies_detected", []),
            risks_identified=data.get("risks_identified", []),
            opportunities=data.get("opportunities", []),
            recommended_actions=data.get("recommended_actions", []),
            confidence=data.get("confidence", "medium"),
            data_completeness=float(data.get("data_completeness", 1.0)),
        )

        return result

    def _repair_json(self, malformed_json: str) -> str:
        """Attempt to repair malformed JSON."""
        json_match = re.search(r"\{.*\}", malformed_json, re.DOTALL)
        if not json_match:
            raise ValueError("Cannot repair: no JSON structure found")

        json_str = json_match.group(0)

        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        json_str = re.sub(r':\s*None(?=[,\}])', ': null', json_str)
        json_str = re.sub(r':\s*True(?=[,\}])', ': true', json_str)
        json_str = re.sub(r':\s*False(?=[,\}])', ': false', json_str)

        return json_str

    def _fallback_result(self, analysis_input: AnalysisInput, error: str) -> AnalysisResult:
        """Return a safe fallback result when JSON parsing fails."""
        return AnalysisResult(
            period_start=analysis_input.analysis_date,
            period_end=analysis_input.analysis_date,
            analysis_type=analysis_input.analysis_type,
            summary=f"Analysis could not be completed: {error}. Review raw metrics manually.",
            key_metrics={},
            performance_findings=[],
            anomalies_detected=analysis_input.detected_anomalies,
            risks_identified=[],
            opportunities=[],
            recommended_actions=["Review analysis failure: consult deterministic metrics directly"],
            confidence="low",
            data_completeness=0.0,
        )
