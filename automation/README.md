# Automation: Report Generation & Distribution

Complete autonomous report generation and email distribution system.

**Author:** Rohit Kumar  
**Date:** 2026-08-23  
**Status:** ✅ Ready to Use

---

## Overview

The `automation/` folder contains everything needed to generate business reports and distribute them via email, either on a daily schedule or on-demand.

### Two Main Components

**A) Email Service** (`email_service.py`)
- Send report attachments (PDF, Excel, etc.) via SMTP
- Support for TO, CC, BCC recipients
- Works with Gmail (App Password) or any SMTP server
- Can be used standalone by other parts of the system

**B) Report + Scheduler** (`report_generator.py` + `scheduler.py`)
- Generate daily reports (metrics → insights → PDF/Excel)
- Schedule automatic execution (default: 6 AM, weekdays)
- Run manual reports on-demand
- Full logging and error handling

---

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 2. Configure Email (Gmail Example)

**Create/get Gmail App Password:**
1. Go to myaccount.google.com → Security
2. Enable 2-Step Verification (if not already done)
3. Find "App passwords" → Select "Mail" → "Windows Computer"
4. Copy the 16-character password

**Update `.env` file:**
```bash
cp .env.example .env

# Edit .env:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=<16-char-app-password>
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Sleepsia Reports

REPORT_RECIPIENT_EMAIL=ningthoujamrohit91@gmail.com
REPORT_SCHEDULE_HOUR=6
REPORT_SCHEDULE_MINUTE=0
```

### 3. Test It Works
```bash
# Generate a test report and send it
python backend/scripts/generate_report_now.py

# Check your email (should arrive within 30 seconds)
# If successful, report PDF and Excel will be in the email
```

### 4. Start Autonomous Scheduler
```bash
# Run forever (reports send daily at configured time)
python backend/scripts/start_report_scheduler.py

# Or run in background:
nohup python backend/scripts/start_report_scheduler.py > scheduler.log 2>&1 &
```

The scheduler will now run every weekday at 6 AM (UTC), generate a report, and email it to the configured recipient.

---

## File Structure

```
automation/
├── __init__.py                    # Package marker
├── email_service.py               # B: Email service (standalone)
├── report_generator.py            # A: Report generation
├── scheduler.py                   # A: Daily scheduling
└── README.md                      # This file

backend/scripts/
├── start_report_scheduler.py      # Start continuous scheduler
├── generate_report_now.py         # On-demand report generation
└── (other scripts)
```

---

## Components

### Email Service (`email_service.py`)

**Class:** `ReportEmailService`

**Use it to send any report via email:**
```python
from automation.email_service import ReportEmailService

email_service = ReportEmailService()

# Send a report
success = email_service.send_report(
    subject="Daily Report - 2026-08-23",
    body="Please see attached report.",
    recipients=["user@example.com"],
    attachments={
        "report.pdf": pdf_bytes,
        "report.xlsx": excel_bytes,
    },
    cc=["manager@example.com"],
    bcc=["archive@example.com"],
)

# Test SMTP connection
email_service.test_connection()  # Returns True/False
```

**Methods:**
- `send_report(subject, body, recipients, attachments=None, cc=None, bcc=None) → bool`
- `test_connection() → bool`

**Configuration:** Uses settings from `.env` (SMTP_*, SMTP_FROM_*)

---

### Report Generator (`report_generator.py`)

**Class:** `AutomatedReportGenerator`

**Use it to generate reports:**
```python
from automation.report_generator import AutomatedReportGenerator
from datetime import date

generator = AutomatedReportGenerator()

# Generate a report and get bytes
attachments, success = generator.generate_daily_report(
    report_date=date(2026, 8, 23)
)

if success:
    pdf_bytes = attachments.get("report.pdf")
    excel_bytes = attachments.get("report.xlsx")
    # Use the bytes however you want
```

**Methods:**
- `generate_daily_report(report_date=None) → (dict, bool)` — Returns (attachments_dict, success)
- `generate_and_get_bytes(report_date=None) → (pdf_bytes, excel_bytes)` — Returns raw bytes

**Pipeline:**
1. Calculate metrics (MetricsEngine)
2. Generate insights (InsightEngine)
3. Generate recommendations (RecommendationEngine)
4. Build OmniChannelReport
5. Generate PDF via ReportService
6. Generate Excel via ReportService
7. Return both as byte strings

---

### Scheduler (`scheduler.py`)

**Class:** `ReportScheduler`

**Use it to schedule or manually run reports:**
```python
from automation.scheduler import ReportScheduler

scheduler = ReportScheduler()

# Schedule daily
scheduler.schedule_daily(hour=6, minute=0, day_of_week="mon-fri")
scheduler.start()  # Runs in background

# Or manually run right now
scheduler.execute_now()

# Check if running
if scheduler.is_running():
    print(f"Next run: {scheduler.get_next_run()}")

# Stop it
scheduler.stop()
```

**Methods:**
- `schedule_daily(hour=None, minute=None, day_of_week="mon-fri")` — Configure schedule
- `start()` — Start scheduler (runs in background)
- `stop()` — Stop scheduler
- `execute_now() → bool` — Run immediately
- `is_running() → bool` — Check status
- `get_next_run() → datetime` — Get next scheduled time

**Pipeline (when run):**
1. Generate report using AutomatedReportGenerator
2. Send email using ReportEmailService
3. Log all results

---

## Usage Examples

### Example 1: Start Daily Scheduler (most common)

```bash
python backend/scripts/start_report_scheduler.py
```

This runs forever, generating and emailing reports every weekday at 6 AM. Logs go to `report_scheduler.log`.

### Example 2: Generate Report Now (for testing)

```bash
# Today's report
python backend/scripts/generate_report_now.py

# Specific date
python backend/scripts/generate_report_now.py --date 2026-08-22

# Without sending (just test generation)
python backend/scripts/generate_report_now.py --no-send
```

### Example 3: Use Components Programmatically

```python
from automation.scheduler import ReportScheduler

scheduler = ReportScheduler()

# Run immediately
scheduler.execute_now()

# Or schedule and run forever
scheduler.schedule_daily(hour=9, minute=30)
scheduler.start()

# In another script later:
scheduler = ReportScheduler()
print(f"Next run at: {scheduler.get_next_run()}")
```

### Example 4: Use Email Service Standalone (for integration)

Teammates can call the email service to send reports they generate themselves:

```python
from automation.email_service import ReportEmailService

email = ReportEmailService()

# Generate report using their own code
their_report_bytes = generate_report_somehow()

# Use our email service to send it
email.send_report(
    subject="Custom Report",
    body="Report content",
    recipients=["user@example.com"],
    attachments={"report.pdf": their_report_bytes},
)
```

---

## Configuration

All settings come from `.env` file (environment variables):

```bash
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=<app-password>
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Sleepsia Reports

# Report Distribution
REPORT_RECIPIENT_EMAIL=user@example.com
REPORT_CC_EMAILS=manager@example.com,director@example.com
REPORT_BCC_EMAILS=archive@example.com

# Scheduling
REPORT_SCHEDULE_HOUR=6       # 0-23
REPORT_SCHEDULE_MINUTE=0     # 0-59

# Optional
ANTHROPIC_API_KEY=sk-...
```

**Defaults:**
- Schedule: 6 AM UTC, Monday-Friday
- Recipient: ningthoujamrohit91@gmail.com
- SMTP Port: 587 (TLS)

**To change later:** Edit `.env` and restart the scheduler.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'apscheduler'"
**Fix:** Install dependencies:
```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### "SMTPAuthenticationError" or "Connection refused"
**Fix:**
1. Check `.env` SMTP credentials
2. For Gmail: Use App Password, not regular password
3. Verify settings: `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`
4. Test connection:
   ```python
   from automation.email_service import ReportEmailService
   email = ReportEmailService()
   email.test_connection()  # Should print "✓ SMTP connection test successful"
   ```

### Report not being sent
1. Check logs: `cat report_scheduler.log`
2. Test manually: `python backend/scripts/generate_report_now.py`
3. Verify recipient email in `.env`
4. Check spam/junk folder

### Scheduler not starting
1. Check Python version (need 3.8+)
2. Check logs: `cat report_scheduler.log`
3. Verify all dependencies installed
4. Verify `.env` file exists with SMTP config

---

## Integration with Teammates' Code

Other team members can:

1. **Use the email service directly** (if they generate reports themselves):
   ```python
   from automation.email_service import ReportEmailService
   email = ReportEmailService()
   email.send_report(subject=..., body=..., recipients=..., attachments=...)
   ```

2. **Call the scheduler to run reports**:
   ```python
   from automation.scheduler import ReportScheduler
   scheduler = ReportScheduler()
   scheduler.execute_now()
   ```

3. **Wire it into the orchestrator** (if they have one):
   - Instead of calling their own service implementations, they can call:
     - `automation.report_generator.AutomatedReportGenerator` → generates reports
     - `automation.email_service.ReportEmailService` → sends emails
   - No changes needed to their orchestration framework

---

## Monitoring & Maintenance

### Check Status
```bash
# See what's running
ps aux | grep "start_report_scheduler.py"

# Check next scheduled run
tail -f report_scheduler.log | grep "next"
```

### View Logs
```bash
tail -f report_scheduler.log      # Scheduler logs
tail -f generate_report.log       # Manual generation logs
```

### Change Schedule
Edit `.env`, change `REPORT_SCHEDULE_HOUR` or `REPORT_SCHEDULE_MINUTE`, restart scheduler:
```bash
# Kill old scheduler
pkill -f "start_report_scheduler.py"

# Start new one with new schedule
python backend/scripts/start_report_scheduler.py
```

### Add More Recipients
Edit `.env`:
```bash
REPORT_RECIPIENT_EMAIL=primary@example.com
REPORT_CC_EMAILS=manager@example.com,director@example.com
```

Restart scheduler.

---

## What This Folder Contains (Your Scope)

✅ Complete email distribution system (`email_service.py`)  
✅ Complete report generation system (`report_generator.py`)  
✅ Complete autonomous scheduling (`scheduler.py`)  
✅ Entry point scripts (`backend/scripts/`)  
✅ Configuration via environment variables  
✅ Full logging and error handling  
✅ Documentation (this file)

**NOT in this folder (other teams' work):**
- Database schema & ETL
- FastAPI backend
- Frontend dashboard
- LLM agent orchestration
- Power Automate integration

---

## Next Steps (Optional)

1. Test SMTP connection (verify Gmail App Password works)
2. Run a manual report generation
3. Start the daily scheduler
4. Monitor first scheduled run
5. Change schedule/recipients as needed
6. Show teammates how to integrate

---

## Contact

**Author:** Rohit Kumar  
**Created:** 2026-08-23  
**Email:** ningthoujamrohit91@gmail.com

For questions about this automation system, see `backend/scripts/*.py` or this README.
