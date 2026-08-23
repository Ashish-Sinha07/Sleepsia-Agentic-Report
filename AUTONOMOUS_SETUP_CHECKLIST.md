# Autonomous Reporting System - Setup Checklist

Complete these steps to enable autonomous daily report generation and distribution.

## Phase 1: Dependencies & Configuration

### 1.1 Install Required Packages
- [ ] Run `pip install -r requirements.txt`
- [ ] Run `pip install -r backend/requirements.txt`
- [ ] Verify installation: `python -c "import apscheduler; import reportlab; print('OK')"`

### 1.2 Set Up Email (Gmail Example)

#### 1.2.1 Create/Enable Gmail Account
- [ ] Have a Gmail account ready (or use your organization's Google Workspace account)
- [ ] Go to [myaccount.google.com](https://myaccount.google.com)

#### 1.2.2 Enable 2-Step Verification
- [ ] Click "Security" in left menu
- [ ] Find "2-Step Verification" → Click "Get started"
- [ ] Follow prompts to enable 2-Step Verification on your phone

#### 1.2.3 Generate App Password
- [ ] Go back to Security
- [ ] Find "App passwords" (appears after 2-Step is enabled)
- [ ] Select "Mail" → "Windows Computer" (or your device)
- [ ] Google generates a 16-character password
- [ ] Copy this password (you'll use it in step 1.3)

#### 1.2.4 Alternative: Non-Gmail SMTP
- [ ] If not using Gmail, get your SMTP server details:
  - [ ] SMTP Host (e.g., smtp.company.com)
  - [ ] SMTP Port (usually 587 for TLS or 465 for SSL)
  - [ ] Username (usually your email)
  - [ ] Password (from your email admin)

### 1.3 Configure Environment Variables

#### 1.3.1 Create .env File
```bash
cp .env.example .env
```

#### 1.3.2 Edit .env with SMTP Details
```bash
# For Gmail:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=<16-char-app-password-from-step-1.2.3>
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Sleepsia Reports

# For custom SMTP server:
SMTP_HOST=<your-smtp-host>
SMTP_PORT=<your-smtp-port>
SMTP_USERNAME=<your-username>
SMTP_PASSWORD=<your-password>
SMTP_FROM_EMAIL=<your-email>
SMTP_FROM_NAME=Sleepsia Reports
```

#### 1.3.3 Configure Recipients & Schedule
```bash
REPORT_RECIPIENT_EMAIL=ningthoujamrohit91@gmail.com
REPORT_CC_EMAILS=                    # Leave empty or add comma-separated emails
REPORT_BCC_EMAILS=                   # Leave empty or add comma-separated emails
REPORT_SCHEDULE_HOUR=6               # Change to desired hour (0-23)
REPORT_SCHEDULE_MINUTE=0             # Change to desired minute (0-59)
```

#### 1.3.4 Optional: Anthropic API Key (for AI analysis)
```bash
ANTHROPIC_API_KEY=sk-...  # Get from https://console.anthropic.com/account/keys
```

### 1.4 Verify Database Connection
- [ ] Test MySQL connection: `python backend/scripts/test_connection.py`
- [ ] Database `sleepsia` exists and is populated
- [ ] User credentials in DATABASE_URL are correct
- [ ] If test fails, see `DATABASE_CONNECTION_DIAGNOSIS.md`

## Phase 2: Testing

### 2.1 Test Email Configuration
```bash
# Run manual report generation (generates without sending by default)
python backend/scripts/run_manual_report.py --no-send
```
- [ ] Report files created in `~/.sleepsia/reports/` or configured output dir
- [ ] Check logs for any errors

### 2.2 Test Email Delivery
```bash
# Generate and send a test report to configured recipient
python backend/scripts/run_manual_report.py
```
- [ ] Check `manual_report.log` for success
- [ ] **Check recipient's email** — report should arrive within 30 seconds
- [ ] If email not received:
  - [ ] Check SMTP credentials in .env
  - [ ] Check spam/junk folder
  - [ ] Review error logs

### 2.3 Verify All Stages Execute
- [ ] All 8 stages logged: INGESTION → VALIDATION → METRICS → ANALYSIS → INSIGHTS → REPORT → DISTRIBUTION → AUDIT
- [ ] No fatal errors in logs
- [ ] Output files readable (PDF opens, Excel opens)

## Phase 3: Deploy Autonomous Scheduler

### 3.1 Start Background Scheduler
```bash
# Option A: Foreground (see logs immediately)
python backend/scripts/run_autonomous_scheduler.py

# Option B: Background (nohup on Linux/Mac)
nohup python backend/scripts/run_autonomous_scheduler.py > scheduler.log 2>&1 &

# Option C: Background (PowerShell on Windows)
Start-Process -WindowStyle Hidden -FilePath python -ArgumentList 'backend\scripts\run_autonomous_scheduler.py'
```

- [ ] Scheduler starts without errors
- [ ] Logs show: "Scheduler is running"
- [ ] Logs show scheduled job details
- [ ] Logs show next execution time

### 3.2 Verify Scheduler Is Running
```bash
# Check if process is alive
ps aux | grep run_autonomous_scheduler.py  # Linux/Mac
Get-Process | grep python                   # Windows
```
- [ ] Process is active
- [ ] No errors in logs

### 3.3 Monitor First Scheduled Run

#### Option A: Wait for Scheduled Time
- [ ] Check `reports_scheduler.log` at configured hour (default 6 AM)
- [ ] Verify workflow executed successfully
- [ ] Check email inbox for report delivery

#### Option B: Force Immediate Test Run (from Python)
```python
from analytics.scheduler import get_scheduler

scheduler = get_scheduler()
result = scheduler.execute_now()
print(result)
```
- [ ] Verify report generated
- [ ] Verify email sent
- [ ] Check `reports_scheduler.log`

## Phase 4: Production Hardening

### 4.1 Set Up Log Rotation
- [ ] Configure logrotate (Linux) or Windows Event Viewer
- [ ] Prevent log files from growing unbounded
- [ ] Archival: `reports_scheduler.log`, `manual_report.log`, `workflow_audit.log`

### 4.2 Set Up Monitoring/Alerting
- [ ] Monitor scheduler process (e.g., check every hour that process is alive)
- [ ] Alert if scheduler crashes or stops responding
- [ ] Track email delivery failures

### 4.3 Regular Testing
- [ ] Weekly: Run manual report and verify email delivery
- [ ] Monthly: Review logs for errors/failures
- [ ] Quarterly: Update recipient list if needed

### 4.4 Backup & Recovery
- [ ] Back up `.env` file (contains SMTP credentials)
- [ ] Back up `checkpoint_dir` (workflow state history)
- [ ] Document recovery procedure if scheduler fails

### 4.5 Security Best Practices
- [ ] `.env` file should NOT be committed to git (already in `.gitignore`)
- [ ] SMTP password is sensitive — store securely
- [ ] Restrict file permissions: `chmod 600 .env`
- [ ] Use strong/unique app passwords for email
- [ ] Rotate SMTP credentials periodically

## Phase 5: Customization (Later)

### 5.1 Change Recipients
Edit `.env`:
```bash
REPORT_RECIPIENT_EMAIL=new-email@company.com
REPORT_CC_EMAILS=manager@company.com,director@company.com
```
- [ ] Restart scheduler
- [ ] Verify next scheduled report goes to new recipients

### 5.2 Change Schedule
Edit `.env`:
```bash
REPORT_SCHEDULE_HOUR=9         # Change to 9 AM
REPORT_SCHEDULE_MINUTE=30      # Change to 9:30 AM
```
- [ ] Restart scheduler
- [ ] Verify next run is at new time

### 5.3 Change Schedule Pattern (Advanced)
Edit `analytics/scheduler.py`, line ~138:
```python
# Change day_of_week parameter:
"mon-fri"           # Weekdays only (default)
"*"                 # Every day
"mon"               # Mondays only
"0,2,4"             # Sunday, Tuesday, Thursday
```
- [ ] Restart scheduler

## Verification Checklist (Final)

- [ ] Dependencies installed
- [ ] `.env` configured with valid SMTP credentials
- [ ] Database connection verified
- [ ] Manual report generates and sends successfully
- [ ] Scheduler starts without errors
- [ ] Logs show scheduled job configured
- [ ] Logs show successful pipeline execution
- [ ] Recipient receives email with PDF and Excel attachments
- [ ] Scheduler running in background/process manager
- [ ] Next scheduled run time is correct
- [ ] Log rotation configured
- [ ] Backup/recovery documented

## Support

**For issues, check these files in order:**
1. `reports_scheduler.log` or `manual_report.log` — execution logs
2. `REPORT_AND_AUTONOMOUS_SETUP.md` — detailed documentation
3. `DATABASE_CONNECTION_DIAGNOSIS.md` — if database connection fails
4. `FINAL_CHECKLIST.md` — general project status

**Need help?**
- Email: Rohit Kumar (author)
- Date: 2026-08-23
