# Sleepsia Agentic Reporting

MVP business intelligence system for unified e-commerce and quick-commerce reporting across Amazon, Blinkit, Flipkart, Myntra, and JioMart.

## Project Layout

- `.claude/`: architecture, business rules, agent, UI, database, and delivery guidance.
- `data/`: immutable source workbook (`final_sleepsia_report_data.xlsx`).
- `backend/`: FastAPI application.
- `dashboard/`: React frontend.
- `agents/`: controlled AI assistant tools.
- `analytics/`: deterministic metric engine.
- `database/`: database access and ingestion.
- `reports/`: report generation.
- `automation/`: distribution integrations.
- `tests/`: automated tests.
- `sql/`: database schema and views.

## Quick Start

1. Copy `.env.example` to `.env` and adjust values.
2. Start MySQL with `docker compose up -d`.
3. Create a Python environment and install `pip install -r requirements.txt`.
4. Add the FastAPI and dashboard implementations in their respective folders.

The source workbook is treated as immutable. Do not edit it in place.
