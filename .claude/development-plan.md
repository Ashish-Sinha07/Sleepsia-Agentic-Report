
---

# 7. `.claude/development-plan.md`

```markdown
# Sleepsia MVP Development Plan

## Timeline

Target:

2 days

Team:

4 developers

---

# Phase 0 — Project Setup

All members:

- Clone repository
- Create branches
- Configure Python environment
- Configure Node.js environment
- Configure MySQL
- Configure .env
- Add source workbook
- Add .claude documentation

Frontend:

React + Vite
Tailwind CSS

Backend:

FastAPI

---

# Phase 1 — Data Profiling

Owner:

Developer 1

Tasks:

- Inspect Excel workbook
- Profile every sheet
- Identify relationships
- Identify duplicate/derived fields
- Identify required fields
- Create data profile

Deliverables:

docs/data-profile.md
docs/database-recommendation.md

---

# Phase 2 — Database + ETL

Owner:

Developer 1

Tasks:

- Create MySQL schema
- Create tables
- Add indexes
- Add foreign keys
- Create analytical views
- Create data loader
- Create validation

Deliverables:

sql/schema.sql
sql/indexes.sql
sql/views.sql
database/loader.py
database/validation.py

---

# Phase 3 — Analytics

Owner:

Developer 2

Tasks:

- KPI engine
- Platform analysis
- Product analysis
- Profitability
- Advertising
- Inventory
- Alerts

Deliverables:

analytics/

---

# Phase 4 — FastAPI Backend

Owner:

Developer 2

Tasks:

Create endpoints:

GET /api/kpis
GET /api/platform-performance
GET /api/product-performance
GET /api/advertising
GET /api/profitability
GET /api/inventory
GET /api/warehouses
GET /api/alerts

POST /api/ai/query

POST /api/reports/generate

---

# Phase 5 — React Frontend

Owner:

Developer 3

Technology:

React
Vite
Tailwind CSS
React Router
Axios
Recharts/ECharts
React Leaflet

Tasks:

- Application shell
- Sidebar
- Header
- Global filters
- Executive dashboard
- Platform analysis
- Product analysis
- Advertising
- Profitability
- Inventory
- Warehouse map
- Alerts
- AI Assistant
- Reports

---

# Phase 6 — AI Assistant

Owner:

Developer 2

Tasks:

- Intent handling
- Controlled tools
- Tool routing
- Response generation
- Follow-up context
- Recommendation generation

Do not implement RAG.

Do not implement unrestricted SQL.

---

# Phase 7 — Reporting

Owner:

Developer 4

Tasks:

- PDF generation
- Excel generation
- Management summary
- Recommendations
- Report templates

---

# Phase 8 — Automation

Owner:

Developer 4

Power Automate:

Scheduled trigger
    ↓
Generate report
    ↓
Retrieve report
    ↓
Send Outlook email
    ↓
Teams notification

---

# Phase 9 — Frontend/Backend Integration

Developer 3 + Developer 2

Test:

React
 ↓
FastAPI
 ↓
Analytics
 ↓
MySQL

Verify:

- Filters
- API responses
- Pagination
- Loading states
- Error states
- AI queries
- Report generation

---

# Phase 10 — Integration

All members.

Full pipeline:

Excel
 ↓
Validation
 ↓
MySQL
 ↓
Analytics
 ↓
FastAPI
 ↓
React
 ↓
AI
 ↓
Reports
 ↓
Power Automate
 ↓
Outlook

---

# Phase 11 — Testing

Required scenarios:

1. Revenue calculation
2. Profit calculation
3. ROAS
4. ACOS
5. Return rate
6. Cancellation rate
7. Inventory status
8. Stockout detection
9. Platform comparison
10. Product profitability
11. AI numerical answer
12. AI recommendation
13. Report generation
14. Dashboard filters
15. Warehouse map
16. API error handling
17. Empty filter results
18. Report download

---

# Phase 12 — Demo

## Scenario 1

"Which platform is performing best?"

---

## Scenario 2

"Which products are unprofitable?"

---

## Scenario 3

"Why did profitability decline?"

---

## Scenario 4

"Which warehouse needs replenishment?"

---

## Scenario 5

"Which platform has the best ROAS?"

---

## Scenario 6

"Generate the management summary."

---

# Git Strategy

Branches:

feature/database
feature/backend
feature/analytics
feature/frontend
feature/ai-assistant
feature/reporting

Integration:

feature branches
    ↓
develop
    ↓
integration testing
    ↓
main

---

# Definition of Done

The MVP is complete when:

- MySQL contains source data.
- Data validation works.
- KPI calculations work.
- Analytics work.
- FastAPI works.
- React dashboard works.
- Tailwind styling works.
- Filters work.
- Warehouse map works.
- Alerts work.
- AI assistant answers database-backed questions.
- AI does not invent numbers.
- Reports can be generated.
- Automated distribution works or is demonstrated.
- Tests pass.
- README is complete.
- Architecture documentation is complete.