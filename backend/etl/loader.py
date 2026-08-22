"""
Sleepsia ETL Loader
Reads Excel workbook and loads normalized data into MySQL with validation and rollback.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import traceback

from dotenv import load_dotenv
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from contextlib import contextmanager

# Load environment variables from .env
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """ETL Configuration"""
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'sleepsia')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    # File paths
    EXCEL_FILE = os.getenv('EXCEL_FILE', 'data/final_sleepsia_report_data.xlsx')
    LOG_DIR = 'logs'
    LOG_FILE = f'logs/etl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    # Validation
    BATCH_SIZE = 1000
    VALIDATE_ON_LOAD = True
    STRICT_MODE = True  # Fail on any validation error


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_file: str) -> logging.Logger:
    """Configure logging to file and console"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger('ETL')
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


logger = setup_logging(Config.LOG_FILE)


# ============================================================================
# DATABASE CONNECTION
# ============================================================================

def get_engine() -> Engine:
    """Create SQLAlchemy engine with proper configuration"""
    connection_string = (
        f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@"
        f"{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
    )

    engine = create_engine(
        connection_string,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600
    )

    # Enable foreign key support
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        cursor.close()

    return engine


@contextmanager
def get_connection(engine: Engine):
    """Context manager for database connections with automatic rollback on error"""
    connection = engine.connect()
    transaction = connection.begin()

    try:
        yield connection
        transaction.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        transaction.rollback()
        logger.error(f"Transaction rolled back due to error: {str(e)}")
        raise
    finally:
        connection.close()


# ============================================================================
# DATA VALIDATION
# ============================================================================

class DataValidator:
    """Validates data before loading"""

    @staticmethod
    def validate_products(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate products master data"""
        errors = []

        # Check required columns
        required = ['SKU', 'ProductName', 'SellingPrice_INR', 'ProductCost_INR']
        for col in required:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")

        # Check for duplicates
        if df['SKU'].duplicated().any():
            errors.append("Duplicate SKU found in products")

        # Check data types
        for idx, row in df.iterrows():
            if not isinstance(row['SKU'], str) or not row['SKU'].strip():
                errors.append(f"Row {idx}: SKU must be non-empty string")

            try:
                float(row['SellingPrice_INR'])
            except (ValueError, TypeError):
                errors.append(f"Row {idx}: SellingPrice_INR must be numeric")

        return len(errors) == 0, errors

    @staticmethod
    def validate_platforms(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate platforms master data"""
        errors = []

        required = ['PlatformID', 'Platform', 'DefaultPlatformFeePct']
        for col in required:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")

        if df['PlatformID'].duplicated().any():
            errors.append("Duplicate PlatformID found")

        return len(errors) == 0, errors

    @staticmethod
    def validate_daily_sales(df: pd.DataFrame, products: set, platforms: set) -> Tuple[bool, List[str]]:
        """Validate daily sales transactions"""
        errors = []

        required = ['Date', 'PlatformID', 'SKU', 'UnitsSold', 'NetSales_INR']
        for col in required:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")

        # Check referential integrity
        invalid_skus = set(df['SKU'].unique()) - products
        if invalid_skus:
            errors.append(f"Invalid SKUs in daily_sales: {invalid_skus}")

        invalid_platforms = set(df['PlatformID'].unique()) - platforms
        if invalid_platforms:
            errors.append(f"Invalid PlatformIDs in daily_sales: {invalid_platforms}")

        # Check data quality
        if (df['UnitsSold'] < 0).any():
            errors.append("Negative values found in UnitsSold")

        if (df['NetSales_INR'] < 0).any():
            errors.append("Negative values found in NetSales_INR")

        return len(errors) == 0, errors

    @staticmethod
    def validate_dates(df: pd.DataFrame, date_col: str) -> Tuple[bool, List[str]]:
        """Validate date columns"""
        errors = []

        if date_col not in df.columns:
            errors.append(f"Missing date column: {date_col}")
            return False, errors

        try:
            pd.to_datetime(df[date_col])
        except Exception as e:
            errors.append(f"Invalid dates in {date_col}: {str(e)}")

        return len(errors) == 0, errors


# ============================================================================
# DATA TRANSFORMATION
# ============================================================================

class DataTransformer:
    """Transforms Excel data to database format"""

    @staticmethod
    def transform_products(df: pd.DataFrame) -> pd.DataFrame:
        """Transform products sheet"""
        df = df.copy()
        df.columns = ['sku', 'product_name', 'product_type', 'material',
                      'intended_use', 'primary_market', 'active', 'public_product_url',
                      'selling_price', 'product_cost', 'target_margin_pct']

        # Convert boolean
        df['active'] = df['active'].str.lower() == 'yes'

        # Convert currencies
        df['selling_price'] = pd.to_numeric(df['selling_price'], errors='coerce')
        df['product_cost'] = pd.to_numeric(df['product_cost'], errors='coerce')
        df['target_margin_pct'] = pd.to_numeric(df['target_margin_pct'], errors='coerce')

        # Select columns for DB
        return df[['sku', 'product_name', 'product_type', 'material',
                   'intended_use', 'primary_market', 'selling_price', 'product_cost',
                   'target_margin_pct', 'active']]

    @staticmethod
    def transform_platforms(df: pd.DataFrame) -> pd.DataFrame:
        """Transform platforms sheet"""
        df = df.copy()
        df.columns = ['platform_id', 'platform_name', 'sales_channel_type',
                      'default_platform_fee_pct', 'active']

        df['active'] = df['active'].str.lower() == 'yes'
        df['default_platform_fee_pct'] = pd.to_numeric(df['default_platform_fee_pct'], errors='coerce')

        return df[['platform_id', 'platform_name', 'sales_channel_type',
                   'default_platform_fee_pct', 'active']]

    @staticmethod
    def transform_daily_sales(df: pd.DataFrame) -> pd.DataFrame:
        """Transform daily sales sheet"""
        df = df.copy()
        df.columns = ['sale_date', 'platform_id', 'platform', 'sku', 'product_name',
                      'orders', 'units_sold', 'gross_sales', 'discount', 'net_sales',
                      'ad_attributed_units', 'ad_attributed_sales']

        df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
        df['orders'] = pd.to_numeric(df['orders'], errors='coerce').astype('Int64')
        df['units_sold'] = pd.to_numeric(df['units_sold'], errors='coerce').astype('Int64')
        df['gross_sales'] = pd.to_numeric(df['gross_sales'], errors='coerce')
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce')
        df['net_sales'] = pd.to_numeric(df['net_sales'], errors='coerce')
        df['ad_attributed_units'] = pd.to_numeric(df['ad_attributed_units'], errors='coerce').astype('Int64')
        df['ad_attributed_sales'] = pd.to_numeric(df['ad_attributed_sales'], errors='coerce')

        return df[['sale_date', 'platform_id', 'sku', 'orders', 'units_sold',
                   'gross_sales', 'discount', 'net_sales', 'ad_attributed_units',
                   'ad_attributed_sales']]

    @staticmethod
    def transform_advertising(df: pd.DataFrame) -> pd.DataFrame:
        """Transform advertising sheet"""
        df = df.copy()
        df.columns = ['ad_date', 'platform_id', 'platform', 'sku', 'product_name',
                      'impressions', 'clicks', 'attributed_orders', 'attributed_units',
                      'attributed_sales', 'ad_spend', 'ctr_pct', 'roas', 'acos_pct']

        df['ad_date'] = pd.to_datetime(df['ad_date']).dt.date
        df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce').astype('Int64')
        df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce').astype('Int64')
        df['attributed_orders'] = pd.to_numeric(df['attributed_orders'], errors='coerce').astype('Int64')
        df['attributed_units'] = pd.to_numeric(df['attributed_units'], errors='coerce').astype('Int64')
        df['attributed_sales'] = pd.to_numeric(df['attributed_sales'], errors='coerce')
        df['ad_spend'] = pd.to_numeric(df['ad_spend'], errors='coerce')

        # Note: CTR, ROAS, ACOS are derived and not stored
        return df[['ad_date', 'platform_id', 'sku', 'impressions', 'clicks',
                   'attributed_orders', 'attributed_units', 'attributed_sales', 'ad_spend']]

    @staticmethod
    def transform_daily_costs(df: pd.DataFrame) -> pd.DataFrame:
        """Transform daily costs sheet"""
        df = df.copy()
        df.columns = ['cost_date', 'platform_id', 'platform', 'sku', 'product_name',
                      'product_cost', 'platform_fee', 'shipping_cost', 'payment_fee',
                      'other_variable_cost']

        df['cost_date'] = pd.to_datetime(df['cost_date']).dt.date
        df['product_cost'] = pd.to_numeric(df['product_cost'], errors='coerce')
        df['platform_fee'] = pd.to_numeric(df['platform_fee'], errors='coerce')
        df['shipping_cost'] = pd.to_numeric(df['shipping_cost'], errors='coerce')
        df['payment_fee'] = pd.to_numeric(df['payment_fee'], errors='coerce')
        df['other_variable_cost'] = pd.to_numeric(df['other_variable_cost'], errors='coerce')

        return df[['cost_date', 'platform_id', 'sku', 'product_cost', 'platform_fee',
                   'shipping_cost', 'payment_fee', 'other_variable_cost']]

    @staticmethod
    def transform_returns(df: pd.DataFrame) -> pd.DataFrame:
        """Transform returns sheet"""
        df = df.copy()
        df.columns = ['return_id', 'return_date', 'platform_id', 'platform', 'sku',
                      'product_name', 'reason', 'units_returned', 'refund_amount', 'status']

        df['return_date'] = pd.to_datetime(df['return_date']).dt.date
        df['units_returned'] = pd.to_numeric(df['units_returned'], errors='coerce').astype('Int64')
        df['refund_amount'] = pd.to_numeric(df['refund_amount'], errors='coerce')

        # Exclude return_id - let database auto-generate it
        return df[['return_date', 'platform_id', 'sku', 'reason',
                   'units_returned', 'refund_amount', 'status']]

    @staticmethod
    def transform_cancellations(df: pd.DataFrame) -> pd.DataFrame:
        """Transform cancellations sheet"""
        df = df.copy()
        df.columns = ['cancellation_id', 'cancellation_date', 'platform_id', 'platform',
                      'sku', 'product_name', 'reason', 'units_cancelled']

        df['cancellation_date'] = pd.to_datetime(df['cancellation_date']).dt.date
        df['units_cancelled'] = pd.to_numeric(df['units_cancelled'], errors='coerce').astype('Int64')

        # Exclude cancellation_id - let database auto-generate it
        return df[['cancellation_date', 'platform_id', 'sku',
                   'reason', 'units_cancelled']]

    @staticmethod
    def transform_warehouses(df: pd.DataFrame) -> pd.DataFrame:
        """Transform warehouses sheet"""
        df = df.copy()
        df.columns = ['warehouse_id', 'region', 'zone', 'city', 'storage_capacity_units', 'status']

        df['warehouse_name'] = df['region']  # Use region as name
        df['latitude'] = None
        df['longitude'] = None
        df['storage_capacity_units'] = pd.to_numeric(df['storage_capacity_units'], errors='coerce').astype('Int64')

        return df[['warehouse_id', 'warehouse_name', 'region', 'zone', 'city',
                   'latitude', 'longitude', 'storage_capacity_units', 'status']]

    @staticmethod
    def transform_inventory_daily(df: pd.DataFrame) -> pd.DataFrame:
        """Transform inventory daily sheet"""
        df = df.copy()
        df.columns = ['inventory_date', 'warehouse_id', 'region', 'zone', 'sku',
                      'product_name', 'opening_stock', 'inbound_stock', 'demand_units',
                      'fulfilled_units', 'closing_stock', 'avg_daily_demand_7d',
                      'days_of_cover', 'reorder_point', 'recommended_reorder_qty',
                      'stockout', 'stock_status']

        df['inventory_date'] = pd.to_datetime(df['inventory_date']).dt.date
        df['opening_stock'] = pd.to_numeric(df['opening_stock'], errors='coerce').astype('Int64')
        df['inbound_stock'] = pd.to_numeric(df['inbound_stock'], errors='coerce').astype('Int64')
        df['demand_units'] = pd.to_numeric(df['demand_units'], errors='coerce').astype('Int64')
        df['fulfilled_units'] = pd.to_numeric(df['fulfilled_units'], errors='coerce').astype('Int64')
        df['closing_stock'] = pd.to_numeric(df['closing_stock'], errors='coerce').astype('Int64')
        df['avg_daily_demand_7d'] = pd.to_numeric(df['avg_daily_demand_7d'], errors='coerce').astype('Int64')
        df['days_of_cover'] = pd.to_numeric(df['days_of_cover'], errors='coerce')
        df['reorder_point'] = pd.to_numeric(df['reorder_point'], errors='coerce').astype('Int64')
        df['recommended_reorder_qty'] = pd.to_numeric(df['recommended_reorder_qty'], errors='coerce').astype('Int64')

        return df[['inventory_date', 'warehouse_id', 'sku', 'opening_stock', 'inbound_stock',
                   'demand_units', 'fulfilled_units', 'closing_stock', 'avg_daily_demand_7d',
                   'days_of_cover', 'reorder_point', 'recommended_reorder_qty',
                   'stockout', 'stock_status']]

    @staticmethod
    def transform_regional_sales(df: pd.DataFrame) -> pd.DataFrame:
        """Transform regional sales sheet"""
        df = df.copy()
        df.columns = ['sales_date', 'warehouse_id', 'region', 'zone', 'sku',
                      'product_name', 'units_sold', 'net_sales']

        df['sales_date'] = pd.to_datetime(df['sales_date']).dt.date
        df['units_sold'] = pd.to_numeric(df['units_sold'], errors='coerce').astype('Int64')
        df['net_sales'] = pd.to_numeric(df['net_sales'], errors='coerce')

        return df[['sales_date', 'warehouse_id', 'region', 'sku', 'units_sold', 'net_sales']]

    @staticmethod
    def transform_replenishment_alerts(df: pd.DataFrame) -> pd.DataFrame:
        """Transform replenishment alerts sheet"""
        df = df.copy()
        df.columns = ['alert_date', 'warehouse_id', 'region', 'sku', 'product_name',
                      'closing_stock', 'avg_daily_demand_7d', 'days_of_cover',
                      'reorder_point', 'recommended_reorder_qty', 'stock_status',
                      'priority', 'recommended_action']

        df['alert_date'] = pd.to_datetime(df['alert_date']).dt.date
        df['closing_stock'] = pd.to_numeric(df['closing_stock'], errors='coerce').astype('Int64')
        df['avg_daily_demand_7d'] = pd.to_numeric(df['avg_daily_demand_7d'], errors='coerce').astype('Int64')
        df['days_of_cover'] = pd.to_numeric(df['days_of_cover'], errors='coerce')
        df['reorder_point'] = pd.to_numeric(df['reorder_point'], errors='coerce').astype('Int64')
        df['recommended_reorder_qty'] = pd.to_numeric(df['recommended_reorder_qty'], errors='coerce').astype('Int64')

        return df[['alert_date', 'warehouse_id', 'region', 'sku', 'closing_stock',
                   'avg_daily_demand_7d', 'days_of_cover', 'reorder_point',
                   'recommended_reorder_qty', 'stock_status', 'priority', 'recommended_action']]


# ============================================================================
# ETL LOADER
# ============================================================================

class ETLLoader:
    """Main ETL loader class"""

    def __init__(self, excel_file: str, engine: Engine):
        self.excel_file = excel_file
        self.engine = engine
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.stats = {
            'products': 0,
            'platforms': 0,
            'daily_sales': 0,
            'advertising': 0,
            'daily_costs': 0,
            'returns': 0,
            'cancellations': 0,
            'warehouses': 0,
            'inventory_daily': 0,
            'regional_sales': 0,
            'replenishment_alerts': 0,
            'errors': []
        }

    def load(self) -> bool:
        """Execute full ETL pipeline"""
        logger.info("=" * 80)
        logger.info("Starting ETL Load Process")
        logger.info(f"Excel file: {self.excel_file}")
        logger.info("=" * 80)

        try:
            # 1. Load and validate reference data
            logger.info("\n[1/3] Loading master data...")
            if not self._load_master_data():
                return False

            # 2. Load transactional data
            logger.info("\n[2/3] Loading transactional data...")
            if not self._load_transactions():
                return False

            # 3. Load inventory data
            logger.info("\n[3/3] Loading inventory data...")
            if not self._load_inventory():
                return False

            logger.info("\n" + "=" * 80)
            logger.info("ETL Load completed successfully!")
            logger.info("=" * 80)
            self._print_summary()

            return True

        except Exception as e:
            logger.error(f"Fatal error during ETL: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def _load_master_data(self) -> bool:
        """Load reference data (products, platforms, warehouses)"""
        try:
            with get_connection(self.engine) as conn:
                # Products
                logger.info("  Loading Products...")
                df_products = pd.read_excel(self.excel_file, sheet_name='Product_Master')
                valid, errors = self.validator.validate_products(df_products)
                if not valid:
                    self._log_errors(errors)
                    if Config.STRICT_MODE:
                        return False

                df_products = self.transformer.transform_products(df_products)
                self._insert_data(conn, 'products', df_products, if_exists='replace')
                self.stats['products'] = len(df_products)
                logger.info(f"    [OK] Loaded {len(df_products)} products")

                # Platforms
                logger.info("  Loading Platforms...")
                df_platforms = pd.read_excel(self.excel_file, sheet_name='Platform_Master')
                valid, errors = self.validator.validate_platforms(df_platforms)
                if not valid:
                    self._log_errors(errors)
                    if Config.STRICT_MODE:
                        return False

                df_platforms = self.transformer.transform_platforms(df_platforms)
                self._insert_data(conn, 'platforms', df_platforms, if_exists='replace')
                self.stats['platforms'] = len(df_platforms)
                logger.info(f"    [OK] Loaded {len(df_platforms)} platforms")

                # Warehouses
                logger.info("  Loading Warehouses...")
                df_warehouses = pd.read_excel(self.excel_file, sheet_name='Warehouse_Master')
                df_warehouses = self.transformer.transform_warehouses(df_warehouses)
                self._insert_data(conn, 'warehouses', df_warehouses, if_exists='replace')
                self.stats['warehouses'] = len(df_warehouses)
                logger.info(f"    [OK] Loaded {len(df_warehouses)} warehouses")

            return True

        except Exception as e:
            logger.error(f"Error loading master data: {str(e)}")
            self.stats['errors'].append(str(e))
            return False

    def _load_transactions(self) -> bool:
        """Load transactional data"""
        try:
            # Get reference data for validation
            df_products = pd.read_excel(self.excel_file, sheet_name='Product_Master')
            products = set(df_products['SKU'].values)

            df_platforms = pd.read_excel(self.excel_file, sheet_name='Platform_Master')
            platforms = set(df_platforms['PlatformID'].values)

            with get_connection(self.engine) as conn:
                # Daily Sales
                logger.info("  Loading Daily Sales...")
                df_sales = pd.read_excel(self.excel_file, sheet_name='Daily_Sales')
                valid, errors = self.validator.validate_daily_sales(df_sales, products, platforms)
                if not valid:
                    self._log_errors(errors)
                    if Config.STRICT_MODE:
                        return False

                df_sales = self.transformer.transform_daily_sales(df_sales)
                self._insert_data(conn, 'daily_sales', df_sales)
                self.stats['daily_sales'] = len(df_sales)
                logger.info(f"    [OK] Loaded {len(df_sales)} sales records")

                # Advertising
                logger.info("  Loading Advertising...")
                df_ads = pd.read_excel(self.excel_file, sheet_name='Advertising')
                df_ads = self.transformer.transform_advertising(df_ads)
                self._insert_data(conn, 'advertising', df_ads)
                self.stats['advertising'] = len(df_ads)
                logger.info(f"    [OK] Loaded {len(df_ads)} advertising records")

                # Daily Costs
                logger.info("  Loading Daily Costs...")
                df_costs = pd.read_excel(self.excel_file, sheet_name='Daily_Costs')
                df_costs = self.transformer.transform_daily_costs(df_costs)
                self._insert_data(conn, 'daily_costs', df_costs)
                self.stats['daily_costs'] = len(df_costs)
                logger.info(f"    [OK] Loaded {len(df_costs)} cost records")

                # Returns
                logger.info("  Loading Returns...")
                df_returns = pd.read_excel(self.excel_file, sheet_name='Returns')
                df_returns = self.transformer.transform_returns(df_returns)
                self._insert_data(conn, 'returns', df_returns)
                self.stats['returns'] = len(df_returns)
                logger.info(f"    [OK] Loaded {len(df_returns)} return records")

                # Cancellations
                logger.info("  Loading Cancellations...")
                df_cancels = pd.read_excel(self.excel_file, sheet_name='Cancellations')
                df_cancels = self.transformer.transform_cancellations(df_cancels)
                self._insert_data(conn, 'cancellations', df_cancels)
                self.stats['cancellations'] = len(df_cancels)
                logger.info(f"    [OK] Loaded {len(df_cancels)} cancellation records")

            return True

        except Exception as e:
            logger.error(f"Error loading transactions: {str(e)}")
            self.stats['errors'].append(str(e))
            return False

    def _load_inventory(self) -> bool:
        """Load inventory and regional data"""
        try:
            with get_connection(self.engine) as conn:
                # Inventory Daily
                logger.info("  Loading Inventory Daily...")
                df_inventory = pd.read_excel(self.excel_file, sheet_name='Inventory_Daily')
                df_inventory = self.transformer.transform_inventory_daily(df_inventory)
                self._insert_data(conn, 'inventory_daily', df_inventory)
                self.stats['inventory_daily'] = len(df_inventory)
                logger.info(f"    [OK] Loaded {len(df_inventory)} inventory records")

                # Regional Sales
                logger.info("  Loading Regional Sales...")
                df_regional = pd.read_excel(self.excel_file, sheet_name='Regional_Sales')
                df_regional = self.transformer.transform_regional_sales(df_regional)
                self._insert_data(conn, 'regional_sales', df_regional)
                self.stats['regional_sales'] = len(df_regional)
                logger.info(f"    [OK] Loaded {len(df_regional)} regional sales records")

                # Replenishment Alerts
                logger.info("  Loading Replenishment Alerts...")
                df_alerts = pd.read_excel(self.excel_file, sheet_name='Replenishment_Alerts')
                df_alerts = self.transformer.transform_replenishment_alerts(df_alerts)
                self._insert_data(conn, 'replenishment_alerts', df_alerts)
                self.stats['replenishment_alerts'] = len(df_alerts)
                logger.info(f"    [OK] Loaded {len(df_alerts)} alert records")

            return True

        except Exception as e:
            logger.error(f"Error loading inventory: {str(e)}")
            self.stats['errors'].append(str(e))
            return False

    def _insert_data(self, connection, table: str, df: pd.DataFrame,
                    if_exists: str = 'append', index: bool = False):
        """Insert data into table using SQLAlchemy"""
        # Convert NaN to None for NULL handling
        df = df.where(pd.notna(df), None)

        # Prepare data for insertion
        total_rows = len(df)
        batch_size = Config.BATCH_SIZE

        # Convert dataframe to list of dicts for batch insertion
        records = df.to_dict(orient='records')

        for i in range(0, total_rows, batch_size):
            batch = records[i:i + batch_size]

            # Use SQLAlchemy's insert with values
            # For 'replace' mode, use MySQL REPLACE syntax
            from sqlalchemy import MetaData, Table

            metadata = MetaData()
            tbl = Table(table, metadata, autoload_with=self.engine)

            if if_exists == 'replace':
                # Use REPLACE INTO for dimension tables (upsert behavior)
                stmt = text(f"""
                    REPLACE INTO {table}
                    ({', '.join([f'`{col}`' for col in df.columns])})
                    VALUES
                    {', '.join([
                        f"({', '.join([f':{col}_{j}' for col in df.columns])})"
                        for j in range(len(batch))
                    ])}
                """)
                # Build parameters dict
                params = {}
                for j, row in enumerate(batch):
                    for col, val in row.items():
                        params[f'{col}_{j}'] = val
                connection.execute(stmt, params)
            else:
                # Regular INSERT for fact tables
                stmt = tbl.insert().values(batch)
                connection.execute(stmt)

            if i > 0:  # Log progress for larger batches
                logger.debug(f"    Batch {i // batch_size}: {min(i + batch_size, total_rows)}/{total_rows} rows")

    def _log_errors(self, errors: List[str]):
        """Log validation errors"""
        for error in errors:
            logger.warning(f"    ⚠ {error}")
            self.stats['errors'].append(error)

    def _print_summary(self):
        """Print load summary"""
        logger.info("\nLoad Summary:")
        logger.info(f"  Products:              {self.stats['products']:,}")
        logger.info(f"  Platforms:             {self.stats['platforms']:,}")
        logger.info(f"  Warehouses:            {self.stats['warehouses']:,}")
        logger.info(f"  Daily Sales:           {self.stats['daily_sales']:,}")
        logger.info(f"  Advertising Records:   {self.stats['advertising']:,}")
        logger.info(f"  Daily Costs:           {self.stats['daily_costs']:,}")
        logger.info(f"  Returns:               {self.stats['returns']:,}")
        logger.info(f"  Cancellations:         {self.stats['cancellations']:,}")
        logger.info(f"  Inventory Daily:       {self.stats['inventory_daily']:,}")
        logger.info(f"  Regional Sales:        {self.stats['regional_sales']:,}")
        logger.info(f"  Replenishment Alerts:  {self.stats['replenishment_alerts']:,}")

        total_records = sum(v for k, v in self.stats.items() if k != 'errors')
        logger.info(f"  {'-' * 40}")
        logger.info(f"  Total Records Loaded:  {total_records:,}")

        if self.stats['errors']:
            logger.warning(f"\n  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5
                logger.warning(f"    - {error}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    logger.info(f"Log file: {Config.LOG_FILE}")

    try:
        # Verify Excel file exists
        if not os.path.exists(Config.EXCEL_FILE):
            logger.error(f"Excel file not found: {Config.EXCEL_FILE}")
            return 1

        # Create engine
        logger.info(f"Connecting to MySQL: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
        engine = get_engine()

        # Test connection
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("[OK] Database connection successful")
        except Exception as e:
            logger.error(f"[FAIL] Database connection failed: {str(e)}")
            logger.error("Ensure MySQL is running and credentials are correct in .env")
            return 1

        # Run ETL
        loader = ETLLoader(Config.EXCEL_FILE, engine)
        success = loader.load()

        if success:
            logger.info(f"\n[OK] ETL completed successfully")
            logger.info(f"Log file: {Config.LOG_FILE}")
            return 0
        else:
            logger.error(f"\n[FAIL] ETL completed with errors")
            logger.error(f"Log file: {Config.LOG_FILE}")
            return 1

    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
