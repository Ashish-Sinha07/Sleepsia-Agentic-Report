# Sleepsia Agent Architecture

## Phase 1: Data Validation Agent ✅

**Status**: Complete  
**Location**: `agents/validation_agent.py`

The Validation Agent performs deterministic, schema-based quality checks on source data before ingestion.

### DataValidationAgent

Implements the following checks:
- Required columns validation
- Null/missing value detection
- Data type validation (numeric, date)
- Duplicate key detection
- Domain/enumeration validation
- Non-negative value constraints
- Reference value validation
- Reconciliation tolerance checking

### ValidationResult

Returns structured output:
- `status`: PASS | PASS_WITH_WARNINGS | FAIL
- `errors`: Hard failures that reject records
- `warnings`: Soft failures that don't reject records
- `records_processed`: Total records validated
- `records_rejected`: Records that failed validation

### Example Usage

```python
from agents.validation_agent import DataValidationAgent, DatasetSpec
import pandas as pd

agent = DataValidationAgent()

spec = DatasetSpec(
    required_columns=("SKU", "ProductName", "Price"),
    non_nullable_columns=("SKU", "Price"),
    numeric_columns=("Price",),
    non_negative_columns=("Price",),
    unique_columns=("SKU",),
)

df = pd.read_csv("products.csv")
result = agent.validate(df, spec)

if result.status == "FAIL":
    print(f"Validation failed: {result.errors}")
```

---

## Phase 2: Business Metric Engine & Analysis Agents ✅

**Status**: Complete  
**Location**: `analytics/metrics_engine.py`, `agents/analysis_agent.py`, `agents/llm_analysis_agent.py`

---

### MetricsEngine

**Role**: Deterministic calculation of all business metrics.  
**Critical Constraint**: Never invents or infers values. All calculations are deterministic.

#### Supported Metrics

**Revenue Metrics**:
- Net Sales
- Gross Sales
- Discounts
- Organic Sales (Total Sales - Ad-Attributed Sales)
- Ad-Attributed Sales

**Advertising Metrics**:
- ROAS (Return on Ad Spend) = Ad-Attributed Sales / Ad Spend
- ACOS (Advertising Cost of Sale) = (Ad Spend / Ad-Attributed Sales) * 100
- Impressions, Clicks, CTR
- Attributed Units & Orders

**Cost Metrics**:
- Product Cost
- Platform Fees
- Shipping Cost
- Payment Fees
- Other Variable Costs
- Total Cost

**Profitability Metrics**:
- Contribution = Net Sales - All Costs - Refunds
- Profit Margin % = (Contribution / Net Sales) * 100
- Profitability Status = "Healthy" (≥15%) | "At Risk" (0-14.99%) | "Unprofitable" (<0%)

**Quality Metrics**:
- Return Rate % = (Units Returned / Units Sold) * 100
- Cancellation Rate % = (Units Cancelled / Units Sold) * 100
- Refund Amount

**Trend Analysis**:
- Average daily value
- Min/Max daily values
- 7-day and 30-day moving averages
- Trend direction (upward, downward, stable)
- Trend strength (%)

#### Calculation Levels

The engine supports metrics at four levels of aggregation:

1. **Product Level** (`calculate_product_metrics`)
   - Single SKU × Platform × Date
   - Input: raw transaction data
   - Output: `ProductMetrics` dataclass

2. **Platform Level** (`calculate_platform_metrics`)
   - Aggregates multiple products
   - Input: list of `ProductMetrics`
   - Output: `PlatformMetrics` dataclass

3. **Daily Level** (`calculate_daily_metrics`)
   - Entire business for a single day
   - Input: DataFrame with daily transactions
   - Output: `DailyMetrics` dataclass

4. **Trend Level** (`calculate_trend`)
   - Metric performance over time period
   - Input: list of (date, value) tuples
   - Output: `TrendMetrics` dataclass

#### Example Usage

```python
from analytics.metrics_engine import MetricsEngine

engine = MetricsEngine()

# Calculate product metrics
metrics = engine.calculate_product_metrics(
    sku="SLP-1001",
    product_name="Contour Pillow",
    units_sold=100,
    gross_sales=10000,
    net_sales=9500,
    discount=500,
    ad_spend=1000,
    ad_attributed_units=60,
    ad_attributed_sales=5700,
    product_cost=3000,
    platform_fee=1000,
    shipping_cost=500,
    payment_fee=250,
    other_cost=50,
    units_returned=5,
    refund_amount=500,
    units_cancelled=2,
)

print(f"Profit Margin: {metrics.profit_margin_pct:.2f}%")
print(f"Status: {metrics.profitability_status}")
print(f"ROAS: {metrics.roas:.2f}x")
```

---

### DataAnalysisAgent

**Role**: Analyze validated metrics and generate business insights.  
**Critical Constraint**: Never calculates financial values. Receives only pre-calculated metrics.

#### Analysis Functions

##### 1. Product Performance Analysis
```python
agent.analyze_product_performance(metrics, benchmark=None)
```

Detects:
- Unprofitable products (negative margins)
- High return rates (>15%)
- High cancellation rates (>10%)
- Poor ROAS (<2.0x)
- High ACOS (>50%)
- High organic sales opportunity (>70% organic)

Returns: `list[PerformanceFinding]` with severity levels

##### 2. Platform Performance Analysis
```python
agent.analyze_platform_performance(platform_metrics)
```

Detects:
- Platform-wide profitability issues
- Platform-wide return rate anomalies
- Advertising efficiency issues
- Product mix problems

##### 3. Trend Analysis
```python
agent.analyze_daily_trend(trend_metrics, lookback_days=7)
```

Detects:
- Upward/downward trends with strength
- High volatility in metrics
- Seasonal patterns

##### 4. Anomaly Detection
```python
agent.detect_anomalies(metrics_list)
```

Uses statistical methods to identify:
- Profit margin outliers (>2 std deviations from mean)
- Return rate anomalies
- Advertising efficiency outliers

##### 5. Result Synthesis
```python
result = agent.generate_analysis_result(
    period_start=date(2026, 8, 1),
    period_end=date(2026, 8, 31),
    analysis_type="product_performance",
    findings=findings,
    anomalies=anomalies,
    key_metrics={"units_sold": 100, "net_sales": 9500},
)
```

Returns: `AnalysisResult` with:
- Executive summary
- Risk list (sorted by severity)
- Opportunities list
- Recommended actions
- Confidence level
- Data completeness %

#### Example Usage

```python
from agents.analysis_agent import DataAnalysisAgent
from analytics.metrics_engine import MetricsEngine

agent = DataAnalysisAgent()
engine = MetricsEngine()

# Calculate metrics
product_metrics = engine.calculate_product_metrics(...)

# Analyze
findings = agent.analyze_product_performance(product_metrics)

# Identify critical issues
critical = [f for f in findings if f.severity == "critical"]

for finding in critical:
    print(f"⚠️  {finding.description}")
    print(f"   → {finding.recommendation}")
```

---

### LLMAnalysisAgent (Claude-Powered)

**Location**: `agents/llm_analysis_agent.py`
**Model**: Claude (configurable, defaults to Opus)  
**Role**: Generate business insights from pre-calculated metrics

#### System Prompt

The agent uses a carefully crafted system prompt that:

1. **Constrains the LLM**: "NEVER calculate financial metrics"
2. **Enforces evidence**: All claims must use only supplied data
3. **Clarifies causation**: "Distinguish correlation from confirmed causation"
4. **Defines output format**: Structured JSON schema
5. **Sets priorities**: Focus on material business impact
6. **Specifies severity levels**: Critical → High → Medium → Low

#### AnalysisInput Model

Provides complete context to the LLM:

```python
analysis_input = AnalysisInput(
    analysis_date=date(2026, 8, 21),
    analysis_type="product",  # product | platform | daily | portfolio
    
    product_metrics=ProductMetrics(...),
    
    current_day_comparisons=[
        MetricComparison("profit_margin", 38.42, 35.0),
        MetricComparison("units_sold", 100, 95),
    ],
    week_comparisons=[...],
    month_comparisons=[...],
    
    trend_metrics=TrendMetrics(...),
    
    detected_anomalies=["Return rate elevated"],
    rule_based_findings=[...],
    
    context_notes="Summer season - expect higher demand",
)

# Agent converts to natural language context for LLM
context = analysis_input.to_prompt_context()
```

#### Safe JSON Integration

The agent implements **three-layer safety** for LLM output:

**Layer 1: JSON Parsing**
- Extracts JSON from Claude's response
- Handles text before/after JSON gracefully
- Uses regex to locate structure

**Layer 2: JSON Repair**
- Automatically fixes common malformations:
  - Trailing commas: `{...,"key":value,}` → `{...,"key":value}`
  - Python booleans: `True` → `true`, `None` → `null`
  - Missing closing braces/brackets

**Layer 3: Fallback Result**
- If all repairs fail, returns safe default
- Low confidence, zero completeness
- Flags issue: "Analysis could not be completed"
- Preserves detected anomalies from rule-based analysis

#### Retry Logic

```python
for attempt in range(3):
    try:
        response = claude.messages.create(...)
        result = parse_response(response)
        return result
    except (JSONDecodeError, ValueError):
        if attempt < 2:
            try:
                repaired = repair_json(response)
                result = parse_response(repaired)
                return result
            except:
                continue
        else:
            return fallback_result()
```

#### Usage Example

```python
from agents.llm_analysis_agent import LLMAnalysisAgent
from analytics.analysis_input import AnalysisInput

agent = LLMAnalysisAgent(api_key="sk-...")

result = agent.analyze(analysis_input)

print(f"Summary: {result.summary}")
print(f"Confidence: {result.confidence}")
print(f"Completeness: {result.data_completeness * 100}%")

for finding in result.performance_findings:
    if finding.severity == "critical":
        print(f"🚨 {finding.description}")
        print(f"   → {finding.recommendation}")

print(f"\nRecommended Actions:")
for action in result.recommended_actions:
    print(f"  • {action}")
```

#### Example Output

```json
{
  "period_start": "2026-08-21",
  "period_end": "2026-08-21",
  "analysis_type": "product",
  "summary": "SLP-1001 shows strong profitability with healthy margins, but return rate warrants investigation.",
  "key_metrics": {
    "profit_margin_pct": 38.42,
    "roas": 5.7,
    "return_rate_pct": 5.0
  },
  "performance_findings": [
    {
      "finding_type": "profitability",
      "severity": "low",
      "sku": "SLP-1001",
      "metric_name": "profit_margin",
      "metric_value": 38.42,
      "threshold": 15.0,
      "description": "Healthy profit margin of 38.42%, well above 15% threshold",
      "recommendation": "Maintain current pricing and ad spend strategy"
    },
    {
      "finding_type": "quality",
      "severity": "medium",
      "sku": "SLP-1001",
      "metric_name": "return_rate",
      "metric_value": 5.0,
      "threshold": 15.0,
      "description": "Return rate is elevated at 5.0% (5 units returned from 100 sold)",
      "recommendation": "Investigate product quality or fit issues through customer feedback"
    }
  ],
  "anomalies_detected": [],
  "risks_identified": ["Return rate elevated - may indicate quality issue"],
  "opportunities": ["Organic sales strong (40% of mix) - consider reducing ad spend"],
  "recommended_actions": [
    "Monitor return rate trend over next 7 days",
    "Review customer feedback for quality concerns",
    "Consider A/B testing different product descriptions"
  ],
  "confidence": "high",
  "data_completeness": 1.0
}
```

---

## What LLMs Can Do ✅

With validated metrics from these agents, an LLM can:

- **Summarize performance** in plain English
- **Highlight significant changes** (e.g., "ROAS improved 15% week-over-week")
- **Explain likely drivers** (e.g., "Higher returns may be due to seasonal demand spike")
- **Prioritize risks** by business impact
- **Identify important anomalies** (e.g., "SLP-1001 margin deviated significantly")
- **Produce management summaries** suitable for executives
- **Answer follow-up questions** about trends and patterns

---

## What LLMs CANNOT Do ❌

LLMs must NEVER:

- ❌ Calculate financial values (ROAS, margins, contribution, etc.)
- ❌ Change or override source data values
- ❌ Invent missing data ("assume this was $X")
- ❌ Make unsupported causal claims ("returns increased because of...")
- ❌ Override validation results
- ❌ Create metrics from raw data without deterministic calculation

If evidence is insufficient, the LLM must say: **"Insufficient evidence."**

---

## Data Flow

```
Source Data (Excel, CSV, Database)
    ↓
Validation Agent (Phase 1)
    ├─ Check schema
    ├─ Check domains
    ├─ Check reconciliation
    └─ Reject invalid records
    ↓
MySQL Database
    ↓
Metrics Engine (Phase 2)
    ├─ Calculate deterministic metrics
    ├─ Aggregate by product/platform/date
    └─ Produce TrendMetrics
    ↓
Analysis Agent (Phase 2)
    ├─ Analyze for patterns
    ├─ Detect anomalies
    └─ Prioritize findings
    ↓
FastAPI
    ↓
React Dashboard / LLM Chat
    └─ Summarize, explain, recommend
```

---

## Test Coverage

### Validation Tests (2 tests)
- Multiple validation failures
- Reconciliation warnings

### Metrics Engine Tests (20 tests)
- All metric calculations (ROAS, ACOS, margins, etc.)
- Product, platform, daily aggregations
- Trend analysis
- Edge cases (zero values, high profitability)

### Rule-Based Analysis Agent Tests (10 tests)
- Product performance analysis
- Platform analysis
- Trend detection (upward, downward, volatile)
- Anomaly detection
- Result synthesis

### LLM Analysis Agent Tests (12 tests)
- JSON parsing and extraction
- Malformed JSON repair
- Python bool/None to JSON conversion
- Integration with mocked Claude
- Product and platform analysis
- Fallback error handling
- Prompt building with context
- Safety constraint verification

**Total**: 44 tests, all passing ✅

---

## Testing

Run the complete test suite:

```bash
python -m pytest tests/ -v
```

Run specific test file:

```bash
python -m pytest tests/test_metrics_engine.py -v
```

Run specific test:

```bash
python -m pytest tests/test_metrics_engine.py::TestMetricsEngineCalculations::test_roas_calculation -v
```

---

## Architecture Rules

1. **Validation is mandatory**: All data must pass validation before metrics are calculated.
2. **Metrics are deterministic**: Same input always produces same output. No randomness.
3. **LLM receives validated metrics**: Agent has no access to raw data or validation logic.
4. **One-way flow**: Metrics flow from Validation → Engine → Agent → LLM. Never reverse.
5. **Errors are explicit**: If calculation cannot be done, return 0 or "Insufficient Evidence", never fabricate.

---

## Phase 3: Insight & Recommendation Agent ✅

**Status**: Complete  
**Location**: `analytics/business_rules.py`, `analytics/insight_models.py`, `analytics/priority_engine.py`, `analytics/insight_engine.py`, `analytics/recommendation_engine.py`, `analytics/summary_generator.py`, `agents/insight_recommendation_agent.py`

The Insight & Recommendation Agent converts analyzed metrics into management-ready insights and evidence-based recommendations.

### Core Components

#### 1. BusinessRules Configuration

Configurable thresholds for alerts and recommendations:

```python
from analytics.business_rules import BusinessRules

rules = BusinessRules(
    minimum_roas=2.0,
    maximum_acos_pct=50.0,
    minimum_profit_margin_pct=15.0,
    maximum_return_rate_pct=15.0,
    maximum_cancellation_rate_pct=10.0,
)

# Evaluate a metric
passes, threshold = rules.evaluate_roas(3.5)

# Platform-specific overrides
amazon_rules = BusinessRules(minimum_roas=1.8)
rules.platform_overrides["amazon"] = amazon_rules
```

#### 2. Priority Engine

Deterministic priority assignment based on business rules:

```python
from analytics.priority_engine import PriorityEngine

engine = PriorityEngine(rules)

priority = engine.determine_profitability_priority(
    margin_pct=-5.0,  # Returns Priority.CRITICAL
)

priority = engine.determine_trend_priority(
    trend_direction="downward",
    trend_strength=0.35,  # Returns Priority.CRITICAL
)
```

Priority Levels:
- **CRITICAL**: Immediate action required (unprofitable, quality crisis, revenue collapse)
- **HIGH**: Significant concern (poor ROAS, high returns/cancellations)
- **MEDIUM**: Monitor closely (volatility, minor inefficiencies)
- **LOW**: Positive trends (margin improvement, growth)
- **INFO**: Informational (reference points, strong performance)

#### 3. Insight Engine

Generates structured business insights from analysis results:

```python
from analytics.insight_engine import InsightEngine

engine = InsightEngine(rules)

insights = engine.generate_insights_from_analysis(
    analysis_result=analysis_result,
    product_metrics=metrics,
)

# Insights contain:
# - insight_id (unique identifier)
# - category (SALES, ADVERTISING, PROFITABILITY, etc.)
# - priority (deterministic, rule-based)
# - title, description
# - evidence (supporting data points)
# - confidence_pct
# - business_impact (estimated financial impact)
```

Insight Categories:
- SALES
- ADVERTISING
- PROFITABILITY
- RETURNS
- CANCELLATIONS
- PLATFORM
- PRODUCT
- TREND
- ANOMALY

#### 4. Recommendation Engine

Generates evidence-based recommendations from insights:

```python
from analytics.recommendation_engine import RecommendationEngine

engine = RecommendationEngine(rules)

recommendations = engine.generate_recommendations(insights)

# Recommendations contain:
# - recommendation_id
# - action (specific, actionable)
# - rationale (evidence-based)
# - expected_impact
# - owner (who should execute)
# - priority
# - timeline
# - estimated_financial_impact_inr
# - evidence (traceability to insights)
```

#### 5. Management Summary Generator

Creates executive-level summaries:

```python
from analytics.summary_generator import ManagementSummaryGenerator

summary = ManagementSummaryGenerator.generate_summary(
    period_start=date(2026, 8, 1),
    period_end=date(2026, 8, 31),
    insights=insights,
    recommendations=recommendations,
)

# Summary contains:
# - executive_summary (2-3 sentences)
# - critical_issues (list)
# - high_priority_items (list)
# - key_opportunities (list)
# - top_recommendations (list)
# - overall_health_score (0-100)
# - data_completeness_pct
```

#### 6. Insight & Recommendation Agent (Orchestrator)

Coordinates all components:

```python
from agents.insight_recommendation_agent import InsightRecommendationAgent

agent = InsightRecommendationAgent(business_rules=rules)

result = agent.analyze(
    analysis_result=analysis_result,
    product_metrics=metrics,
    data_completeness=0.95,
)

# Result contains:
# - insights (list[BusinessInsight])
# - recommendations (list[Recommendation])
# - management_summary (ManagementSummary)
# - overall_confidence ("high" | "medium" | "low")
# - data_completeness (0.0-1.0)
# - issues_count
# - opportunities_count

# Export for LLM refinement
export_dict = agent.export_for_llm_refinement(result)
```

### Architecture Constraints

1. **Never recalculates metrics**: Receives pre-calculated metrics only
2. **Deterministic priorities**: All priorities come from BusinessRules, not LLM judgment
3. **Evidence-based**: Every insight and recommendation has supporting evidence
4. **Traceable**: Recommendations link back to specific insights
5. **No invented data**: Clearly states when evidence is insufficient
6. **Structured output**: All results are validated with Pydantic models

### Example Usage

```python
from agents.insight_recommendation_agent import InsightRecommendationAgent
from analytics.business_rules import BusinessRules
from agents.analysis_agent import DataAnalysisAgent
from analytics.metrics_engine import MetricsEngine

# Initialize components
rules = BusinessRules()
agent = InsightRecommendationAgent(rules)
metrics_engine = MetricsEngine()
analysis_agent = DataAnalysisAgent()

# Calculate metrics
product_metrics = metrics_engine.calculate_product_metrics(...)

# Analyze
findings = analysis_agent.analyze_product_performance(product_metrics)
analysis_result = analysis_agent.generate_analysis_result(
    period_start=date(2026, 8, 1),
    period_end=date(2026, 8, 31),
    analysis_type="product",
    findings=findings,
    anomalies=[],
    key_metrics={...},
)

# Generate insights and recommendations
result = agent.analyze(
    analysis_result=analysis_result,
    product_metrics=product_metrics,
)

# Print management summary
print(result.management_summary.executive_summary)

# Iterate through critical insights
for insight in result.critical_insights():
    print(f"⚠️  {insight.title}: {insight.description}")
    for rec in result.recommendations:
        if insight.insight_id in rec.insight_sources:
            print(f"   → Action: {rec.action}")
```

### Output Models

#### BusinessInsight
- `insight_id`: Unique identifier
- `category`: InsightCategory (enum)
- `priority`: Priority level (deterministic)
- `title`: Short description
- `description`: Detailed explanation
- `metric_name`: Which metric (optional)
- `metric_value`: Current value (optional)
- `threshold`: Business rule threshold (optional)
- `sku`, `product_name`, `platform_id`, `platform_name`: Dimensions
- `evidence`: List of supporting facts
- `finding_sources`: Links to source findings
- `confidence_pct`: 0-100
- `business_impact`: Financial impact statement

#### Recommendation
- `recommendation_id`: Unique identifier
- `action`: Specific, actionable step
- `rationale`: Why it matters
- `expected_impact`: Predicted outcome
- `owner`: Who executes
- `priority`: Priority level (from insight)
- `evidence`: Supporting data points
- `insight_sources`: Links to source insights
- `timeline`: Expected execution timeframe
- `estimated_financial_impact_inr`: Potential benefit
- `risk_level`: "low" | "medium" | "high"

#### ManagementSummary
- `executive_summary`: Concise overview
- `critical_issues`: List of critical problems
- `high_priority_items`: List of high-priority concerns
- `key_opportunities`: List of opportunities
- `top_recommendations`: Prioritized action items
- `overall_health_score`: 0-100 composite score
- `data_completeness_pct`: Data availability percentage

---

## Test Coverage

### Phase 3 Tests (35 tests)
- **BusinessRules**: 7 tests (threshold evaluation, overrides)
- **PriorityEngine**: 13 tests (all priority scenarios)
- **InsightEngine**: 3 tests (generation, evidence, confidence)
- **RecommendationEngine**: 3 tests (generation, priority mapping, evidence)
- **ManagementSummaryGenerator**: 3 tests (summary generation, health score, formatting)
- **InsightRecommendationAgent**: 3 tests (full pipeline, structure, export)
- **Error Handling**: 3 tests (empty findings, low completeness, evidence chain)

**Total Test Coverage**: 79 tests (44 existing + 35 new), all passing ✅

---

## Architecture Rules (Phase 3)

1. **Deterministic everything**: No probabilistic thresholds, no "maybe" in priorities
2. **Threshold-based decisions**: All rules come from BusinessRules, not heuristics
3. **Evidence chains**: Every recommendation traces back to specific insights/findings
4. **Never override metrics**: Accept pre-calculated values as ground truth
5. **Structured output**: All results validated by Pydantic
6. **Transparent confidence**: Report confidence, completeness, and data quality

---

## Phase 4: Report Generation ✅

**Status**: Complete  
**Location**: `analytics/report_models.py`, `analytics/report_builder.py`, `analytics/html_renderer.py`, `analytics/excel_renderer.py`, `analytics/pdf_renderer.py`, `agents/report_agent.py`

Converts structured business metrics, analysis results, and insights into management-ready reports in multiple formats.

### Core Components

#### 1. Report Models (Canonical Report)

Complete, deterministic report structure:

```python
from analytics.report_models import Report, ReportType

report = Report(
    report_id="RPT-ABC123",
    report_date=date(2026, 8, 21),
    report_type=ReportType.PRODUCT_DAILY,
    title="Product Daily Report",
    executive_summary="...",
    overall_metrics=OverallMetrics(...),
    product_sections=[ProductSection(...)],
    platform_sections=[PlatformSection(...)],
    advertising_section=AdvertisingSection(...),
    profitability_section=ProfitabilitySection(...),
    quality_section=QualitySection(...),
    insights=[Insight(...)],
    recommendations=[Recommendation(...)],
)
```

Report contains:
- **report_id**: Unique identifier
- **report_date**: Date of analysis
- **report_type**: PRODUCT_DAILY | PLATFORM_DAILY | PRODUCT_PLATFORM_DAILY | MANAGEMENT_DAILY_SUMMARY
- **title**: Report title
- **executive_summary**: 2-3 sentence overview
- **overall_metrics**: Aggregate KPIs
- **product_sections**: Product-level details
- **platform_sections**: Platform-level details
- **advertising_section**: Advertising performance
- **profitability_section**: Profitability analysis
- **quality_section**: Returns/cancellations
- **insights**: Key business insights
- **recommendations**: Actionable recommendations

#### 2. Report Builder

Deterministically constructs Report objects from metrics:

```python
from analytics.report_builder import ReportBuilder

# Build product report
report = ReportBuilder.build_product_report(
    report_date=date(2026, 8, 21),
    sku="SLP-1001",
    product_name="Contour Pillow",
    product_metrics=metrics,
    insight_result=insights,
)

# Build platform report
report = ReportBuilder.build_platform_report(
    report_date=date(2026, 8, 21),
    platform_metrics=platform_metrics,
    product_metrics_list=[...],
    insight_result=insights,
)
```

Key features:
- No metric recalculation
- Automatic section population
- Evidence-based insights integration
- Consistent aggregations

#### 3. HTML Renderer

Professional HTML report generation:

```python
from analytics.html_renderer import HTMLRenderer

html = HTMLRenderer.render(report)
# Returns: Complete HTML document with styles
```

Features:
- Responsive design
- Print-friendly CSS
- Professional styling
- All sections formatted
- Mobile-compatible

#### 4. Excel Renderer

Multi-sheet Excel workbook generation:

```python
from analytics.excel_renderer import ExcelRenderer

excel_bytes = ExcelRenderer.render(report)
# Returns: Binary Excel file (openpyxl required)
```

Sheets created:
- Summary (overview, timestamps)
- Products (product details)
- Platforms (platform details)
- Advertising (ad performance)
- Profitability (margin analysis)
- Quality (returns/cancellations)
- Insights (key insights)
- Recommendations (action items)
- Metrics (overall KPIs)

#### 5. PDF Renderer

Professional PDF report generation:

```python
from analytics.pdf_renderer import PDFRenderer

pdf_bytes = PDFRenderer.render(report)
# Returns: Binary PDF file (reportlab required)
```

Features:
- Professional formatting
- Executive-ready appearance
- All sections included
- Table of contents
- Proper pagination

#### 6. Report Agent

LLM-powered narrative refinement (narrative only, never metrics):

```python
from agents.report_agent import ReportAgent

agent = ReportAgent()

narratives = agent.refine_report_narrative(report)
# Returns: {
#   "executive_summary": "...",
#   "executive_narrative": "...",
#   "product_insights": "...",
#   "advertising_insights": "...",
#   "profitability_insights": "...",
#   "key_risks": "...",
#   "key_opportunities": "..."
# }
```

LLM is used ONLY for:
- Narrative summaries
- Insight explanations
- Business impact descriptions
- Recommendations rationale

LLM NEVER:
- Calculates financial metrics
- Modifies metric values
- Invents trends
- Creates false data

### Complete Example

```python
from analytics.report_builder import ReportBuilder
from analytics.html_renderer import HTMLRenderer
from analytics.excel_renderer import ExcelRenderer
from agents.report_agent import ReportAgent

# Build report from metrics and insights
report = ReportBuilder.build_product_report(
    report_date=date(2026, 8, 21),
    sku="SLP-1001",
    product_name="Contour Pillow",
    product_metrics=metrics,
    insight_result=insights,
)

# Optionally refine narratives with LLM
agent = ReportAgent()
narratives = agent.refine_report_narrative(report)

# Render to multiple formats
html = HTMLRenderer.render(report)
excel_bytes = ExcelRenderer.render(report)

# Save
with open("report.html", "w") as f:
    f.write(html)

with open("report.xlsx", "wb") as f:
    f.write(excel_bytes)
```

### Supported Report Types

1. **PRODUCT_PLATFORM_DAILY**: Single product on single platform
2. **PRODUCT_DAILY**: Single product across platforms
3. **PLATFORM_DAILY**: Single platform with all products
4. **MANAGEMENT_DAILY_SUMMARY**: Multi-platform, multi-product overview

### Architecture Constraints (Phase 4)

1. **Report is source of truth**: All values come from pre-calculated metrics
2. **Never recalculate**: Use metric values exactly as provided
3. **LLM for narrative only**: Never for calculations or data creation
4. **Deterministic structure**: Same input produces same output
5. **Traceable metrics**: Every KPI links to its source
6. **Safe rendering**: Missing data handled gracefully
7. **Validation**: Report objects validated by Pydantic

---

## Test Coverage

### Phase 4 Tests (16 tests, 2 skipped)
- **ReportModels**: 3 tests (model creation, structure)
- **ReportBuilder**: 4 tests (building, aggregations, unprofitable)
- **HTMLRenderer**: 2 tests (rendering, content)
- **ExcelRenderer**: 2 tests (available, rendering)
- **PDFRenderer**: 2 tests (skipped - requires reportlab)
- **ReportAgent**: 2 tests (fallback, structure)
- **ErrorHandling**: 3 tests (empty data, metric preservation)

**Total Test Coverage**: 95 tests (79 existing + 16 new), all passing ✅

---

---

## Phase 7: Workflow Orchestration Engine ✅

**Status**: Complete  
**Location**: `analytics/orchestration/`

A deterministic workflow orchestrator that executes the complete reporting pipeline with dependency management, retries, checkpointing, resumability, and idempotency.

### Key Components

#### 1. WorkflowDefinition

Declarative pipeline configuration:
- Ordered stages (INGESTION → VALIDATION → METRICS → ANALYSIS → INSIGHTS → REPORT → DISTRIBUTION → AUDIT)
- Required vs optional sources
- Retry policy with exponential backoff
- Checkpoint and idempotency settings

#### 2. WorkflowOrchestrator

Main execution controller:
- Executes stages in sequence
- Manages dependencies and retries
- Handles required vs optional source failures
- Caches results for idempotency
- Creates and tracks run state

#### 3. RunManager

Persistence and recovery:
- Creates and tracks workflow runs
- Persists state to checkpoints (JSON files)
- Supports resumability from last successful stage
- Tracks failed and partial sources
- Records stage results and timing

#### 4. Service Interfaces

Loose coupling via abstract interfaces:
- `IngestionService` - Load data
- `ValidationService` - Validate data
- `MetricService` - Calculate metrics
- `AnalysisService` - Analyze metrics
- `InsightService` - Generate insights
- `ReportService` - Generate reports
- `DistributionService` - Distribute reports
- `MonitoringService` - Audit and monitoring

#### 5. IdempotencyKeyManager

Deterministic key generation:
- Same inputs always produce same key
- Stage-specific key generators
- Support for context (platform, product, etc.)
- Prevents duplicate processing

#### 6. IdempotencyCache

In-memory result caching:
- Prevents redundant stage execution
- Cleared on orchestrator reset
- Survives within-session retries

### Workflow Execution Flow

**Successful Run**:
```
PENDING → INGESTION → VALIDATION → METRICS → ANALYSIS → 
INSIGHTS → REPORT → DISTRIBUTION → AUDIT → SUCCESS
```

**Required Source Failure**:
```
PENDING → INGESTION → VALIDATION [FAILED] → FAILED
(Downstream stages don't execute)
```

**Optional Source Failure**:
```
PENDING → ... → DISTRIBUTION [WARNING] → AUDIT → PARTIAL
(Continues with warning, marked as partial)
```

**Resumable Failure**:
```
Run 1: PENDING → INGESTION → VALIDATION → METRICS [FAILED] → FAILED
(Checkpoint saved)

Run 2: Resume from checkpoint
       → METRICS [RETRY] → ANALYSIS → ... → SUCCESS
```

### Retry Logic

Transient failures are automatically retried:
- Configurable max retries (default: 3)
- Exponential backoff (default: 60s × 2^n)
- Permanent failures fail immediately
- Optional stages warn instead of failing

### Key Features

1. **Deterministic**: No LLM-based orchestration, pure logic
2. **Idempotent**: Same inputs produce same output, no duplicates
3. **Recoverable**: Can resume from last successful stage via checkpoint
4. **Loosely Coupled**: All stages implement interfaces, easily testable
5. **Clear Error Handling**: Distinguishes required vs optional failures
6. **Observable**: Full timing, status, and error tracking
7. **Persistent**: Run state saved to disk for recovery

### Example Usage

```python
from analytics.orchestration import WorkflowOrchestrator, WorkflowDefinition
from datetime import date

# Define workflow
definition = WorkflowDefinition(
    workflow_id="daily_report",
    name="Daily Business Report",
)

# Create orchestrator with services
orchestrator = WorkflowOrchestrator(
    workflow_definition=definition,
    ingestion_service=...,
    validation_service=...,
    metric_service=...,
    analysis_service=...,
    insight_service=...,
    report_service=...,
    distribution_service=...,
    monitoring_service=...,
)

# Execute workflow
result = orchestrator.execute(date(2026, 8, 21))

if result.status == RunStatus.SUCCESS:
    print(f"✅ Completed: {result.report_path}")
elif result.status == RunStatus.PARTIAL:
    print(f"⚠️  Partial: {result.partial_sources}")
    print(f"   Report: {result.report_path}")
else:
    print(f"❌ Failed: {result.error_message}")
    # Resume when ready
    result2 = orchestrator.resume(result.run_id)
```

### Test Coverage

**Phase 7 Tests** (33 tests):
- **IdempotencyKeyManager**: 6 tests (deterministic key generation)
- **IdempotencyCache**: 4 tests (caching operations)
- **RunManager**: 8 tests (run lifecycle, checkpoint persistence)
- **WorkflowOrchestrator**: 15 tests (complete pipeline, retries, failures, resumability)

**Total Test Coverage**: 128 tests (95 existing + 33 new), all passing ✅

### Files

- `analytics/orchestration/__init__.py` - Package exports
- `analytics/orchestration/models.py` - Domain models
- `analytics/orchestration/service_interfaces.py` - Abstract service interfaces
- `analytics/orchestration/idempotency.py` - Idempotency management
- `analytics/orchestration/run_manager.py` - Run state persistence
- `analytics/orchestration/workflow_engine.py` - Main orchestrator
- `tests/test_orchestration.py` - Comprehensive test suite
- `ORCHESTRATION.md` - Detailed documentation

---

## Next Steps (Post-Phase 7)

- **Database Integration**: Load validated data into MySQL schema
- **FastAPI Endpoints**: Expose metrics, analysis, and insights via REST API
- **React Dashboard**: Display metrics, alerts, insights, and recommendations
- **LLM Chat Interface**: Claude-powered business assistant with controlled tools
- **Scheduled Execution**: Run workflows on schedule via APScheduler
- **Alerts**: Real-time notifications for critical insights
- **Distributed Execution**: Scale to multiple machines (future enhancement)
