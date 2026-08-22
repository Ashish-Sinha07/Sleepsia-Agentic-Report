#!/usr/bin/env python3
"""
ETL Environment Verification Test
Tests Python environment, dependencies, and MySQL connection
"""

import os
import sys
from pathlib import Path

print("=" * 80)
print("ETL ENVIRONMENT VERIFICATION TEST")
print("=" * 80)

# ============================================================================
# 1. CHECK PYTHON VERSION
# ============================================================================

print("\n[1/5] Checking Python version...")
py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
print(f"  Python version: {py_version}")
if sys.version_info >= (3, 8):
    print("  [PASS] Python 3.8+ detected")
else:
    print("  [FAIL] ERROR: Python 3.8+ required")
    sys.exit(1)

# ============================================================================
# 2. CHECK REQUIRED PACKAGES
# ============================================================================

print("\n[2/5] Checking required packages...")

required_packages = {
    'pandas': 'pandas',
    'numpy': 'numpy',
    'openpyxl': 'openpyxl',
    'sqlalchemy': 'sqlalchemy',
    'pymysql': 'PyMySQL',
    'dotenv': 'python-dotenv',
}

missing_packages = []

for import_name, package_name in required_packages.items():
    try:
        __import__(import_name)
        print(f"  [OK] {package_name:25} installed")
    except ImportError:
        print(f"  [XX] {package_name:25} MISSING")
        missing_packages.append(package_name)

if missing_packages:
    print(f"\n  [FAIL] Missing packages: {', '.join(missing_packages)}")
    print(f"  Install with: pip install {' '.join(missing_packages)}")
    sys.exit(1)

# ============================================================================
# 3. CHECK .ENV FILE
# ============================================================================

print("\n[3/5] Checking .env configuration...")

from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    print(f"  [OK] .env file found: {env_path}")
    load_dotenv()
else:
    print(f"  [FAIL] ERROR: .env file not found at {env_path}")
    sys.exit(1)

# Check required environment variables
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
excel_file = os.getenv('EXCEL_FILE')

missing_vars = []

if not db_host:
    missing_vars.append('DB_HOST')
    print(f"  [XX] DB_HOST not set")
else:
    print(f"  [OK] DB_HOST={db_host}")

if not db_port:
    missing_vars.append('DB_PORT')
    print(f"  [XX] DB_PORT not set")
else:
    print(f"  [OK] DB_PORT={db_port}")

if not db_name:
    missing_vars.append('DB_NAME')
    print(f"  [XX] DB_NAME not set")
else:
    print(f"  [OK] DB_NAME={db_name}")

if not db_user:
    missing_vars.append('DB_USER')
    print(f"  [XX] DB_USER not set")
else:
    print(f"  [OK] DB_USER={db_user}")

if not db_password:
    missing_vars.append('DB_PASSWORD')
    print(f"  [XX] DB_PASSWORD not set")
else:
    print(f"  [OK] DB_PASSWORD=*** (hidden)")

if not excel_file:
    missing_vars.append('EXCEL_FILE')
    print(f"  [XX] EXCEL_FILE not set")
else:
    print(f"  [OK] EXCEL_FILE={excel_file}")

if missing_vars:
    print(f"\n  [FAIL] Missing environment variables: {', '.join(missing_vars)}")
    print(f"  Configure these in .env file")
    sys.exit(1)

# ============================================================================
# 4. CHECK EXCEL FILE EXISTS
# ============================================================================

print("\n[4/5] Checking Excel file...")

excel_path = Path(excel_file)
if excel_path.exists():
    file_size = excel_path.stat().st_size / 1024 / 1024
    print(f"  [OK] Excel file found: {excel_path}")
    print(f"       Size: {file_size:.2f} MB")
else:
    print(f"  [FAIL] ERROR: Excel file not found: {excel_path}")
    sys.exit(1)

# ============================================================================
# 5. TEST MYSQL CONNECTION
# ============================================================================

print("\n[5/5] Testing MySQL connection...")

try:
    from sqlalchemy import create_engine, text

    connection_string = (
        f"mysql+pymysql://{db_user}:***@{db_host}:{db_port}/{db_name}"
    )
    print(f"  Connection string: {connection_string}")

    # Create engine
    engine = create_engine(
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
        echo=False,
        pool_size=5,
        pool_recycle=3600
    )

    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        result.fetchone()

    print(f"  [OK] MySQL connection successful")
    print(f"       Host: {db_host}:{db_port}")
    print(f"       Database: {db_name}")
    print(f"       User: {db_user}")

    engine.dispose()

except Exception as e:
    print(f"  [FAIL] MySQL connection FAILED")
    print(f"         Error: {str(e)}")
    print(f"\n  Troubleshooting:")
    print(f"    1. Ensure MySQL is running")
    print(f"    2. Check DB_HOST={db_host}, DB_PORT={db_port}")
    print(f"    3. Check DB_USER={db_user} and DB_PASSWORD")
    print(f"    4. Verify database '{db_name}' exists")
    sys.exit(1)

# ============================================================================
# SUCCESS
# ============================================================================

print("\n" + "=" * 80)
print("ALL CHECKS PASSED")
print("=" * 80)
print("\nStatus Summary:")
print("  Python:           [PASS]")
print("  Dependencies:     [PASS]")
print("  Configuration:    [PASS]")
print("  Excel file:       [PASS]")
print("  MySQL connection: [PASS]")
print("\nReady for ETL execution.")
print("=" * 80)

sys.exit(0)
