#!/usr/bin/env python
"""
ETL Unit Tests
Test data validation, transformation, and basic loading.
Execute: python -m pytest backend/etl/test_etl.py -v
"""

import unittest
import pandas as pd
from datetime import date
from loader import DataValidator, DataTransformer


class TestDataValidator(unittest.TestCase):
    """Test validation functions"""

    def test_validate_products_success(self):
        """Valid products should pass"""
        df = pd.DataFrame({
            'SKU': ['SKU-001', 'SKU-002'],
            'ProductName': ['Product A', 'Product B'],
            'SellingPrice_INR': [1000, 2000],
            'ProductCost_INR': [500, 1000]
        })

        validator = DataValidator()
        valid, errors = validator.validate_products(df)

        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_validate_products_missing_column(self):
        """Missing required column should fail"""
        df = pd.DataFrame({
            'SKU': ['SKU-001'],
            'ProductName': ['Product A']
            # Missing SellingPrice_INR and ProductCost_INR
        })

        validator = DataValidator()
        valid, errors = validator.validate_products(df)

        self.assertFalse(valid)
        self.assertTrue(any('Missing required column' in e for e in errors))

    def test_validate_products_duplicate_sku(self):
        """Duplicate SKU should fail"""
        df = pd.DataFrame({
            'SKU': ['SKU-001', 'SKU-001'],
            'ProductName': ['Product A', 'Product B'],
            'SellingPrice_INR': [1000, 1000],
            'ProductCost_INR': [500, 500]
        })

        validator = DataValidator()
        valid, errors = validator.validate_products(df)

        self.assertFalse(valid)
        self.assertTrue(any('Duplicate SKU' in e for e in errors))

    def test_validate_platforms_success(self):
        """Valid platforms should pass"""
        df = pd.DataFrame({
            'PlatformID': ['AMZ', 'FLP'],
            'Platform': ['Amazon', 'Flipkart'],
            'DefaultPlatformFeePct': [15.0, 16.0]
        })

        validator = DataValidator()
        valid, errors = validator.validate_platforms(df)

        self.assertTrue(valid)

    def test_validate_platforms_duplicate_id(self):
        """Duplicate PlatformID should fail"""
        df = pd.DataFrame({
            'PlatformID': ['AMZ', 'AMZ'],
            'Platform': ['Amazon', 'Amazon2'],
            'DefaultPlatformFeePct': [15.0, 16.0]
        })

        validator = DataValidator()
        valid, errors = validator.validate_platforms(df)

        self.assertFalse(valid)

    def test_validate_daily_sales_invalid_sku(self):
        """Invalid SKU should fail"""
        df = pd.DataFrame({
            'Date': pd.to_datetime(['2024-01-01']),
            'PlatformID': ['AMZ'],
            'SKU': ['INVALID-SKU'],
            'UnitsSold': [10],
            'NetSales_INR': [15000]
        })

        validator = DataValidator()
        valid, errors = validator.validate_daily_sales(
            df,
            products={'SKU-001', 'SKU-002'},
            platforms={'AMZ', 'FLP'}
        )

        self.assertFalse(valid)
        self.assertTrue(any('Invalid SKUs' in e for e in errors))

    def test_validate_daily_sales_negative_units(self):
        """Negative units should fail"""
        df = pd.DataFrame({
            'Date': pd.to_datetime(['2024-01-01']),
            'PlatformID': ['AMZ'],
            'SKU': ['SKU-001'],
            'UnitsSold': [-10],
            'NetSales_INR': [15000]
        })

        validator = DataValidator()
        valid, errors = validator.validate_daily_sales(
            df,
            products={'SKU-001'},
            platforms={'AMZ'}
        )

        self.assertFalse(valid)
        self.assertTrue(any('Negative values' in e for e in errors))

    def test_validate_dates_success(self):
        """Valid dates should pass"""
        df = pd.DataFrame({
            'Date': pd.to_datetime(['2024-01-01', '2024-01-02'])
        })

        validator = DataValidator()
        valid, errors = validator.validate_dates(df, 'Date')

        self.assertTrue(valid)

    def test_validate_dates_missing_column(self):
        """Missing date column should fail"""
        df = pd.DataFrame({
            'Value': [1, 2]
        })

        validator = DataValidator()
        valid, errors = validator.validate_dates(df, 'Date')

        self.assertFalse(valid)


class TestDataTransformer(unittest.TestCase):
    """Test transformation functions"""

    def test_transform_products(self):
        """Products should be transformed correctly"""
        df = pd.DataFrame({
            'SKU': ['SKU-001'],
            'ProductName': ['Product A'],
            'ProductType': ['Type A'],
            'Material': ['Material A'],
            'IntendedUse': ['Use A'],
            'PrimaryMarket': ['India'],
            'Active': ['Yes'],
            'PublicProductURL': ['http://example.com'],
            'SellingPrice_INR': [1000],
            'ProductCost_INR': [500],
            'TargetMarginPct': [0.50]
        })

        transformer = DataTransformer()
        result = transformer.transform_products(df)

        self.assertEqual(result['sku'].iloc[0], 'SKU-001')
        self.assertEqual(result['product_name'].iloc[0], 'Product A')
        self.assertTrue(result['active'].iloc[0])
        self.assertEqual(result['selling_price'].iloc[0], 1000)

    def test_transform_platforms(self):
        """Platforms should be transformed correctly"""
        df = pd.DataFrame({
            'PlatformID': ['AMZ'],
            'Platform': ['Amazon'],
            'SalesChannelType': ['Marketplace'],
            'DefaultPlatformFeePct': [15.0],
            'Active': ['Yes']
        })

        transformer = DataTransformer()
        result = transformer.transform_platforms(df)

        self.assertEqual(result['platform_id'].iloc[0], 'AMZ')
        self.assertEqual(result['platform_name'].iloc[0], 'Amazon')
        self.assertTrue(result['active'].iloc[0])

    def test_transform_daily_sales(self):
        """Daily sales should be transformed correctly"""
        df = pd.DataFrame({
            'Date': pd.to_datetime(['2024-01-01']),
            'PlatformID': ['AMZ'],
            'Platform': ['Amazon'],
            'SKU': ['SKU-001'],
            'ProductName': ['Product A'],
            'Orders': [5],
            'UnitsSold': [10],
            'GrossSales_INR': [15000],
            'Discount_INR': [1500],
            'NetSales_INR': [13500],
            'AdAttributedUnits': [5],
            'AdAttributedSales_INR': [6750]
        })

        transformer = DataTransformer()
        result = transformer.transform_daily_sales(df)

        self.assertEqual(result['sale_date'].iloc[0], date(2024, 1, 1))
        self.assertEqual(result['platform_id'].iloc[0], 'AMZ')
        self.assertEqual(result['units_sold'].iloc[0], 10)
        self.assertEqual(result['net_sales'].iloc[0], 13500)

    def test_transform_advertising(self):
        """Advertising should be transformed correctly"""
        df = pd.DataFrame({
            'Date': pd.to_datetime(['2024-01-01']),
            'PlatformID': ['AMZ'],
            'Platform': ['Amazon'],
            'SKU': ['SKU-001'],
            'ProductName': ['Product A'],
            'Impressions': [1000],
            'Clicks': [50],
            'AttributedOrders': [5],
            'AttributedUnits': [10],
            'AttributedSales_INR': [15000],
            'AdSpend_INR': [2000],
            'CTR_Pct': [5.0],
            'ROAS': [7.5],
            'ACOS_Pct': [13.33]
        })

        transformer = DataTransformer()
        result = transformer.transform_advertising(df)

        self.assertEqual(result['ad_date'].iloc[0], date(2024, 1, 1))
        self.assertEqual(result['impressions'].iloc[0], 1000)
        self.assertEqual(result['ad_spend'].iloc[0], 2000)

    def test_transform_inventory_daily(self):
        """Inventory should be transformed correctly"""
        df = pd.DataFrame({
            'Date': pd.to_datetime(['2024-01-01']),
            'WarehouseID': ['WH-NCR'],
            'Region': ['Delhi NCR'],
            'Zone': ['North'],
            'SKU': ['SKU-001'],
            'ProductName': ['Product A'],
            'OpeningStock_Units': [100],
            'InboundStock_Units': [50],
            'Demand_Units': [30],
            'FulfilledUnits': [30],
            'ClosingStock_Units': [120],
            'AvgDailyDemand_7D': [25],
            'DaysOfCover': [4.8],
            'ReorderPoint_Units': [50],
            'RecommendedReorderQty': [100],
            'Stockout': ['No'],
            'StockStatus': ['Healthy']
        })

        transformer = DataTransformer()
        result = transformer.transform_inventory_daily(df)

        self.assertEqual(result['inventory_date'].iloc[0], date(2024, 1, 1))
        self.assertEqual(result['warehouse_id'].iloc[0], 'WH-NCR')
        self.assertEqual(result['opening_stock'].iloc[0], 100)
        self.assertEqual(result['closing_stock'].iloc[0], 120)

    def test_transform_returns(self):
        """Returns should be transformed correctly"""
        df = pd.DataFrame({
            'ReturnID': ['RET-0001'],
            'ReturnDate': pd.to_datetime(['2024-01-01']),
            'PlatformID': ['AMZ'],
            'Platform': ['Amazon'],
            'SKU': ['SKU-001'],
            'ProductName': ['Product A'],
            'Reason': ['Quality Issue'],
            'UnitsReturned': [1],
            'RefundAmount_INR': [1000],
            'Status': ['Completed']
        })

        transformer = DataTransformer()
        result = transformer.transform_returns(df)

        self.assertEqual(result['return_id'].iloc[0], 'RET-0001')
        self.assertEqual(result['return_date'].iloc[0], date(2024, 1, 1))
        self.assertEqual(result['units_returned'].iloc[0], 1)


class TestDataValidationIntegration(unittest.TestCase):
    """Integration tests for validation"""

    def test_validate_referential_integrity(self):
        """Test referential integrity validation"""
        df_sales = pd.DataFrame({
            'Date': pd.to_datetime(['2024-01-01']),
            'PlatformID': ['AMZ', 'FLP'],
            'SKU': ['SKU-001', 'SKU-002'],
            'UnitsSold': [10, 20],
            'NetSales_INR': [15000, 25000]
        })

        products = {'SKU-001', 'SKU-002'}
        platforms = {'AMZ', 'FLP'}

        validator = DataValidator()
        valid, errors = validator.validate_daily_sales(df_sales, products, platforms)

        self.assertTrue(valid)

    def test_validate_referential_integrity_invalid_sku(self):
        """Test referential integrity with invalid SKU"""
        df_sales = pd.DataFrame({
            'Date': pd.to_datetime(['2024-01-01']),
            'PlatformID': ['AMZ'],
            'SKU': ['INVALID'],
            'UnitsSold': [10],
            'NetSales_INR': [15000]
        })

        products = {'SKU-001'}
        platforms = {'AMZ'}

        validator = DataValidator()
        valid, errors = validator.validate_daily_sales(df_sales, products, platforms)

        self.assertFalse(valid)
        self.assertTrue(any('Invalid SKUs' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
