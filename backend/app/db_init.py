"""Database initialization module.

Handles schema creation and sample data loading.
"""

import logging
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from pathlib import Path

logger = logging.getLogger(__name__)


def init_database(engine) -> bool:
    """Initialize database schema and load sample data.

    Args:
        engine: SQLAlchemy engine

    Returns:
        True if initialization successful, False otherwise
    """
    try:
        # Check if tables exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if not existing_tables:
            logger.info("Creating database schema...")
            _create_schema(engine)
            logger.info("Schema created successfully")

            # Load sample data
            logger.info("Loading sample data...")
            with engine.connect() as conn:
                _load_sample_data(conn)
            logger.info("Sample data loaded successfully")
            return True
        else:
            logger.info(f"Database already initialized with {len(existing_tables)} tables")
            return True

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        return False


def _create_schema(engine):
    """Create database schema from schema.sql file."""
    schema_path = Path(__file__).parent.parent.parent / "sql" / "schema.sql"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Split by ';' and execute each statement
    statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

    with engine.connect() as conn:
        for stmt in statements:
            if stmt:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    # Some statements might fail (e.g., DROP IF EXISTS), so just log
                    logger.debug(f"SQL statement execution note: {str(e)}")
        conn.commit()


def _load_sample_data(conn):
    """Load sample data for testing."""
    from datetime import datetime, timedelta, date

    # Insert sample platforms
    platforms = [
        ("AMZ", "Amazon", "Marketplace", 16.00),
        ("BLK", "Blinkit", "Quick Commerce", 18.00),
        ("FLP", "Flipkart", "Marketplace", 15.00),
        ("MTR", "Myntra", "Marketplace", 17.00),
        ("JMT", "JioMart", "Quick Commerce", 16.00),
    ]

    for platform_id, name, channel, fee in platforms:
        conn.execute(text("""
            INSERT IGNORE INTO platforms (platform_id, platform_name, sales_channel_type, default_platform_fee_pct)
            VALUES (:pid, :name, :channel, :fee)
        """), {"pid": platform_id, "name": name, "channel": channel, "fee": fee})

    # Insert sample warehouses
    warehouses = [
        ("WH-NCR", "Delhi NCR Warehouse", "Delhi NCR", "North", "Gurugram", 28.4595, 77.0266),
        ("WH-JPR", "Jaipur Warehouse", "Jaipur", "North", "Jaipur", 26.9124, 75.7873),
        ("WH-MUM", "Mumbai Warehouse", "Mumbai", "West", "Mumbai", 19.0760, 72.8777),
        ("WH-BLR", "Bengaluru Warehouse", "Bengaluru", "South", "Bengaluru", 12.9716, 77.5946),
        ("WH-HYD", "Hyderabad Warehouse", "Hyderabad", "South", "Hyderabad", 17.3850, 78.4867),
    ]

    for wid, name, region, zone, city, lat, lon in warehouses:
        conn.execute(text("""
            INSERT IGNORE INTO warehouses (warehouse_id, warehouse_name, region, zone, city, latitude, longitude, storage_capacity_units)
            VALUES (:wid, :name, :region, :zone, :city, :lat, :lon, 5000)
        """), {"wid": wid, "name": name, "region": region, "zone": zone, "city": city, "lat": lat, "lon": lon})

    # Insert sample products
    products = [
        ("SKU001", "Memory Foam Pillow", "Pillow", "Memory Foam", "Sleep", "Domestic", 1999, 800, 40),
        ("SKU002", "Cooling Gel Pillow", "Pillow", "Gel", "Sleep", "Domestic", 2499, 950, 40),
        ("SKU003", "Orthopedic Mattress", "Mattress", "Memory Foam", "Sleep", "Domestic", 14999, 6000, 40),
        ("SKU004", "Bamboo Bedsheet", "Bedsheet", "Bamboo", "Sleep", "Domestic", 1299, 400, 40),
        ("SKU005", "Comforter Set", "Comforter", "Cotton", "Sleep", "Domestic", 3499, 1400, 40),
    ]

    for sku, name, ptype, material, use, market, price, cost, margin in products:
        conn.execute(text("""
            INSERT IGNORE INTO products (sku, product_name, product_type, material, intended_use, primary_market, selling_price, product_cost, target_margin_pct)
            VALUES (:sku, :name, :type, :material, :use, :market, :price, :cost, :margin)
        """), {
            "sku": sku, "name": name, "type": ptype, "material": material,
            "use": use, "market": market, "price": price, "cost": cost, "margin": margin
        })

    # Insert sample daily sales for last 30 days
    base_date = date.today() - timedelta(days=30)
    for i in range(30):
        current_date = base_date + timedelta(days=i)

        for platform_id in ["AMZ", "BLK", "FLP"]:
            for sku in ["SKU001", "SKU002", "SKU003"]:
                orders = 10 + i % 5
                units = 15 + i % 8
                gross = 1999 * units + 500 * (i % 2)
                discount = gross * 0.1
                net = gross - discount

                conn.execute(text("""
                    INSERT IGNORE INTO daily_sales (sale_date, platform_id, sku, orders, units_sold, gross_sales, discount, net_sales, ad_attributed_units, ad_attributed_sales)
                    VALUES (:date, :pid, :sku, :orders, :units, :gross, :discount, :net, :ad_units, :ad_sales)
                """), {
                    "date": current_date,
                    "pid": platform_id,
                    "sku": sku,
                    "orders": orders,
                    "units": units,
                    "gross": gross,
                    "discount": discount,
                    "net": net,
                    "ad_units": units // 2,
                    "ad_sales": net * 0.3,
                })

        # Insert advertising data
        for platform_id in ["AMZ", "BLK", "FLP"]:
            for sku in ["SKU001", "SKU002", "SKU003"]:
                impressions = 5000 + i * 100
                clicks = 250 + i * 10
                orders = 8 + i % 4
                units = 12 + i % 6
                sales = 5000 + i * 100
                spend = 2000 + i * 50

                conn.execute(text("""
                    INSERT IGNORE INTO advertising (ad_date, platform_id, sku, impressions, clicks, attributed_orders, attributed_units, attributed_sales, ad_spend)
                    VALUES (:date, :pid, :sku, :impressions, :clicks, :orders, :units, :sales, :spend)
                """), {
                    "date": current_date,
                    "pid": platform_id,
                    "sku": sku,
                    "impressions": impressions,
                    "clicks": clicks,
                    "orders": orders,
                    "units": units,
                    "sales": sales,
                    "spend": spend,
                })

        # Insert costs data
        for platform_id in ["AMZ", "BLK", "FLP"]:
            for sku in ["SKU001", "SKU002", "SKU003"]:
                product_cost = 800 if sku == "SKU001" else (950 if sku == "SKU002" else 6000)
                platform_fee = 1200 + i * 10
                shipping = 300 + i * 5
                payment_fee = 150 + i * 2

                conn.execute(text("""
                    INSERT IGNORE INTO daily_costs (cost_date, platform_id, sku, product_cost, platform_fee, shipping_cost, payment_fee, other_variable_cost)
                    VALUES (:date, :pid, :sku, :pcost, :pfee, :ship, :payment, :other)
                """), {
                    "date": current_date,
                    "pid": platform_id,
                    "sku": sku,
                    "pcost": product_cost,
                    "pfee": platform_fee,
                    "ship": shipping,
                    "payment": payment_fee,
                    "other": 100,
                })

    conn.commit()
    logger.info("Sample data insertion completed")
