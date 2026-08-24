# Agent Integration Guide

This document explains how all agents are integrated into the Sleepsia Agentic Reporting System.

## Architecture Overview

```
React Dashboard (http://localhost:5173)
    ↓
FastAPI Backend (http://localhost:8000)
    ↓
Agent Orchestrator
    ├── Validation Agent (validates source data)
    ├── Metrics Engine (calculates financial metrics)
    ├── Analysis Agent (analyzes metrics)
    ├── Insight Recommendation Agent (generates insights)
    ├── LLM Analysis Agent (NLP & recommendations)
    └── Report Agent (generates reports)
    ↓
MySQL Database
    ↓
Analytics & Reporting
```

## API Endpoints

### KPI Dashboard
- **GET /api/kpis** - Executive dashboard KPIs
  - Filters: start_date, end_date, platform, warehouse
  - Returns: Revenue, Profit, ROAS, ACOS, Return Rate, etc.

### Platform Performance
- **GET /api/platform-performance** - Performance by platform
  - Filters: start_date, end_date
  - Returns: Revenue, profit, profitability by platform

### Product Performance
- **GET /api/product-performance** - Product-wise analysis
  - Filters: start_date, end_date, platform, sort_by
  - Returns: Product metrics, profitability status, alerts
- **GET /api/top-products** - Top performing products
  - Filters: limit, metric
  - Returns: Ranked product list
- **GET /api/bottom-products** - Underperforming products
  - Filters: limit, metric
  - Returns: Products that need attention

### Advertising
- **GET /api/advertising** - Ad spend and ROI
  - Filters: start_date, end_date, platform
  - Returns: ROAS, ACOS, impressions, clicks, CTR
- **GET /api/advertising/roi-analysis** - ROI breakdown
  - Returns: Organic vs paid analysis

### Profitability
- **GET /api/profitability** - Margin analysis
  - Filters: start_date, end_date, platform, warehouse
  - Returns: Profit margin, contribution, profitability status
- **GET /api/profitability/cost-breakdown** - Cost analysis
  - Returns: Cost components (product, platform, shipping, etc.)

### Inventory
- **GET /api/inventory** - Inventory data
  - Filters: platform, warehouse, sku, status
  - Returns: Stock levels, days of cover, reorder status
- **GET /api/inventory/alerts** - Inventory alerts
  - Returns: Low stock, stockout, overstock counts

### Warehouses
- **GET /api/warehouses** - Warehouse locations and health
  - Returns: All warehouses with location, inventory, health status
- **GET /api/warehouses/{warehouse_id}** - Warehouse details
  - Returns: Detailed warehouse information

### Alerts
- **GET /api/alerts** - Active business alerts
  - Filters: severity, alert_type, resolved
  - Returns: Ranked alerts by severity
- **POST /api/alerts/{alert_id}/acknowledge** - Mark alert as seen
- **POST /api/alerts/{alert_id}/resolve** - Mark alert as resolved

### AI Assistant
- **POST /api/ai/ask** - Ask business questions
  - Body: {question: string, context?: dict}
  - Returns: Answer, confidence, data sources, recommendations
- **GET /api/ai/suggestions** - Suggested questions
  - Returns: List of common business questions
- **POST /api/ai/explain-metric** - Explain a metric
  - Body: {metric: string}
  - Returns: Definition, formula, interpretation

### Reports
- **GET /api/reports** - List all reports
  - Returns: Report history
- **POST /api/reports/generate** - Generate a new report
  - Body: {report_type, start_date, end_date, format, filters}
  - Returns: Report ID and download URL
- **GET /api/reports/{report_id}** - Download report
  - Query: format (pdf, excel, html)
- **POST /api/reports/{report_id}/email** - Email report
  - Body: {email_to: string}
  - Returns: Confirmation

## Running the System

### Option 1: Using Start Scripts

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**Linux/Mac (Bash):**
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Setup

**Backend:**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd dashboard
npm install
npm run dev
```

## Environment Variables

Create a `.env` file in the root directory:

```env
# API
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=mysql+pymysql://sleepsia:sleepsia@localhost:3306/sleepsia_reporting

# Data source
SOURCE_WORKBOOK=data/final_sleepsia_report_data.xlsx

# Optional: Use mock data
USE_MOCK_DATA=false

# Optional: LLM API keys (for AI features)
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
```

## Integration Flow

### 1. Frontend Makes Request
```javascript
// dashboard/src/services/analyticsApi.js
const response = await analyticsApi.getKPIs({
  start_date: "2024-01-01",
  end_date: "2024-01-31",
  platform: "Amazon"
});
```

### 2. FastAPI Route Handler
```python
# backend/routes/kpis.py
@router.get("/kpis")
async def get_kpis(start_date, end_date, platform):
    orchestrator = AgentOrchestrator()
    kpis = orchestrator.get_kpis(
        start_date=start_date,
        end_date=end_date,
        platform=platform
    )
    return {"status": "success", "data": kpis}
```

### 3. Agent Orchestrator Coordinates
```python
# backend/services/agent_orchestrator.py
def get_kpis(self, start_date, end_date, platform):
    # 1. Query database
    data = query_database(start_date, end_date, platform)
    
    # 2. Validate using DataValidationAgent
    validation_result = self.validation_agent.validate(data)
    
    # 3. Calculate metrics using MetricsEngine
    metrics = self.metrics_engine.calculate_product_metrics(...)
    
    # 4. Analyze patterns using DataAnalysisAgent
    analysis = self.analysis_agent.analyze_product_performance(metrics)
    
    # 5. Generate insights using InsightRecommendationAgent
    insights = self.insight_agent.generate_recommendations(analysis)
    
    # 6. Return aggregated KPIs
    return aggregate_kpis(metrics, analysis, insights)
```

### 4. Response Sent to Frontend
```json
{
  "status": "success",
  "data": {
    "total_revenue": 1250000,
    "gross_profit": 375000,
    "profit_margin": 30.0,
    "total_orders": 2500,
    "avg_order_value": 500,
    "return_rate": 8.5,
    "cancellation_rate": 5.2,
    "ads_spend": 50000,
    "roas": 15.0,
    "acos": 6.67
  }
}
```

## Agent Responsibilities

### DataValidationAgent
- **Location**: `agents/validation_agent.py`
- **Responsibility**: Validate source data before processing
- **Input**: Raw data (DataFrame)
- **Output**: ValidationResult (PASS, PASS_WITH_WARNINGS, FAIL)
- **Usage**: Called by orchestrator for data quality checks

### MetricsEngine
- **Location**: `analytics/metrics_engine.py`
- **Responsibility**: Calculate all financial metrics deterministically
- **Input**: Raw transaction data
- **Output**: ProductMetrics, PlatformMetrics, DailyMetrics, TrendMetrics
- **Metrics Calculated**:
  - Revenue (gross, net, organic, attributed)
  - Profitability (margin, contribution, status)
  - Advertising (ROAS, ACOS, CTR, attribution)
  - Quality (return rate, cancellation rate)
  - Trends (moving averages, trend strength)

### DataAnalysisAgent
- **Location**: `agents/analysis_agent.py`
- **Responsibility**: Analyze pre-calculated metrics for patterns and anomalies
- **Input**: ProductMetrics, PlatformMetrics
- **Output**: List of PerformanceFinding with severity levels
- **Analysis Types**:
  - Product performance (profitability, quality issues)
  - Platform performance (channel comparison)
  - Advertising efficiency (ROAS, ACOS analysis)
  - Inventory health (stock levels, reorder status)

### InsightRecommendationAgent
- **Location**: `agents/insight_recommendation_agent.py`
- **Responsibility**: Generate actionable business recommendations
- **Input**: Analysis findings
- **Output**: Prioritized recommendations with expected impact
- **Recommendation Types**:
  - Product optimization (price, cost, marketing)
  - Platform strategy (allocation, focus)
  - Advertising optimization (budget reallocation)
  - Inventory optimization (reorder, safety stock)

### LLMAnalysisAgent
- **Location**: `agents/llm_analysis_agent.py`
- **Responsibility**: Natural language understanding and explanation
- **Input**: Business question, context data
- **Output**: Natural language answer with confidence
- **Capabilities**:
  - Question intent understanding
  - Metric calculation coordination
  - Business explanation
  - Recommendation generation
  - Follow-up question handling

### ReportAgent
- **Location**: `agents/report_agent.py`
- **Responsibility**: Generate formatted business reports
- **Input**: Metrics, analysis, insights
- **Output**: PDF, Excel, HTML reports
- **Report Types**:
  - Executive summary
  - Platform analysis
  - Product analysis
  - Profitability deep-dive
  - Advertising analysis
  - Inventory analysis
  - Management monthly report

## Data Flow Example: Get KPIs

```
User opens Dashboard
    ↓
Frontend calls GET /api/kpis
    ↓
FastAPI route handler receives request
    ↓
AgentOrchestrator.get_kpis() is called
    ↓
1. Query MySQL for sales, costs, returns, ads data (filtered)
    ↓
2. DataValidationAgent validates the data
    ↓
3. MetricsEngine calculates all financial metrics
    ↓
4. DataAnalysisAgent identifies patterns (profitable vs unprofitable)
    ↓
5. InsightRecommendationAgent generates recommendations
    ↓
6. Aggregate into KPI response
    ↓
FastAPI returns JSON response
    ↓
Frontend displays in dashboard
```

## Testing Endpoints

### Using curl:
```bash
# Get KPIs
curl "http://localhost:8000/api/kpis?start_date=2024-01-01&end_date=2024-01-31"

# Get platform performance
curl "http://localhost:8000/api/platform-performance"

# Get alerts
curl "http://localhost:8000/api/alerts?severity=critical"

# View API documentation
open http://localhost:8000/docs
```

### Using Python:
```python
import requests

response = requests.get(
    "http://localhost:8000/api/kpis",
    params={
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "platform": "Amazon"
    }
)

print(response.json())
```

## Next Steps for Full Integration

The skeleton is in place. To complete the integration:

1. **Implement Database Queries**
   - Create database connection in `backend/database.py`
   - Implement data fetch functions for each domain
   - Add query functions for filtered data

2. **Implement Agent Calls**
   - Update `AgentOrchestrator` methods to actually call agents
   - Pass real data to agents
   - Process agent outputs

3. **Add Error Handling**
   - Handle database connection errors
   - Handle agent execution errors
   - Return appropriate error responses

4. **Add Authentication**
   - Implement user authentication
   - Add request logging
   - Add API rate limiting

5. **Optimize Performance**
   - Add caching for expensive calculations
   - Implement pagination for large datasets
   - Add async database queries

6. **Complete AI Features**
   - Connect LLMAnalysisAgent to real LLM (OpenAI/Anthropic)
   - Implement question parsing
   - Add conversation history

7. **Complete Report Generation**
   - Implement ReportAgent rendering
   - Add PDF/Excel export
   - Implement email distribution

## Architecture Decisions

### Why Not Microservices?
- MVP requires simplicity and speed
- Single backend process easier to debug
- Database is shared anyway (no data isolation benefit)
- Can scale to microservices later if needed

### Why Agent Orchestrator?
- Centralizes agent coordination
- Makes data flow clear
- Easier to add new agents later
- Simplifies testing and debugging

### Why Separate Service Layer?
- Keeps routes clean (just HTTP handling)
- Makes services reusable
- Easier to test business logic separately
- Supports multiple entry points (API, CLI, etc.)

### Why FastAPI?
- Fast performance
- Easy async support
- Built-in documentation (Swagger UI)
- Pydantic validation
- Type hints for IDE support

### Why No ORM at MVP Level?
- Raw queries are faster for analytics
- Easier to write complex aggregations
- Can add ORM later
- SQL more familiar to analytics teams
