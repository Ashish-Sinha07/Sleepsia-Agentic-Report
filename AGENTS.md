# Sleepsia Agent Architecture

## Phase 1: Data Validation Agent ✅

**Status**: Complete  
**Location**: `database/validation.py`

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
from database.validation import DataValidationAgent, DatasetSpec
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

## Phase 2: Business Metric Engine & Analysis Agent ✅

**Status**: Complete  
**Location**: `analytics/metrics_engine.py`, `analytics/analysis_agent.py`

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
from analytics.analysis_agent import DataAnalysisAgent
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

### Analysis Agent Tests (10 tests)
- Product performance analysis
- Platform analysis
- Trend detection (upward, downward, volatile)
- Anomaly detection
- Result synthesis

**Total**: 32 tests, all passing ✅

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

## Next Steps (Phase 3)

- **Database Integration**: Load validated data into MySQL schema
- **FastAPI Endpoints**: Expose metrics and analysis results via REST API
- **React Dashboard**: Display metrics, alerts, and analysis results
- **LLM Integration**: Connect chat interface for business questions
- **Report Generation**: PDF/Excel reporting with analysis
- **Automation**: Scheduled metric calculation and report distribution
