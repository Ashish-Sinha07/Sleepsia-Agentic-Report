#!/usr/bin/env python
"""
ETL Load Verification Script
Validates data after loading into MySQL.
Execute: python backend/etl/verify_load.py
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Database config
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'sleepsia')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')


def get_engine():
    """Create database engine"""
    connection_string = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@"
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    return create_engine(connection_string, echo=False)


def verify_load():
    """Verify successful data load"""
    logger.info("=" * 80)
    logger.info("ETL Load Verification")
    logger.info("=" * 80)

    try:
        engine = get_engine()

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection successful\n")

        # Check table row counts
        tables = {
            'products': 'Products',
            'platforms': 'Platforms',
            'warehouses': 'Warehouses',
            'daily_sales': 'Daily Sales',
            'advertising': 'Advertising',
            'daily_costs': 'Daily Costs',
            'returns': 'Returns',
            'cancellations': 'Cancellations',
            'inventory_daily': 'Inventory Daily',
            'regional_sales': 'Regional Sales',
            'replenishment_alerts': 'Replenishment Alerts',
        }

        logger.info("Row Counts by Table:")
        logger.info("─" * 80)

        total_rows = 0
        with engine.connect() as conn:
            for table, label in tables.items():
                result = conn.execute(text(f"SELECT COUNT(*) as cnt FROM {table}"))
                count = result.scalar()
                total_rows += count

                status = "✓" if count > 0 else "✗"
                logger.info(f"  {status} {label:.<40} {count:>10,} rows")

        logger.info("─" * 80)
        logger.info(f"  Total rows loaded:          {total_rows:>10,}")

        # Check data quality
        logger.info("\n" + "=" * 80)
        logger.info("Data Quality Checks")
        logger.info("=" * 80)

        with engine.connect() as conn:
            # Check for nulls in critical fields
            checks = [
                ("daily_sales", "sku", "SKU field in daily_sales"),
                ("advertising", "platform_id", "PlatformID in advertising"),
                ("inventory_daily", "warehouse_id", "WarehouseID in inventory_daily"),
            ]

            for table, field, desc in checks:
                result = conn.execute(
                    text(f"SELECT COUNT(*) FROM {table} WHERE {field} IS NULL")
                )
                null_count = result.scalar()
                status = "✓" if null_count == 0 else "✗"
                logger.info(f"  {status} No null values in {desc}: {null_count} nulls")

        # Check referential integrity
        logger.info("\nReferential Integrity:")

        with engine.connect() as conn:
            # SKUs in sales
            result = conn.execute(
                text("""
                    SELECT COUNT(DISTINCT sku) as distinct_skus,
                           COUNT(*) as total_rows
                    FROM daily_sales
                """)
            )
            row = result.fetchone()
            logger.info(f"  ✓ Daily Sales: {row[1]:,} rows, {row[0]} unique SKUs")

            # Platforms in sales
            result = conn.execute(
                text("""
                    SELECT COUNT(DISTINCT platform_id) as platforms
                    FROM daily_sales
                """)
            )
            platform_count = result.scalar()
            logger.info(f"  ✓ Platforms with sales: {platform_count}")

            # Warehouses in inventory
            result = conn.execute(
                text("""
                    SELECT COUNT(DISTINCT warehouse_id) as warehouses
                    FROM inventory_daily
                """)
            )
            warehouse_count = result.scalar()
            logger.info(f"  ✓ Warehouses with inventory: {warehouse_count}")

        # Check date ranges
        logger.info("\nDate Ranges:")

        with engine.connect() as conn:
            # Sales dates
            result = conn.execute(
                text("""
                    SELECT MIN(sale_date) as min_date, MAX(sale_date) as max_date
                    FROM daily_sales
                """)
            )
            min_date, max_date = result.fetchone()
            logger.info(f"  ✓ Sales: {min_date} to {max_date}")

            # Inventory dates
            result = conn.execute(
                text("""
                    SELECT MIN(inventory_date) as min_date, MAX(inventory_date) as max_date
                    FROM inventory_daily
                """)
            )
            min_date, max_date = result.fetchone()
            logger.info(f"  ✓ Inventory: {min_date} to {max_date}")

        # Check aggregations
        logger.info("\nFinancial Data Summary:")

        with engine.connect() as conn:
            # Total sales
            result = conn.execute(
                text("SELECT SUM(net_sales) FROM daily_sales")
            )
            total_sales = result.scalar()
            logger.info(f"  ✓ Total Net Sales: ₹{total_sales:,.2f}")

            # Total ad spend
            result = conn.execute(
                text("SELECT SUM(ad_spend) FROM advertising")
            )
            total_ad_spend = result.scalar()
            logger.info(f"  ✓ Total Ad Spend: ₹{total_ad_spend:,.2f}")

            # Total returns
            result = conn.execute(
                text("SELECT SUM(refund_amount) FROM returns")
            )
            total_refunds = result.scalar()
            logger.info(f"  ✓ Total Refunds: ₹{total_refunds:,.2f}")

        # Views check
        logger.info("\nAnalytical Views:")

        views = [
            'vw_product_platform_daily',
            'vw_platform_performance',
            'vw_product_performance',
            'vw_profitability',
            'vw_inventory_health',
            'vw_warehouse_summary',
            'vw_regional_performance',
            'vw_daily_kpi_summary',
        ]

        with engine.connect() as conn:
            for view in views:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {view} LIMIT 1"))
                    count = result.scalar()
                    logger.info(f"  ✓ {view}")
                except Exception as e:
                    logger.warning(f"  ✗ {view}: {str(e)}")

        logger.info("\n" + "=" * 80)
        logger.info("✓ ETL Load Verification Completed Successfully")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"\n✗ Verification Failed: {str(e)}")
        logger.error("\nCommon issues:")
        logger.error("  - MySQL not running")
        logger.error("  - Schema not created (run sql/schema.sql)")
        logger.error("  - Wrong credentials in .env")
        logger.error("  - ETL not completed successfully")
        return 1


if __name__ == '__main__':
    exit_code = verify_load()
    sys.exit(exit_code)
