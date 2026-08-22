# ETL Loader Documentation

## Overview

The ETL (Extract, Transform, Load) loader reads data from the Excel workbook (`data/final_sleepsia_report_data.xlsx`) and loads it into MySQL with comprehensive validation, error handling, and transaction rollback.

## Architecture

```
Excel Workbook (20 sheets)
    ↓
Extract (Read sheets with pandas)
    ↓
Validate (Check data quality & referential integrity)
    ↓
Transform (Normalize columns, convert types)
    ↓
Load (Insert into MySQL with rollback)
    ↓
Log (File + console output)
```

## Features

- **Comprehensive Validation**
  - Referential integrity (SKU, PlatformID exist in master)
  - Data type validation (numeric, date, string)
  - Duplicate detection
  - Null/empty field checks

- **Smart Data Transformation**
  - Column name normalization (CamelCase → snake_case)
  - Type conversion (strings to numbers/dates)
  - Boolean flag conversion (Yes/No → True/False)
  - Null handling (NaN → SQL NULL)

- **Transaction Management**
  - All-or-nothing loading (ACID compliance)
  - Automatic rollback on validation failure
  - Per-table transaction isolation

- **Comprehensive Logging**
  - File-based logs: `logs/etl_YYYYMMDD_HHMMSS.log`
  - Console output (INFO level)
  - File output (DEBUG level)
  - Error tracking and summary

- **Batch Processing**
  - Configurable batch size (default: 1000 rows)
  - Progress tracking for large datasets
  - Efficient memory usage

## Installation

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

Required packages:
- pandas — Data reading and manipulation
- openpyxl — Excel file handling
- SQLAlchemy — Database ORM
- PyMySQL — MySQL connector
- python-dotenv — Environment variable management

### 2. Configure Database Connection

Create a `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:

```ini
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sleepsia
DB_USER=root
DB_PASSWORD=your_password
```

**Never commit `.env` to version control.**

### 3. Create MySQL Database

```bash
# Connect to MySQL
mysql -u root -p

# Create database
CREATE DATABASE sleepsia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 4. Create Schema

```bash
mysql -u root -p sleepsia < sql/schema.sql
```

## Running the ETL

### Option 1: Direct Python Execution

```bash
cd backend/etl
python loader.py
```

### Option 2: Using Run Script

```bash
python backend/etl/run_etl.py
```

### Option 3: Import as Module

```python
from backend.etl.loader import ETLLoader, get_engine, Config

engine = get_engine()
loader = ETLLoader('data/final_sleepsia_report_data.xlsx', engine)
success = loader.load()

if success:
    print("✓ Load successful")
else:
    print("✗ Load failed - check logs/")
```

## Configuration

Edit `backend/etl/loader.py` to customize behavior:

```python
class Config:
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'sleepsia')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    # File paths
    EXCEL_FILE = 'data/final_sleepsia_report_data.xlsx'
    LOG_DIR = 'logs'

    # Validation
    BATCH_SIZE = 1000          # Rows per batch
    VALIDATE_ON_LOAD = True    # Enable validation
    STRICT_MODE = True         # Fail on validation error
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| BATCH_SIZE | int | 1000 | Rows per insert batch |
| VALIDATE_ON_LOAD | bool | True | Run validation before load |
| STRICT_MODE | bool | True | Fail on validation error (False = warn only) |

## Load Process

### Phase 1: Master Data (5 tables)
- Products (8 rows)
- Platforms (5 rows)
- Warehouses (5 rows)
- Business Config (10 rows)
- Supply Chain Config (7 rows)

**Status:** Products, Platforms, and Warehouses are required; others seed configuration.

### Phase 2: Transactional Data (5 tables)
- Daily Sales (744 rows)
- Advertising (744 rows)
- Daily Costs (744 rows)
- Returns (275 rows)
- Cancellations (142 rows)

**Validation:** References checked against Products and Platforms.

### Phase 3: Inventory Data (3 tables)
- Inventory Daily (930 rows)
- Regional Sales (930 rows)
- Replenishment Alerts (11 rows)

**Validation:** References checked against Warehouses and Products.

## Logging

### Log Locations

- **Console:** Real-time progress (INFO level)
- **File:** `logs/etl_YYYYMMDD_HHMMSS.log` (DEBUG level)

### Log Format

```
2024-01-15 14:30:45 - ETL - INFO - Starting ETL Load Process
2024-01-15 14:30:45 - ETL - INFO - Excel file: data/final_sleepsia_report_data.xlsx
2024-01-15 14:30:46 - ETL - INFO - [1/3] Loading master data...
2024-01-15 14:30:46 - ETL - INFO -   Loading Products...
2024-01-15 14:30:47 - ETL - INFO -     ✓ Loaded 8 products
```

### Common Log Messages

| Message | Meaning |
|---------|---------|
| ✓ Loaded X records | Successfully inserted |
| ⚠ Validation error | Warning; may continue if not strict |
| Transaction committed | Batch inserted successfully |
| Transaction rolled back | Error detected; all changes reverted |
| ✓ ETL completed successfully | All phases passed |
| ✗ ETL completed with errors | Some data not loaded |

## Validation Rules

### Products
- ✓ SKU is unique and non-empty
- ✓ ProductName is non-empty
- ✓ SellingPrice and ProductCost are numeric

### Platforms
- ✓ PlatformID is unique
- ✓ Platform name is unique
- ✓ DefaultPlatformFeePct is numeric

### Daily Sales
- ✓ All SKUs reference Product_Master
- ✓ All PlatformIDs reference Platform_Master
- ✓ UnitsSold and NetSales_INR are non-negative

### Advertising, Costs, Returns, Cancellations
- ✓ Foreign key references
- ✓ Date format is valid
- ✓ Numeric fields are non-negative

### Inventory
- ✓ WarehouseID references Warehouse_Master
- ✓ SKU references Product_Master
- ✓ Stock counts are non-negative

## Handling Errors

### Validation Errors

If `STRICT_MODE = True` (default), validation errors cause rollback:

```
⚠ Invalid SKUs in daily_sales: {'SLP-9999'}
✗ ETL completed with errors
```

**Resolution:**
1. Check Excel data for invalid references
2. Fix the data in Excel
3. Re-run ETL

If `STRICT_MODE = False`, validation errors are warnings:

```
⚠ Invalid SKUs in daily_sales: {'SLP-9999'}
✓ ETL completed successfully (with warnings)
```

### Database Errors

Common issues:

| Error | Cause | Resolution |
|-------|-------|-----------|
| Connection refused | MySQL not running | Start MySQL: `mysql.server start` |
| Unknown database | Schema not created | Run `sql/schema.sql` |
| Access denied | Wrong credentials | Check `.env` file |
| Duplicate key | Data already loaded | Drop tables or use `DELETE FROM table;` |
| Constraint violation | Foreign key missing | Check master data is loaded |

### Debugging

Enable SQLAlchemy debug logging:

```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
```

## Data Integrity Checks

### Referential Integrity

The loader validates:
- All SKUs in transactions reference Product_Master
- All PlatformIDs reference Platform_Master
- All WarehouseIDs reference Warehouse_Master

Example:
```python
invalid_skus = set(df_sales['SKU'].unique()) - products
if invalid_skus:
    errors.append(f"Invalid SKUs: {invalid_skus}")
```

### Business Rules

Pre-transaction validations:
- No negative quantities
- No negative financial values
- No null required fields
- Proper date formats

### Constraints in Database

Post-load constraints:
- PRIMARY KEY on all tables
- FOREIGN KEY constraints
- UNIQUE constraints on grain keys
- CHECK constraints on numeric ranges

## Performance

### Expected Load Times

| Dataset | Rows | Time |
|---------|------|------|
| Small test | 100 | < 1 sec |
| Sample data | ~2,800 | 2-5 sec |
| Full month | ~5,000 | 5-10 sec |
| Full year | ~60,000 | 30-60 sec |

### Optimization Tips

1. **Batch Size:** Increase for faster loads (default 1000)
   ```python
   Config.BATCH_SIZE = 5000
   ```

2. **Disable Validation:** Skip validation if data is trusted
   ```python
   Config.VALIDATE_ON_LOAD = False
   ```

3. **Use Local MySQL:** Avoid network latency

## Monitoring & Maintenance

### Check Load Status

```sql
SELECT table_name, TABLE_ROWS 
FROM INFORMATION_SCHEMA.TABLES 
WHERE table_schema = 'sleepsia';
```

### Reload Data

**Option 1: Clear and reload**
```bash
# Delete all data but keep schema
mysql -u root -p sleepsia < sql/clear_data.sql
python backend/etl/run_etl.py
```

**Option 2: Drop and recreate**
```bash
# Full schema recreation
mysql -u root -p sleepsia < sql/schema.sql
python backend/etl/run_etl.py
```

### Verify Data Quality

```sql
-- Check for nulls in key fields
SELECT COUNT(*) FROM daily_sales WHERE sku IS NULL;

-- Check for orphaned foreign keys
SELECT sku FROM daily_sales 
WHERE sku NOT IN (SELECT sku FROM products);

-- Check date range
SELECT MIN(sale_date), MAX(sale_date) FROM daily_sales;

-- Check row counts by platform
SELECT platform_id, COUNT(*) FROM daily_sales GROUP BY platform_id;
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pandas'"

**Solution:** Install dependencies
```bash
pip install -r backend/requirements.txt
```

### Issue: "FileNotFoundError: Excel file not found"

**Solution:** Check file path
```bash
ls -la data/final_sleepsia_report_data.xlsx
```

### Issue: "Connection refused" to MySQL

**Solution:** Start MySQL
```bash
# macOS
mysql.server start

# Linux
sudo systemctl start mysql

# Windows
net start MySQL80
```

### Issue: "Unknown database 'sleepsia'"

**Solution:** Create schema
```bash
mysql -u root -p < sql/schema.sql
```

### Issue: "Duplicate entry" for primary key

**Solution:** Clear existing data
```sql
DELETE FROM daily_sales;
DELETE FROM advertising;
DELETE FROM daily_costs;
DELETE FROM returns;
DELETE FROM cancellations;
DELETE FROM inventory_daily;
DELETE FROM regional_sales;
DELETE FROM replenishment_alerts;
```

## Advanced Usage

### Load into Different Database

```python
from backend.etl.loader import ETLLoader
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://user:pass@host/dbname')
loader = ETLLoader('data/final_sleepsia_report_data.xlsx', engine)
loader.load()
```

### Partial Load (Specific Tables)

```python
# Modify Config.EXCEL_FILE to load only certain sheets
# Or customize _load_master_data(), _load_transactions(), etc.
```

### Continuous Integration

In CI pipeline:

```bash
#!/bin/bash
set -e

# Install dependencies
pip install -r backend/requirements.txt

# Create schema
mysql -u root -p"$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS sleepsia;"
mysql -u root -p"$DB_PASSWORD" sleepsia < sql/schema.sql

# Run ETL
python backend/etl/run_etl.py
```

## Support

For issues or questions:
1. Check logs: `logs/etl_*.log`
2. Review data-profile: `docs/data-profile.md`
3. Check database schema: `sql/schema.sql`
4. Validate Excel data against the profile

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Compatibility:** Python 3.8+, MySQL 8.0+
