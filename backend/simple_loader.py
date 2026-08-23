"""
Simple ETL Loader - Loads Excel data directly to MySQL using pandas to_sql
"""
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
import sys

load_dotenv()

# Database config
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'sleepsia_reporting')
DB_USER = os.getenv('DB_USER', 'sleepsia')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'sleepsia')

EXCEL_FILE = 'data/final_sleepsia_report_data.xlsx'

print("=" * 70)
print("SLEEPSIA - SIMPLE DATA LOADER")
print("=" * 70)

# Create engine
engine_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"\n✓ Connecting to {DB_NAME}...")
engine = create_engine(engine_url)

# Test connection
try:
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✓ Connected successfully\n")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    sys.exit(1)

# Tables to load
TABLES = {
    'products': ('Product_Master', {
        'SKU': 'sku',
        'ProductName': 'product_name',
        'ProductType': 'product_type',
        'Material': 'material',
        'IntendedUse': 'intended_use',
        'PrimaryMarket': 'primary_market',
        'SellingPrice_INR': 'selling_price',
        'ProductCost_INR': 'product_cost',
        'TargetMarginPct': 'target_margin_pct',
    }),
    'platforms': ('Platform_Master', {
        'PlatformID': 'platform_id',
        'Platform': 'platform_name',
        'SalesChannelType': 'sales_channel_type',
        'DefaultPlatformFeePct': 'default_platform_fee_pct',
    }),
    'warehouses': ('Warehouse_Master', {
        'WarehouseID': 'warehouse_id',
        'WarehouseName': 'warehouse_name',
        'Zone': 'zone',
        'City': 'city',
        'Region': 'region',
        'Latitude': 'latitude',
        'Longitude': 'longitude',
    }),
    'daily_sales': ('Daily_Sales', {
        'Date': 'date',
        'PlatformID': 'platform_id',
        'SKU': 'sku',
        'Orders': 'orders',
        'UnitsSold': 'units_sold',
        'GrossSales_INR': 'gross_sales',
        'Discount_INR': 'discount',
        'NetSales_INR': 'net_sales',
        'AdAttributedUnits': 'ad_attributed_units',
        'AdAttributedSales_INR': 'ad_attributed_sales',
    }),
    'advertising': ('Advertising', {
        'Date': 'date',
        'PlatformID': 'platform_id',
        'SKU': 'sku',
        'Impressions': 'impressions',
        'Clicks': 'clicks',
        'AttributedOrders': 'attributed_orders',
        'AttributedUnits': 'attributed_units',
        'AttributedSales_INR': 'attributed_sales',
        'AdSpend_INR': 'ad_spend',
        'CTR_Pct': 'ctr_pct',
        'ROAS': 'roas',
        'ACOS_Pct': 'acos_pct',
    }),
    'returns': ('Returns', {
        'ReturnDate': 'date',
        'PlatformID': 'platform_id',
        'SKU': 'sku',
        'UnitsReturned': 'units_returned',
        'RefundAmount_INR': 'refund_amount',
    }),
    'cancellations': ('Cancellations', {
        'CancellationDate': 'date',
        'PlatformID': 'platform_id',
        'SKU': 'sku',
        'UnitsCancelled': 'units_cancelled',
    }),
    'inventory_daily': ('Inventory_Daily', {
        'Date': 'date',
        'WarehouseID': 'warehouse_id',
        'SKU': 'sku',
        'ClosingStock': 'closing_stock',
        'AvgDailyDemand7D': 'avg_daily_demand_7d',
        'DaysOfCover': 'days_of_cover',
        'ReorderPoint': 'reorder_point',
        'RecommendedReorderQty': 'recommended_reorder_qty',
        'StockStatus': 'stock_status',
    }),
}

loaded_tables = 0
errors = []

for table_name, (sheet_name, columns_map) in TABLES.items():
    try:
        print(f"[{loaded_tables + 1}/{len(TABLES)}] Loading {table_name}...", end=" ")

        # Read Excel
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)

        # Rename columns
        df = df.rename(columns=columns_map)

        # Select only the mapped columns
        df = df[[col for col in columns_map.values() if col in df.columns]]

        # Handle dates
        date_columns = ['date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.date

        # Convert to numeric where needed
        numeric_columns = [col for col in df.columns if col in ['units_sold', 'orders', 'gross_sales', 'discount', 'net_sales', 'ad_spend', 'price', 'cost', 'impressions', 'clicks', 'units_returned', 'units_cancelled', 'closing_stock', 'inventory', 'margin_pct']]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Write to database
        df.to_sql(table_name, engine, if_exists='replace', index=False)

        print(f"✓ ({len(df)} rows)")
        loaded_tables += 1

    except Exception as e:
        print(f"✗ Error: {str(e)[:50]}")
        errors.append(f"{table_name}: {str(e)}")

print("\n" + "=" * 70)
if loaded_tables == len(TABLES):
    print(f"✓ SUCCESS! All {loaded_tables} tables loaded")
else:
    print(f"✗ {loaded_tables}/{len(TABLES)} tables loaded")
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")

print("=" * 70)
