# ETL Quick Start Guide

Get the data loaded into MySQL in 5 minutes.

## Prerequisites

- Python 3.8+
- MySQL 8.0+ (running)
- Excel workbook: `data/final_sleepsia_report_data.xlsx`

## Step 1: Install Dependencies (2 min)

```bash
pip install -r backend/requirements.txt
```

## Step 2: Configure Database (1 min)

Create `.env` in project root:

```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:

```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sleepsia
DB_USER=root
DB_PASSWORD=your_password
```

## Step 3: Create Database & Schema (1 min)

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS sleepsia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Create schema
mysql -u root -p sleepsia < sql/schema.sql
```

## Step 4: Run ETL (1 min)

```bash
python backend/etl/run_etl.py
```

Expected output:

```
2024-01-15 14:30:45 - ETL - INFO - Starting ETL Load Process
2024-01-15 14:30:45 - ETL - INFO - Connecting to MySQL: localhost:3306/sleepsia
2024-01-15 14:30:46 - ETL - INFO - ✓ Database connection successful

2024-01-15 14:30:46 - ETL - INFO - [1/3] Loading master data...
2024-01-15 14:30:46 - ETL - INFO -   Loading Products...
2024-01-15 14:30:47 - ETL - INFO -     ✓ Loaded 8 products
2024-01-15 14:30:47 - ETL - INFO -   Loading Platforms...
2024-01-15 14:30:47 - ETL - INFO -     ✓ Loaded 5 platforms
2024-01-15 14:30:47 - ETL - INFO -   Loading Warehouses...
2024-01-15 14:30:47 - ETL - INFO -     ✓ Loaded 5 warehouses

2024-01-15 14:30:47 - ETL - INFO - [2/3] Loading transactional data...
2024-01-15 14:30:48 - ETL - INFO -   Loading Daily Sales...
2024-01-15 14:30:48 - ETL - INFO -     ✓ Loaded 744 sales records
...

2024-01-15 14:30:50 - ETL - INFO - ✓ ETL completed successfully
```

## Step 5: Verify Load (Optional)

```bash
python backend/etl/verify_load.py
```

Output:

```
================================================================================
ETL Load Verification
================================================================================
✓ Database connection successful

Row Counts by Table:
────────────────────────────────────────────────────────────────────────────────
  ✓ Products........................... 8 rows
  ✓ Platforms.......................... 5 rows
  ✓ Warehouses......................... 5 rows
  ✓ Daily Sales..................... 744 rows
  ✓ Advertising..................... 744 rows
  ✓ Daily Costs..................... 744 rows
  ✓ Returns......................... 275 rows
  ✓ Cancellations................... 142 rows
  ✓ Inventory Daily................ 930 rows
  ✓ Regional Sales................. 930 rows
  ✓ Replenishment Alerts............ 11 rows
────────────────────────────────────────────────────────────────────────────────
  Total rows loaded:           4,368

✓ ETL Load Verification Completed Successfully
```

## Troubleshooting

### Issue: "Connection refused"

MySQL is not running.

```bash
# Start MySQL
mysql.server start  # macOS
sudo systemctl start mysql  # Linux
```

### Issue: "Unknown database 'sleepsia'"

Schema not created.

```bash
mysql -u root -p sleepsia < sql/schema.sql
```

### Issue: "Access denied"

Wrong credentials in `.env`.

```bash
# Test connection
mysql -u root -p -e "SELECT 1;"
# Fix credentials in .env
```

### Issue: "Duplicate entry"

Data already loaded.

```bash
# Clear and reload
python backend/etl/run_etl.py
# Or delete specific tables before reloading
```

## What Just Happened?

The ETL loader:

1. ✅ **Extracted** 20 sheets from Excel workbook
2. ✅ **Validated** data quality and referential integrity
3. ✅ **Transformed** columns to database format
4. ✅ **Loaded** ~4,400 rows into MySQL
5. ✅ **Logged** all operations to `logs/etl_*.log`

Your data is now in MySQL with:
- ✓ 11 operational tables (sales, costs, inventory, returns, etc.)
- ✓ 8 analytical views (KPIs, profitability, warehouse health, etc.)
- ✓ All calculations ready (ROAS, ACOS, profit margins, etc.)

## Next Steps

1. **Review the data:** Check `logs/etl_*.log` for load summary
2. **Query the data:** Use SQL to explore `sleepsia` database
3. **Build API:** See `backend/` directory for FastAPI setup
4. **Create Dashboard:** See `dashboard/` directory for React frontend

## Configuration

Most users won't need to change these, but you can customize:

```python
# In backend/etl/loader.py
class Config:
    BATCH_SIZE = 1000          # Rows per insert (increase for speed)
    VALIDATE_ON_LOAD = True    # Run validation (disable for speed)
    STRICT_MODE = True         # Fail on error (False = warn only)
```

## Documentation

- **Full docs:** `backend/ETL_README.md`
- **Data profile:** `docs/data-profile.md`
- **Schema design:** `sql/schema.sql`

---

**Success!** Your data is now loaded and ready for analytics. 🎉
