# Sleepsia Agentic Business Reporting System

## 1. Project Identity

Project Name:
Sleepsia Agentic Business Reporting System

Organization:
Sleepsia

Project Type:
Agentic Business Intelligence, Financial Reporting, E-commerce Analytics and Operational Intelligence

Project Objective:

Build an MVP system that consolidates sales, advertising, financial, inventory, warehouse, returns and cancellation data from multiple e-commerce and quick-commerce platforms and provides:

- Unified business reporting
- Product-wise analysis
- Platform-wise analysis
- Profitability analysis
- Advertising analysis
- Organic vs inorganic sales analysis
- Inventory and warehouse analysis
- Regional demand analysis
- Business alerts
- AI-powered business assistant
- Management reports
- Automated report distribution

Supported platforms:

- Amazon
- Blinkit
- Flipkart
- Myntra
- JioMart

The system must be simple enough to implement within two days while demonstrating a complete end-to-end architecture.

---

# 2. Development Philosophy

This is an MVP.

DO NOT over-engineer the system.

Prefer:

- Simple
- Maintainable
- Testable
- Modular
- Fast to implement
- Easy to demonstrate

Avoid unnecessary:

- Microservices
- Kubernetes
- Kafka
- Databricks
- Complex data lakes
- Vector databases
- Complex ML pipelines
- Large numbers of LLM agents
- Unrestricted text-to-SQL
- Complex infrastructure

The MVP should demonstrate business value rather than infrastructure complexity.

---

# 3. Technology Stack

## Frontend

- React.js
- Vite
- Tailwind CSS
- React Router
- Axios or Fetch API
- Recharts or Apache ECharts
- React Leaflet
- Lucide React

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy

## Database

- MySQL 8+

## Data Processing

- Pandas
- SQLAlchemy

## Analytics

- SQL
- Python

## AI

- LLM-based business assistant
- Controlled analytical tools
- Tool-based agent architecture

## Automation

- Power Automate

## Email

- Outlook

## Reporting

- PDF
- Excel

## Version Control

- Git
- GitHub

---

# 4. Source Data

The primary source workbook is:

data/Sleepsia_Copilot_Studio_Clean_Excel_Tables_With_JioMart.xlsx

The workbook contains business data related to:

- Products
- Platforms
- Sales
- Advertising
- Costs
- Returns
- Cancellations
- Warehouses
- Inventory
- Regional sales
- KPIs
- Replenishment
- Supply chain

Never modify the original source workbook.

Treat the original workbook as immutable source data.

---

# 5. Core Architecture

Logical architecture:

Data Sources
    ↓
Orchestration
    ↓
Data Ingestion
    ↓
Raw/Staging Data
    ↓
Validation
    ↓
Unified Business Data
    ↓
Business Metric Engine
    ↓
Analytics Engine
    ↓
Agentic AI Layer
    ↓
Report Generation
    ↓
Distribution
    ↓
Audit and Monitoring

MVP implementation:

Source Excel/CSV
    ↓
Python ingestion
    ↓
Validation
    ↓
MySQL
    ↓
Analytics Engine
    ↓
FastAPI
    ↓
React + Tailwind CSS
    ↓
AI Assistant / Reports

---

# 6. AI Architecture

The AI assistant must NOT directly calculate financial metrics.

Use:

User Question
    ↓
Intent Understanding
    ↓
Controlled Analytical Tool
    ↓
SQL / Analytics Engine
    ↓
Structured Result
    ↓
LLM Explanation
    ↓
Recommendation

The LLM must never invent numerical values.

All numerical answers must originate from the database or deterministic analytics layer.

Do not implement unrestricted LLM-generated SQL execution.

Do not implement RAG for structured transactional business data.

RAG may be introduced later for unstructured documents such as:

- Business policies
- SOPs
- Product documentation
- Operational guidelines

RAG is NOT required for the MVP.

---

# 7. Deterministic vs AI Responsibilities

Deterministic systems must handle:

- Revenue
- Sales
- Units
- Orders
- Advertising spend
- ROAS
- ACOS
- Product cost
- Platform fees
- Profit
- Profit margin
- Returns
- Cancellations
- Inventory
- Days of cover
- Reorder calculations
- Threshold detection
- Rankings
- Aggregations

AI may handle:

- Natural-language question understanding
- Tool selection
- Business explanation
- Summarization
- Root-cause exploration
- Recommendations
- Management summaries
- Follow-up questions

---

# 8. Frontend Architecture

The frontend is a separate React application.

Architecture:

React.js + Tailwind CSS
        ↓
REST API
        ↓
FastAPI
        ↓
Analytics / AI / Reports
        ↓
MySQL

The frontend must NOT:

- Connect directly to MySQL
- Execute SQL
- Calculate financial metrics
- Apply business rules
- Generate AI responses

The frontend only:

- Displays data
- Collects filters
- Sends API requests
- Displays analytics
- Displays AI responses
- Initiates report generation

---

# 9. Backend Architecture

FastAPI provides the API layer.

Recommended API groups:

/api/kpis
/api/platform-performance
/api/product-performance
/api/advertising
/api/profitability
/api/inventory
/api/warehouses
/api/alerts
/api/ai
/api/reports

Backend responsibilities:

- API validation
- Authentication if required
- Database access
- Analytics services
- AI orchestration
- Report generation
- Error handling

---

# 10. Code Quality Rules

Before modifying the repository:

1. Inspect existing files.
2. Understand existing architecture.
3. Reuse existing functionality.
4. Do not duplicate business logic.
5. Do not create unnecessary files.
6. Do not break existing APIs.
7. Do not change database schemas without checking dependencies.
8. Use environment variables for secrets.
9. Never hardcode credentials.
10. Use parameterized SQL.
11. Add error handling.
12. Add tests for important business calculations.
13. Keep frontend and backend responsibilities separate.

---

# 11. Database Rules

MySQL is the system of record for the MVP.

Do not store calculated metrics redundantly unless there is a clear performance reason.

Prefer:

Raw/transactional data
    ↓
SQL views
    ↓
Analytics layer
    ↓
FastAPI
    ↓
React / AI / Reports

Use indexes for:

- date
- SKU
- platform
- warehouse
- product

Use foreign keys wherever practical.

---

# 12. Dashboard Rules

The frontend must be management-oriented.

Required pages:

1. Executive Dashboard
2. Platform Analysis
3. Product Analysis
4. Advertising
5. Profitability
6. Inventory & Warehouse
7. Alerts
8. AI Business Assistant
9. Reports

Required filters:

- Date range
- Platform
- Product
- SKU
- Region
- Warehouse

The frontend must use reusable React components.

---

# 13. Warehouse Visualization

The dashboard must include an India warehouse map.

Each warehouse should contain:

- Warehouse name
- City
- Latitude
- Longitude
- Total inventory
- SKU count
- Low-stock SKU count
- Stockout count
- Days of cover
- Warehouse health

Warehouse statuses:

- Healthy
- Low Stock
- Critical
- Stockout

The map should support:

- Hover
- Click
- Popup
- Filtering
- Zoom
- Pan

---

# 14. Agent Rules

Recommended logical components:

1. Validation Agent
2. Analytics Agent
3. Alert Engine
4. Report Agent
5. AI Business Assistant

Not every component needs to be an LLM agent.

Prefer deterministic Python services for:

- Validation
- KPI calculation
- Alert rules
- Report calculations

Use LLM reasoning primarily for:

- Natural-language understanding
- Tool selection
- Explanation
- Recommendations

---

# 15. Agent Safety

Agents must:

- Use validated data
- Never invent metrics
- Never fabricate records
- Never claim a calculation that was not performed
- Clearly state when data is unavailable
- Use controlled tools
- Respect business rules
- Return structured results where possible

If required data does not exist:

"I don't have sufficient data to answer that accurately."

---

# 16. Development Workflow

For every feature:

PLAN
    ↓
IMPLEMENT
    ↓
TEST
    ↓
REVIEW
    ↓
INTEGRATE

When asked to implement a complex feature:

1. Inspect the repository.
2. Explain the implementation plan.
3. Identify affected files.
4. Implement the smallest maintainable solution.
5. Run tests.
6. Fix failures.
7. Summarize changes.

Do not make unrelated changes.

---

# 17. Git Rules

Never directly modify main unless explicitly requested.

Use feature branches:

feature/database
feature/backend
feature/analytics
feature/frontend
feature/ai-assistant
feature/reporting

Preferred integration:

feature branches
    ↓
develop
    ↓
integration testing
    ↓
main

Keep commits focused.

Examples:

feat: add MySQL schema

feat: add sales analytics

feat: add React dashboard

feat: add AI business assistant

feat: add management report

---

# 18. MVP Priority

Priority 1:

- MySQL database
- Data loading
- Validation
- KPI calculations
- Analytics
- FastAPI
- React dashboard
- AI assistant

Priority 2:

- Warehouse map
- Alerts
- Reports

Priority 3:

- Power Automate
- Outlook distribution
- Advanced recommendations

If time is limited, complete Priority 1 before advanced features.

---

# 19. Expected Final User Experience

Management should be able to:

1. Open the dashboard.
2. Select a date range.
3. Select platform/product/warehouse.
4. View financial KPIs.
5. Compare platforms.
6. Identify profitable and unprofitable products.
7. Analyze advertising efficiency.
8. View warehouse inventory.
9. Identify critical alerts.
10. Ask the AI assistant business questions.
11. Receive recommendations.
12. Generate management reports.
13. Download reports.
14. Distribute reports automatically.

---

# 20. Critical Instruction

When uncertain between a simple implementation and a complex implementation:

Choose the simpler implementation that satisfies the business requirement.

Do not introduce new infrastructure unless necessary.

The primary goal is a working end-to-end MVP.