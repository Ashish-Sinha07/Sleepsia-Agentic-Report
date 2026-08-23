# Report Generation & Autonomous Scheduling System

## Overview

This document describes the completed **Report Generation** and **Autonomous Scheduling** system for the Sleepsia reporting platform. This system enables:

1. **On-Demand Report Generation** — generate PDF and Excel business reports immediately
2. **Automated Distribution** — email reports to configured recipients
3. **Autonomous Daily Execution** — run the full pipeline on a configured schedule (default: 6 AM daily, weekdays only)

## Architecture

### System Flow

```
Scheduler (APScheduler)
    ↓
Daily Trigger (6 AM by default)
    ↓
WorkflowOrchestrator (analytics/orchestration/)
    ├─→ IngestionService (load data from MySQL)
    ├─→ ValidationService (validate data quality)
    ├─→ MetricService (calculate KPIs)
    ├─→ AnalysisService (rule-based analysis)
    ├─→ InsightService (generate insights)
    ├─→ ReportService (PDF/Excel generation)
    ├─→ DistributionService (email delivery)
    └─→ MonitoringService (audit logging)
```

### Key Components

#### 1. **Concrete Service Implementations** (`analytics/concrete_services.py`)
Eight service classes that implement the orchestration interfaces:

- `ConcreteIngestionService` — Loads business data from MySQL views via backend API
- `ConcreteValidationService` — Validates data using `DataValidationAgent` (deterministic)
- `ConcreteMetricService` — Calculates metrics using `MetricsEngine`
- `ConcreteAnalysisService` — Analyzes metrics using `DataAnalysisAgent` (rule-based)
- `ConcreteInsightService` — Generates insights using `InsightEngine` + `RecommendationEngine`
- `ConcreteReportService` — Generates PDF/Excel via `reports/report_service.py`
- `ConcreteDistributionService` — Distributes reports via `SMTPEmailProvider`
- `ConcreteMonitoringService` — Audits workflow execution

#### 2. **Scheduler** (`analytics/scheduler.py`)
`ReportScheduler` class that:

- Uses APScheduler with Cron triggers
- Defines the 8-stage daily reporting workflow
- Instantiates all service implementations
- Executes the workflow on schedule
- Manages checkpoint/run state via `RunManager`

#### 3. **Entry Points**

**Autonomous Scheduler (continuous):**
```bash
python backend/scripts/run_autonomous_scheduler.py
```
Starts the background scheduler. Reports run daily at configured time, Monday-Friday.

**Manual Report (on-demand):**
```bash
python backend/scripts/run_manual_report.py [--date YYYY-MM-DD] [--no-send]
```
Generates a report immediately (optionally without sending email).

## Configuration

### Environment Variables (`.env`)

```bash
# SMTP Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use Gmail App Password, not your regular password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Sleepsia Reports

# Report Scheduling
REPORT_SCHEDULE_HOUR=6           # 0-23 (6 AM)
REPORT_SCHEDULE_MINUTE=0         # 0-59
REPORT_RECIPIENT_EMAIL=ningthoujamrohit91@gmail.com
REPORT_CC_EMAILS=                # Optional, comma-separated
REPORT_BCC_EMAILS=               # Optional, comma-separated

# Anthropic API (for optional AI-based analysis)
ANTHROPIC_API_KEY=your-api-key-here
```

### Email Configuration Details

#### Gmail Setup (Recommended)

1. Enable 2-Step Verification on your Google Account
2. Generate an **App Password** for Gmail:
   - Go to myaccount.google.com → Security
   - Select "App passwords" (under "Password & sign-in method")
   - Choose "Mail" and "Windows Computer"
   - Copy the generated 16-character password
3. Use this app password in `SMTP_PASSWORD`, NOT your regular Gmail password

#### Custom SMTP Server

Update the SMTP_* variables in `.env` to match your mail server:
- SMTP_HOST: your mail server hostname
- SMTP_PORT: typically 587 (TLS) or 465 (SSL)
- SMTP_USERNAME: your email/username
- SMTP_PASSWORD: your password

## Usage

### 1. Initial Setup

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Create .env file with SMTP config
cp .env.example .env
# Edit .env and fill in SMTP credentials and schedule
```

### 2. Start Autonomous Scheduler

```bash
# Run in foreground (see logs immediately)
python backend/scripts/run_autonomous_scheduler.py

# Or run in background with nohup
nohup python backend/scripts/run_autonomous_scheduler.py > scheduler.log 2>&1 &
```

The scheduler will:
- Start immediately
- Log configuration
- Wait for the scheduled time (6 AM by default)
- Execute the full pipeline automatically
- Run every weekday unless configured otherwise

### 3. Generate Reports On-Demand

```bash
# Generate today's report and send email
python backend/scripts/run_manual_report.py

# Generate specific date report
python backend/scripts/run_manual_report.py --date 2026-08-22

# Generate without sending (test only)
python backend/scripts/run_manual_report.py --no-send
```

### 4. Monitor Execution

Check `reports_scheduler.log` or `manual_report.log` for detailed execution logs:

```bash
# Monitor live
tail -f reports_scheduler.log

# View audit trail
cat workflow_audit.log
```

## File Structure

### New/Modified Files

```
analytics/
├── concrete_services.py          ← NEW: Service implementations
├── scheduler.py                  ← NEW: APScheduler-based orchestration
└── orchestration/                (unchanged, uses our service impls)

backend/
├── app/
│   └── config.py                 ← MODIFIED: Added SMTP/schedule config
├── scripts/
│   ├── run_autonomous_scheduler.py    ← NEW: Continuous scheduler entry point
│   └── run_manual_report.py           ← NEW: On-demand report entry point
└── requirements.txt              ← MODIFIED: Added reportlab, apscheduler, pytz, anthropic

reports/                          (unchanged, already complete)
├── report_service.py
├── generators/
│   ├── pdf_generator.py
│   └── excel_generator.py

.env.example                      ← MODIFIED: Added SMTP and schedule vars
requirements.txt                  ← MODIFIED: Added dependencies
```

## Workflow Stages (Daily Pipeline)

The orchestrator executes these stages sequentially:

1. **INGESTION** (ConcreteIngestionService)
   - Loads data from MySQL views for the business date
   - Sources: products, platforms, sales, advertising, inventory, alerts, warehouses

2. **VALIDATION** (ConcreteValidationService)
   - Data quality checks using DataValidationAgent
   - Detects missing fields, anomalies, data consistency issues

3. **METRICS** (ConcreteMetricService)
   - Calculates KPIs: ACOS, return rate, cancellation rate, etc.
   - Uses MetricsEngine with business rules

4. **ANALYSIS** (ConcreteAnalysisService)
   - Rule-based analysis of metrics against thresholds
   - Identifies anomalies, alerts, risk levels using DataAnalysisAgent

5. **INSIGHTS** (ConcreteInsightService)
   - Generates business insights from analysis
   - Produces recommendations using InsightEngine + RecommendationEngine

6. **REPORT** (ConcreteReportService)
   - Builds OmniChannelReport data structure
   - Generates PDF via reportlab
   - Generates Excel via openpyxl
   - Saves both to disk

7. **DISTRIBUTION** (ConcreteDistributionService)
   - Sends reports via SMTP to configured recipients
   - Queues delivery with retry/escalation logic

8. **AUDIT** (ConcreteMonitoringService)
   - Logs full workflow state to audit file
   - Records success/failure for compliance

## Email Output

### Recipient Configuration

Currently hardcoded to `ningthoujamrohit91@gmail.com` (can be changed in `.env`).

To add multiple recipients, update `.env`:
```bash
REPORT_CC_EMAILS=other1@company.com,other2@company.com
REPORT_BCC_EMAILS=archive@company.com
```

### Email Content

- **Subject:** `Sleepsia Daily Report - YYYY-MM-DD`
- **Body:** Template text (configurable)
- **Attachments:**
  - `report.pdf` — PDF report with formatted sections
  - `report.xlsx` — Excel workbook with multiple sheets

## Troubleshooting

### Scheduler Not Starting

**Error:** `ModuleNotFoundError: No module named 'apscheduler'`
- **Fix:** Run `pip install apscheduler pytz` or `pip install -r requirements.txt`

### SMTP Connection Failed

**Error:** `SMTPAuthenticationError` or `Connection refused`
- **Fix:** 
  - Verify SMTP credentials in `.env`
  - For Gmail: use App Password, not regular password
  - Check SMTP host/port (smtp.gmail.com:587 for Gmail TLS)
  - Ensure "Less secure app access" is enabled (for non-Gmail servers)

### Reports Not Sending

**Error:** `Delivery failed` in logs
- **Check:**
  - SMTP configuration correct
  - Recipient email valid
  - SMTP server reachable (test with `telnet smtp.gmail.com 587`)
  - App password correct (Gmail only)

### Database Connection Failed

**Error:** `Connection refused` or `Access denied`
- **Check:**
  - MySQL is running
  - DATABASE_URL in `.env` is correct
  - Database `sleepsia` exists
  - User credentials correct
  - See `DATABASE_CONNECTION_DIAGNOSIS.md` for detailed debugging

## Performance Considerations

- **Ingestion:** ~1-2 seconds (MySQL view queries)
- **Validation:** ~0.5 seconds (deterministic checks)
- **Metrics:** ~2-3 seconds (aggregation queries)
- **Analysis:** ~1 second (rule evaluation)
- **Insights:** ~1-2 seconds (engine processing)
- **Report Generation:** ~3-5 seconds (PDF/Excel rendering)
- **Distribution:** ~2-3 seconds (SMTP delivery)

**Total:** ~15-20 seconds per full run (typical)

## Future Enhancements

1. **Multiple Schedules** — Support different reports on different schedules (daily, weekly, monthly)
2. **Report Variants** — Product-specific, platform-specific, region-specific reports
3. **Conditional Distribution** — Send only if metrics meet certain thresholds
4. **Report Portal** — Web dashboard to view/download past reports
5. **Power Automate Integration** — Replace SMTP with Power Automate connector
6. **Slack/Teams Integration** — Send report summaries to messaging platforms
7. **PDF Customization** — Branding, logos, custom sections per recipient

## Contact

**Author:** Rohit Kumar  
**Date:** 2026-08-23  
**Component:** Report Generation & Autonomous Scheduling
