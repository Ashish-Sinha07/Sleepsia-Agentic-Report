# Database Schema Guide

Reference for the MySQL database structure used by the Sleepsia Agentic Reporting System.

## Overview

The database contains transactional and master data for e-commerce analytics across 5 platforms.

```
Data Sources (Excel)
    ↓
ETL Process
    ↓
MySQL Database
    ├── Master Tables (Products, Platforms, Warehouses)
    ├── Transactional Tables (Sales, Returns, Cancellations)
    ├── Operational Tables (Inventory, Advertising)
    └── Reporting Tables (Metrics Cache, Alerts)
```

## Master Data Tables

### `products`
Product master data.

```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    product_cost DECIMAL(10, 2),
    standard_price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sku (sku),
    INDEX idx_category (category)
);
```

**Use in code**:
```python
# In database.py
def get_product(sku: str) -> dict:
    """Get product details by SKU."""
    query = "SELECT * FROM products WHERE sku = %s"
    return db.fetch_one(query, (sku,))
```

### `platforms`
E-commerce platform master data.

```sql
CREATE TABLE platforms (
    platform_id INT PRIMARY KEY AUTO_INCREMENT,
    platform_name VARCHAR(50) UNIQUE NOT NULL,
    platform_code VARCHAR(20) UNIQUE NOT NULL,
    commission_rate DECIMAL(5, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code (platform_code)
);
```

**Data**:
- Amazon
- Flipkart
- Blinkit
- Myntra
- JioMart

### `warehouses`
Warehouse locations and master data.

```sql
CREATE TABLE warehouses (
    warehouse_id INT PRIMARY KEY AUTO_INCREMENT,
    warehouse_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    capacity INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_city (city)
);
```

## Transactional Tables

### `sales`
Daily sales transactions (the main fact table).

```sql
CREATE TABLE sales (
    sale_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    date DATE NOT NULL,
    sku VARCHAR(50) NOT NULL,
    product_id INT,
    platform_id INT,
    warehouse_id INT,
    
    -- Units and Orders
    units_sold INT,
    orders INT,
    
    -- Revenue
    gross_sales DECIMAL(12, 2),
    discounts DECIMAL(12, 2),
    net_sales DECIMAL(12, 2),
    
    -- Costs
    product_cost DECIMAL(12, 2),
    platform_fee DECIMAL(12, 2),
    shipping_cost DECIMAL(12, 2),
    payment_fee DECIMAL(12, 2),
    other_cost DECIMAL(12, 2),
    
    -- Quality Metrics
    units_returned INT DEFAULT 0,
    refund_amount DECIMAL(12, 2) DEFAULT 0,
    units_cancelled INT DEFAULT 0,
    cancellation_amount DECIMAL(12, 2) DEFAULT 0,
    
    -- Advertising
    ad_spend DECIMAL(12, 2),
    ad_attributed_units INT,
    ad_attributed_sales DECIMAL(12, 2),
    ad_impressions INT,
    ad_clicks INT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    
    INDEX idx_date (date),
    INDEX idx_sku (sku),
    INDEX idx_platform (platform_id),
    INDEX idx_warehouse (warehouse_id),
    INDEX idx_date_platform (date, platform_id)
);
```

**Use in code**:
```python
# Get sales for a date range
def get_sales(start_date: date, end_date: date, platform: str = None) -> List[dict]:
    """Query sales data."""
    query = """
        SELECT s.* FROM sales s
        JOIN platforms p ON s.platform_id = p.platform_id
        WHERE s.date BETWEEN %s AND %s
    """
    params = [start_date, end_date]
    
    if platform:
        query += " AND p.platform_code = %s"
        params.append(platform)
    
    return db.fetch_all(query, params)
```

### `returns`
Product returns (normalized from sales table for detailed analysis).

```sql
CREATE TABLE returns (
    return_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    date DATE NOT NULL,
    sku VARCHAR(50) NOT NULL,
    product_id INT,
    platform_id INT,
    units_returned INT,
    refund_amount DECIMAL(12, 2),
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    
    INDEX idx_date (date),
    INDEX idx_sku (sku),
    INDEX idx_platform (platform_id)
);
```

### `cancellations`
Order cancellations (normalized from sales table).

```sql
CREATE TABLE cancellations (
    cancellation_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    date DATE NOT NULL,
    sku VARCHAR(50) NOT NULL,
    product_id INT,
    platform_id INT,
    units_cancelled INT,
    cancellation_amount DECIMAL(12, 2),
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    
    INDEX idx_date (date),
    INDEX idx_sku (sku),
    INDEX idx_platform (platform_id)
);
```

## Operational Tables

### `inventory`
Current inventory levels by warehouse and SKU.

```sql
CREATE TABLE inventory (
    inventory_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(50) NOT NULL,
    product_id INT,
    warehouse_id INT,
    
    -- Inventory Levels
    total_units INT,
    available_units INT,
    reserved_units INT,
    damaged_units INT DEFAULT 0,
    
    -- Replenishment
    reorder_point INT,
    safety_stock INT,
    last_reorder_date DATE,
    days_of_cover DECIMAL(5, 2),
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    
    UNIQUE KEY uniq_warehouse_sku (warehouse_id, sku),
    INDEX idx_warehouse (warehouse_id),
    INDEX idx_sku (sku),
    INDEX idx_status (available_units)
);
```

**Inventory Status Logic**:
```python
def get_inventory_status(days_of_cover: float, available: int, reorder_point: int, safety_stock: int) -> str:
    """Determine inventory status."""
    if available <= 0:
        return "STOCKOUT"
    if available < safety_stock:
        return "CRITICAL"
    if available < reorder_point:
        return "LOW_STOCK"
    return "HEALTHY"
```

### `advertising`
Advertising spend and attribution data by platform.

```sql
CREATE TABLE advertising (
    ad_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    date DATE NOT NULL,
    platform_id INT,
    sku VARCHAR(50),
    
    -- Ad Metrics
    ad_spend DECIMAL(12, 2),
    impressions INT,
    clicks INT,
    attributed_units INT,
    attributed_sales DECIMAL(12, 2),
    
    -- Calculated Metrics
    ctr DECIMAL(5, 2),  -- Click-through rate
    cpc DECIMAL(10, 2), -- Cost per click
    roas DECIMAL(8, 2), -- Return on ad spend
    acos DECIMAL(5, 2), -- Advertising cost of sale
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    
    INDEX idx_date (date),
    INDEX idx_platform (platform_id),
    INDEX idx_sku (sku)
);
```

## Reporting Tables

### `daily_kpis`
Cached daily KPI calculations (for performance).

```sql
CREATE TABLE daily_kpis (
    kpi_date DATE PRIMARY KEY,
    
    -- Revenue Metrics
    total_revenue DECIMAL(15, 2),
    gross_sales DECIMAL(15, 2),
    net_sales DECIMAL(15, 2),
    total_discounts DECIMAL(15, 2),
    
    -- Cost Metrics
    total_costs DECIMAL(15, 2),
    total_product_cost DECIMAL(15, 2),
    total_platform_fees DECIMAL(15, 2),
    
    -- Profitability
    gross_profit DECIMAL(15, 2),
    profit_margin DECIMAL(5, 2),
    
    -- Advertising
    total_ad_spend DECIMAL(15, 2),
    ad_attributed_sales DECIMAL(15, 2),
    overall_roas DECIMAL(8, 2),
    overall_acos DECIMAL(5, 2),
    
    -- Quality
    total_returns INT,
    total_cancellations INT,
    return_rate DECIMAL(5, 2),
    cancellation_rate DECIMAL(5, 2),
    
    -- Volume
    total_units_sold INT,
    total_orders INT,
    avg_order_value DECIMAL(10, 2),
    
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### `product_kpis`
Cached product-level KPIs (for performance).

```sql
CREATE TABLE product_kpis (
    kpi_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_date DATE NOT NULL,
    sku VARCHAR(50) NOT NULL,
    product_id INT,
    platform_id INT,
    
    -- Sales
    units_sold INT,
    orders INT,
    net_sales DECIMAL(12, 2),
    
    -- Profitability
    profit DECIMAL(12, 2),
    profit_margin DECIMAL(5, 2),
    status ENUM('healthy', 'at_risk', 'unprofitable'),
    
    -- Quality
    return_rate DECIMAL(5, 2),
    cancellation_rate DECIMAL(5, 2),
    
    -- Advertising
    roas DECIMAL(8, 2),
    acos DECIMAL(5, 2),
    
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    
    INDEX idx_date (product_date),
    INDEX idx_sku (sku),
    INDEX idx_platform (platform_id),
    INDEX idx_status (status)
);
```

### `alerts`
Generated business alerts.

```sql
CREATE TABLE alerts (
    alert_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    alert_type VARCHAR(50),  -- inventory, profitability, sales, ads, quality
    severity ENUM('info', 'warning', 'critical'),
    
    product_id INT,
    platform_id INT,
    warehouse_id INT,
    
    title VARCHAR(255),
    description TEXT,
    
    metric_name VARCHAR(100),
    metric_value DECIMAL(15, 4),
    threshold DECIMAL(15, 4),
    
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    
    INDEX idx_severity (severity),
    INDEX idx_created (created_at),
    INDEX idx_resolved (is_resolved),
    INDEX idx_type (alert_type)
);
```

## Query Patterns

### Get KPIs for a Date Range
```python
def get_kpi_for_range(start_date: date, end_date: date):
    query = """
        SELECT 
            SUM(net_sales) as total_revenue,
            SUM(product_cost + platform_fee + shipping_cost + payment_fee) as total_costs,
            SUM(net_sales) - SUM(product_cost + platform_fee + shipping_cost + payment_fee) as profit,
            SUM(units_sold) as total_units,
            SUM(orders) as total_orders,
            SUM(ad_spend) as total_ad_spend,
            SUM(ad_attributed_sales) as ad_sales,
            SUM(units_returned) as total_returns,
            SUM(units_cancelled) as total_cancellations
        FROM sales
        WHERE date BETWEEN %s AND %s
    """
    return db.fetch_one(query, (start_date, end_date))
```

### Get Product Performance
```python
def get_product_performance(sku: str, start_date: date, end_date: date):
    query = """
        SELECT 
            SUM(net_sales) as revenue,
            COUNT(*) as days_sold,
            SUM(units_sold) as units,
            SUM(units_returned) as returns,
            AVG(profit_margin) as avg_margin
        FROM product_kpis
        WHERE sku = %s AND product_date BETWEEN %s AND %s
    """
    return db.fetch_one(query, (sku, start_date, end_date))
```

### Get Inventory Alerts
```python
def get_inventory_alerts():
    query = """
        SELECT * FROM inventory
        WHERE available_units < reorder_point OR available_units <= 0
        ORDER BY available_units ASC
    """
    return db.fetch_all(query)
```

### Get Platform Comparison
```python
def get_platform_comparison(start_date: date, end_date: date):
    query = """
        SELECT 
            p.platform_name,
            SUM(s.net_sales) as revenue,
            SUM(s.net_sales) - SUM(s.product_cost + s.platform_fee) as profit,
            COUNT(DISTINCT s.orders) as orders,
            SUM(s.ad_spend) as ad_spend,
            SUM(s.ad_attributed_sales) / SUM(s.ad_spend) as roas
        FROM sales s
        JOIN platforms p ON s.platform_id = p.platform_id
        WHERE s.date BETWEEN %s AND %s
        GROUP BY p.platform_id
        ORDER BY revenue DESC
    """
    return db.fetch_all(query, (start_date, end_date))
```

## Setup Instructions

### 1. Create Database
```sql
CREATE DATABASE sleepsia_reporting
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE sleepsia_reporting;
```

### 2. Create Tables
Run all the CREATE TABLE statements above.

### 3. Create Indexes
Indexes are included in CREATE TABLE statements above.

### 4. Load Initial Data
```bash
# From the project root
python backend/etl/run_etl.py
```

This will:
- Read `data/final_sleepsia_report_data.xlsx`
- Parse all sheets
- Validate data
- Load into MySQL

### 5. Verify Setup
```sql
SELECT 
    (SELECT COUNT(*) FROM sales) as sales_count,
    (SELECT COUNT(*) FROM products) as products_count,
    (SELECT COUNT(*) FROM warehouses) as warehouses_count,
    (SELECT COUNT(*) FROM inventory) as inventory_count;
```

## Performance Optimization

### Recommended Indexes (Already in Schema)
- `sales.date` - For date range queries
- `sales.sku` - For product lookups
- `sales.platform_id` - For platform analysis
- `inventory.warehouse_id` - For warehouse queries
- `products.sku` - For product master lookups

### Query Optimization Tips
1. Always filter by date range (most queries)
2. Use date index for range queries
3. Pre-calculate daily/product KPIs in cache tables
4. Consider materialized views for complex aggregations

### Cache Strategy
1. **Daily KPIs** - Calculate once per day at midnight
2. **Product KPIs** - Calculate daily for top 100 products
3. **Platform KPIs** - Calculate daily
4. **Inventory Status** - Update real-time

## Data Volume Expectations

For an MVP with 6 months of data:
- **sales**: 1-2 million rows (~2 GB)
- **products**: 50-100 rows
- **platforms**: 5 rows
- **warehouses**: 10-15 rows
- **inventory**: 500-1000 rows (current state)
- **alerts**: 1000-5000 rows

## Connection String Examples

```python
# From .env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/sleepsia_reporting

# In Python
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
```

```bash
# From command line
mysql -h localhost -u user -p sleepsia_reporting
```

---

**Ready to implement**: `backend/database.py` using this schema
