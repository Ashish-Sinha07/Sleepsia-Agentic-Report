# Manual Database Setup Instructions

## Step 1: Open MySQL Command Line

Open Command Prompt or PowerShell and run:
```
mysql -u root
```

If it asks for password, try pressing Enter (blank) first. If that doesn't work, you'll need to provide the MySQL root password.

## Step 2: Run These SQL Commands

Copy and paste the following commands in the MySQL terminal:

```sql
DROP USER IF EXISTS 'sleepsia'@'localhost';
CREATE DATABASE IF NOT EXISTS sleepsia_reporting;
CREATE USER 'sleepsia'@'localhost' IDENTIFIED BY 'sleepsia';
GRANT ALL PRIVILEGES ON sleepsia_reporting.* TO 'sleepsia'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Step 3: Load Data from Excel

Go to the backend directory and run the loader:
```bash
cd backend
python etl/loader.py
```

Expected output:
```
[INFO] Loading data from data/final_sleepsia_report_data.xlsx
[INFO] Tables created successfully
[INFO] Data loaded into sleepsia_reporting database
```

## Step 4: Start the Backend

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Step 5: Start the Frontend (in new terminal)

```bash
cd dashboard
npm run dev
```

## Verify Everything Works

1. Open browser: http://localhost:5173
2. Check that data loads on the dashboard
3. All should work now!

---

## If You Still Get Errors

1. **"Access denied for sleepsia"**: The user wasn't created. Run the SQL commands above again.
2. **"Database sleepsia_reporting not found"**: The database wasn't created. Check the SQL commands.
3. **"Excel file not found"**: Make sure you're in the `backend` directory when running the loader.

For help, check the logs:
- Backend logs: `backend/logs/etl_*.log`
- Frontend console: Press F12 in browser
