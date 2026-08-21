#!/usr/bin/env python3
"""Post-ETL Data Integrity Audit - READ-ONLY"""

from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import json

load_dotenv()

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

engine = create_engine(
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
    echo=False
)

results = {}

# 1. Row counts for all tables
print("\n[1/17] ROW COUNTS FOR ALL TABLES")
print("=" * 80)

row_counts = {}
tables = [
    'products', 'platforms', 'warehouses', 'daily_sales', 'advertising',
    'daily_costs', 'returns', 'cancellations', 'inventory_daily',
    'regional_sales', 'replenishment_alerts'
]

with engine.connect() as conn:
    for table in tables:
        result = conn.execute(text(f"SELECT COUNT(*) as cnt FROM {table}"))
        count = result.fetchone()[0]
        row_counts[table] = count
        print(f"{table:30} {count:>10,}")

results['row_counts'] = row_counts

# 2. MIN/MAX dates
print("\n[2/17] MIN/MAX DATES FOR FACT TABLES")
print("=" * 80)

date_tables = {
    'daily_sales': 'sale_date',
    'advertising': 'ad_date',
    'daily_costs': 'cost_date',
    'returns': 'return_date',
    'cancellations': 'cancellation_date',
    'inventory_daily': 'inventory_date',
    'regional_sales': 'sales_date'
}

date_ranges = {}
with engine.connect() as conn:
    for table, date_col in date_tables.items():
        result = conn.execute(text(f"SELECT MIN({date_col}), MAX({date_col}) FROM {table}"))
        min_date, max_date = result.fetchone()
        date_ranges[table] = {'min': str(min_date), 'max': str(max_date)}
        print(f"{table:30} {min_date} to {max_date}")

results['date_ranges'] = date_ranges

# 3. Distinct SKUs
print("\n[3/17] DISTINCT SKU COUNT IN PRODUCT-RELATED TABLES")
print("=" * 80)

sku_queries = {
    'daily_sales': 'SELECT COUNT(DISTINCT sku) FROM daily_sales',
    'advertising': 'SELECT COUNT(DISTINCT sku) FROM advertising',
    'daily_costs': 'SELECT COUNT(DISTINCT sku) FROM daily_costs',
    'inventory_daily': 'SELECT COUNT(DISTINCT sku) FROM inventory_daily',
    'regional_sales': 'SELECT COUNT(DISTINCT sku) FROM regional_sales',
    'products': 'SELECT COUNT(*) FROM products'
}

sku_counts = {}
with engine.connect() as conn:
    for label, query in sku_queries.items():
        result = conn.execute(text(query))
        count = result.fetchone()[0]
        sku_counts[label] = count
        print(f"{label:30} {count:>10}")

results['sku_counts'] = sku_counts

# 4. Distinct platform_ids
print("\n[4/17] DISTINCT PLATFORM_ID COUNT")
print("=" * 80)

platform_queries = {
    'daily_sales': 'SELECT COUNT(DISTINCT platform_id) FROM daily_sales',
    'advertising': 'SELECT COUNT(DISTINCT platform_id) FROM advertising',
    'daily_costs': 'SELECT COUNT(DISTINCT platform_id) FROM daily_costs',
    'returns': 'SELECT COUNT(DISTINCT platform_id) FROM returns',
    'cancellations': 'SELECT COUNT(DISTINCT platform_id) FROM cancellations',
    'platforms': 'SELECT COUNT(*) FROM platforms'
}

platform_counts = {}
with engine.connect() as conn:
    for label, query in platform_queries.items():
        result = conn.execute(text(query))
        count = result.fetchone()[0]
        platform_counts[label] = count
        print(f"{label:30} {count:>10}")

results['platform_counts'] = platform_counts

# 5. Orphan SKUs
print("\n[5/17] ORPHAN SKU CHECK")
print("=" * 80)

orphan_checks = {}
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(DISTINCT ds.sku) FROM daily_sales ds
        LEFT JOIN products p ON ds.sku = p.sku
        WHERE p.sku IS NULL
    """))
    orphan_skus = result.fetchone()[0]
    orphan_checks['orphan_skus_daily_sales'] = orphan_skus
    print(f"Orphan SKUs in daily_sales: {orphan_skus}")

# 6. Orphan platform_ids
print("\n[6/17] ORPHAN PLATFORM_ID CHECK")
print("=" * 80)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(DISTINCT ds.platform_id) FROM daily_sales ds
        LEFT JOIN platforms pl ON ds.platform_id = pl.platform_id
        WHERE pl.platform_id IS NULL
    """))
    orphan_platforms = result.fetchone()[0]
    orphan_checks['orphan_platforms_daily_sales'] = orphan_platforms
    print(f"Orphan platform_ids in daily_sales: {orphan_platforms}")

# 7. Orphan warehouse_ids
print("\n[7/17] ORPHAN WAREHOUSE_ID CHECK")
print("=" * 80)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(DISTINCT id.warehouse_id) FROM inventory_daily id
        LEFT JOIN warehouses w ON id.warehouse_id = w.warehouse_id
        WHERE w.warehouse_id IS NULL
    """))
    orphan_warehouses = result.fetchone()[0]
    orphan_checks['orphan_warehouses_inventory'] = orphan_warehouses
    print(f"Orphan warehouse_ids in inventory_daily: {orphan_warehouses}")

results['orphan_checks'] = orphan_checks

# 8. Duplicate business keys: daily_sales
print("\n[8/17] DUPLICATE BUSINESS KEY CHECK: daily_sales")
print("=" * 80)

duplicate_checks = {}
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(*) as total_rows, COUNT(DISTINCT CONCAT(sale_date, '_', platform_id, '_', sku)) as unique_keys
        FROM daily_sales
    """))
    total, unique = result.fetchone()
    duplicates = total - unique
    duplicate_checks['daily_sales'] = {'total': total, 'unique': unique, 'duplicates': duplicates}
    print(f"Total rows: {total}, Unique keys: {unique}, Duplicates: {duplicates}")

# 9. Duplicate business keys: advertising
print("\n[9/17] DUPLICATE BUSINESS KEY CHECK: advertising")
print("=" * 80)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(*) as total_rows, COUNT(DISTINCT CONCAT(ad_date, '_', platform_id, '_', sku)) as unique_keys
        FROM advertising
    """))
    total, unique = result.fetchone()
    duplicates = total - unique
    duplicate_checks['advertising'] = {'total': total, 'unique': unique, 'duplicates': duplicates}
    print(f"Total rows: {total}, Unique keys: {unique}, Duplicates: {duplicates}")

# 10. Duplicate business keys: inventory_daily
print("\n[10/17] DUPLICATE BUSINESS KEY CHECK: inventory_daily")
print("=" * 80)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(*) as total_rows, COUNT(DISTINCT CONCAT(inventory_date, '_', warehouse_id, '_', sku)) as unique_keys
        FROM inventory_daily
    """))
    total, unique = result.fetchone()
    duplicates = total - unique
    duplicate_checks['inventory_daily'] = {'total': total, 'unique': unique, 'duplicates': duplicates}
    print(f"Total rows: {total}, Unique keys: {unique}, Duplicates: {duplicates}")

results['duplicate_checks'] = duplicate_checks

# 11. NULL/blank SKU check
print("\n[11/17] NULL/BLANK SKU CHECK")
print("=" * 80)

null_checks = {}
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM daily_sales WHERE sku IS NULL OR sku = ''"))
    null_skus = result.fetchone()[0]
    null_checks['null_sku_daily_sales'] = null_skus
    print(f"NULL/blank SKUs in daily_sales: {null_skus}")

    result = conn.execute(text("SELECT COUNT(*) FROM inventory_daily WHERE sku IS NULL OR sku = ''"))
    null_skus_inv = result.fetchone()[0]
    null_checks['null_sku_inventory'] = null_skus_inv
    print(f"NULL/blank SKUs in inventory_daily: {null_skus_inv}")

# 12. NULL/blank platform check
print("\n[12/17] NULL/BLANK PLATFORM CHECK")
print("=" * 80)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM daily_sales WHERE platform_id IS NULL OR platform_id = ''"))
    null_platforms = result.fetchone()[0]
    null_checks['null_platform_daily_sales'] = null_platforms
    print(f"NULL/blank platform_ids in daily_sales: {null_platforms}")

results['null_checks'] = null_checks

# 13. Invalid dates
print("\n[13/17] INVALID DATE CHECK")
print("=" * 80)

invalid_dates = {}
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(*) FROM daily_sales
        WHERE sale_date < '2026-06-01' OR sale_date > '2026-09-01'
    """))
    invalid_date_count = result.fetchone()[0]
    invalid_dates['out_of_range_daily_sales'] = invalid_date_count
    print(f"Out-of-range dates in daily_sales: {invalid_date_count}")

results['invalid_dates'] = invalid_dates

# 14. Negative values
print("\n[14/17] NEGATIVE VALUE CHECK")
print("=" * 80)

negative_checks = {}
with engine.connect() as conn:
    checks = {
        'negative_sales': "SELECT COUNT(*) FROM daily_sales WHERE net_sales < 0",
        'negative_units': "SELECT COUNT(*) FROM daily_sales WHERE units_sold < 0",
        'negative_gross': "SELECT COUNT(*) FROM daily_sales WHERE gross_sales < 0",
        'negative_discount': "SELECT COUNT(*) FROM daily_sales WHERE discount < 0",
        'negative_cost': "SELECT COUNT(*) FROM daily_costs WHERE product_cost < 0 OR platform_fee < 0 OR shipping_cost < 0",
        'negative_ad_spend': "SELECT COUNT(*) FROM advertising WHERE ad_spend < 0",
    }

    for label, query in checks.items():
        result = conn.execute(text(query))
        count = result.fetchone()[0]
        negative_checks[label] = count
        print(f"{label:30} {count:>5}")

results['negative_checks'] = negative_checks

# 15. Test view
print("\n[15/17] VIEW TEST: vw_product_platform_daily")
print("=" * 80)

view_test = {}
with engine.connect() as conn:
    try:
        result = conn.execute(text("SELECT * FROM vw_product_platform_daily LIMIT 10"))
        rows = result.fetchall()
        view_test['status'] = 'OK'
        view_test['row_count'] = len(rows)
        print(f"View executed successfully")
        print(f"Sample rows returned: {len(rows)}")
        if rows:
            print(f"Columns in result: {len(rows[0])}")
    except Exception as e:
        view_test['status'] = 'FAIL'
        view_test['error'] = str(e)
        print(f"View test FAILED: {str(e)}")

results['view_test'] = view_test

# 16. Calculate basic totals
print("\n[16/17] BASIC TOTALS & AGGREGATIONS")
print("=" * 80)

aggregations = {}
with engine.connect() as conn:
    queries = {
        'total_gross_sales': "SELECT COALESCE(SUM(gross_sales), 0) FROM daily_sales",
        'total_net_sales': "SELECT COALESCE(SUM(net_sales), 0) FROM daily_sales",
        'total_units_sold': "SELECT COALESCE(SUM(units_sold), 0) FROM daily_sales",
        'total_ad_spend': "SELECT COALESCE(SUM(ad_spend), 0) FROM advertising",
        'total_refund_amount': "SELECT COALESCE(SUM(refund_amount), 0) FROM returns",
        'total_units_returned': "SELECT COALESCE(SUM(units_returned), 0) FROM returns",
        'total_units_cancelled': "SELECT COALESCE(SUM(units_cancelled), 0) FROM cancellations",
        'total_inventory_units': "SELECT COALESCE(SUM(closing_stock), 0) FROM inventory_daily",
    }

    for label, query in queries.items():
        result = conn.execute(text(query))
        value = result.fetchone()[0]
        aggregations[label] = float(value) if value else 0
        if label in ['total_refund_amount', 'total_ad_spend', 'total_gross_sales', 'total_net_sales']:
            print(f"{label:35} {value:>15,.2f}")
        else:
            print(f"{label:35} {value:>15,}")

results['aggregations'] = aggregations

# 17. Date range confirmation
print("\n[17/17] DATE RANGE CONFIRMATION")
print("=" * 80)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT
            MIN(sale_date) as min_date,
            MAX(sale_date) as max_date,
            DATEDIFF(MAX(sale_date), MIN(sale_date)) as days_diff
        FROM daily_sales
    """))
    min_d, max_d, days = result.fetchone()
    print(f"Min date: {min_d}")
    print(f"Max date: {max_d}")
    print(f"Days covered: {days} (Expected ~62 days)")
    results['date_coverage'] = {'min': str(min_d), 'max': str(max_d), 'days': days}

engine.dispose()

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)

# Save results
with open('etl_audit_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("\nResults saved to etl_audit_results.json")
