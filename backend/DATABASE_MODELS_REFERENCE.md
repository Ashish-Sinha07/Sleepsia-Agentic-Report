# Sleepsia Database Models Reference

## Overview

Complete SQLAlchemy ORM model definitions for the Sleepsia Agentic Business Reporting System. All models are mapped directly to the MySQL schema defined in `sql/schema.sql`.

**Location**: `backend/app/models/database_models.py`  
**Base Class**: `declarative_base()` from SQLAlchemy  
**Database**: MySQL 8+ with utf8mb4 encoding

---

## 1. Master Data Models

### Product

**Table**: `products`  
**Purpose**: Stores product/SKU master information

**Columns**:
```
product_id         INT (Primary Key, Auto-increment)
sku                VARCHAR(20) NOT NULL UNIQUE [indexed]
product_name       VARCHAR(255) NOT NULL
product_type       VARCHAR(100) [indexed]
material           VARCHAR(100)
intended_use       VARCHAR(255)
primary_market     VARCHAR(100)
selling_price      DECIMAL(18,2) NOT NULL
product_cost       DECIMAL(18,2) NOT NULL
target_margin_pct  DECIMAL(10,4)
brand              VARCHAR(100)
category           VARCHAR(100)
sub_category       VARCHAR(100)
active             BOOLEAN DEFAULT TRUE [indexed]
created_at         DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE
```

**Relationships**:
- One-to-Many: daily_sales, advertising, costs, returns, cancellations, inventory_daily, regional_sales, replenishment_alerts

**Usage Example**:
```python
from app.models import Product
from app.database import SessionLocal

db = SessionLocal()
product = db.query(Product).filter(Product.sku == "SKU001").first()
print(f"Price: {product.selling_price}, Cost: {product.product_cost}")
```

---

### Platform

**Table**: `platforms`  
**Purpose**: Represents e-commerce platforms (Amazon, Flipkart, etc.)

**Columns**:
```
platform_id              VARCHAR(10) PRIMARY KEY
platform_name            VARCHAR(100) NOT NULL UNIQUE
sales_channel_type       VARCHAR(50)
default_platform_fee_pct DECIMAL(10,4) NOT NULL
active                   BOOLEAN DEFAULT TRUE [indexed]
created_at               DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at               DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE
```

**Seed Data**:
- AMZ - Amazon (16% fee)
- BLK - Blinkit (18% fee)
- FLP - Flipkart (15% fee)
- MTR - Myntra (17% fee)
- JMT - JioMart (16% fee)

**Relationships**:
- One-to-Many: daily_sales, advertising, costs, returns, cancellations

**Usage Example**:
```python
from app.models import Platform

# Get all active platforms
platforms = db.query(Platform).filter(Platform.active == True).all()
for p in platforms:
    print(f"{p.platform_name}: {p.default_platform_fee_pct}% fee")
```

---

### Warehouse

**Table**: `warehouses`  
**Purpose**: Physical warehouse locations with geographic coordinates

**Columns**:
```
warehouse_id          VARCHAR(20) PRIMARY KEY
warehouse_name        VARCHAR(100) NOT NULL
region                VARCHAR(100) NOT NULL [indexed]
zone                  VARCHAR(50) NOT NULL [indexed]
city                  VARCHAR(100) NOT NULL [indexed]
latitude              DECIMAL(10,8)
longitude             DECIMAL(11,8)
storage_capacity_units INT
status                VARCHAR(50) DEFAULT 'Active' [indexed]
created_at            DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at            DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE
```

**Seed Data**:
- WH-NCR: Delhi NCR Warehouse (28.4595, 77.0266)
- WH-JPR: Jaipur Warehouse (26.9124, 75.7873)
- WH-MUM: Mumbai Warehouse (19.0760, 72.8777)
- WH-BLR: Bengaluru Warehouse (12.9716, 77.5946)
- WH-HYD: Hyderabad Warehouse (17.3850, 78.4867)

**Relationships**:
- One-to-Many: inventory_daily, regional_sales, replenishment_alerts

**Usage Example**:
```python
from app.models import Warehouse

# Get all warehouses in a region
warehouses = db.query(Warehouse).filter(Warehouse.region == "Delhi NCR").all()

# Get warehouse with map coordinates
warehouse = db.query(Warehouse).filter(Warehouse.warehouse_id == "WH-BLR").first()
print(f"Location: ({warehouse.latitude}, {warehouse.longitude})")
```

---

## 2. Transactional Data Models

### DailySales

**Table**: `daily_sales`  
**Purpose**: Daily sales transactions by platform and SKU

**Columns**:
```
sales_id            INT (Primary Key, Auto-increment)
sale_date           DATE NOT NULL [indexed]
platform_id         VARCHAR(10) NOT NULL [FK: platforms, indexed]
sku                 VARCHAR(20) NOT NULL [FK: products, indexed]
orders              INT DEFAULT 0
units_sold          INT DEFAULT 0
gross_sales         DECIMAL(18,2) DEFAULT 0
discount            DECIMAL(18,2) DEFAULT 0
net_sales           DECIMAL(18,2) DEFAULT 0
ad_attributed_units INT DEFAULT 0
ad_attributed_sales DECIMAL(18,2) DEFAULT 0
created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
```

**Unique Constraint**: (sale_date, platform_id, sku)  
**Composite Index**: (sale_date, platform_id, sku)

**Relationships**:
- Many-to-One: platform, product

**Usage Example**:
```python
from app.models import DailySales
from datetime import datetime, timedelta

# Get sales for last 7 days
start_date = datetime.now() - timedelta(days=7)
sales = db.query(DailySales).filter(
    DailySales.sale_date >= start_date.date()
).all()

# Total revenue by platform
from sqlalchemy import func
revenue = db.query(
    DailySales.platform_id,
    func.sum(DailySales.net_sales)
).group_by(DailySales.platform_id).all()
```

---

### Advertising

**Table**: `advertising`  
**Purpose**: Daily advertising performance metrics

**Columns**:
```
advertising_id      INT (Primary Key, Auto-increment)
ad_date             DATE NOT NULL [indexed]
platform_id         VARCHAR(10) NOT NULL [FK: platforms, indexed]
sku                 VARCHAR(20) NOT NULL [FK: products, indexed]
impressions         INT DEFAULT 0
clicks              INT DEFAULT 0
attributed_orders   INT DEFAULT 0
attributed_units    INT DEFAULT 0
attributed_sales    DECIMAL(18,2) DEFAULT 0
ad_spend            DECIMAL(18,2) DEFAULT 0
created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
```

**Unique Constraint**: (ad_date, platform_id, sku)  
**Composite Index**: (ad_date, platform_id, sku)

**Calculated Metrics** (typically done in SQL/Python):
- CTR (Click-Through Rate) = (clicks / impressions) * 100
- ROAS (Return on Ad Spend) = attributed_sales / ad_spend
- ACOS (Ad Cost of Sale) = (ad_spend / attributed_sales) * 100

**Relationships**:
- Many-to-One: platform, product

**Usage Example**:
```python
# Get ROAS for a product on a platform
from sqlalchemy import func

roas_data = db.query(
    Advertising.ad_date,
    func.sum(Advertising.attributed_sales).label("sales"),
    func.sum(Advertising.ad_spend).label("spend")
).filter(
    Advertising.sku == "SKU001",
    Advertising.platform_id == "AMZ"
).group_by(Advertising.ad_date).all()

for row in roas_data:
    roas = row.sales / row.spend if row.spend > 0 else 0
    print(f"Date: {row.ad_date}, ROAS: {roas:.2f}")
```

---

### DailyCosts

**Table**: `daily_costs`  
**Purpose**: Cost breakdown by date, platform, and SKU

**Columns**:
```
cost_id             INT (Primary Key, Auto-increment)
cost_date           DATE NOT NULL [indexed]
platform_id         VARCHAR(10) NOT NULL [FK: platforms, indexed]
sku                 VARCHAR(20) NOT NULL [FK: products, indexed]
product_cost        DECIMAL(18,2) DEFAULT 0
platform_fee        DECIMAL(18,2) DEFAULT 0
shipping_cost       DECIMAL(18,2) DEFAULT 0
payment_fee         DECIMAL(18,2) DEFAULT 0
other_variable_cost DECIMAL(18,2) DEFAULT 0
created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
```

**Unique Constraint**: (cost_date, platform_id, sku)

**Total Cost Formula**: product_cost + platform_fee + shipping_cost + payment_fee + other_variable_cost

**Relationships**:
- Many-to-One: platform, product

**Usage Example**:
```python
# Calculate total costs for a period
from sqlalchemy import func

total_costs = db.query(
    func.sum(DailyCosts.product_cost).label("product_cost"),
    func.sum(DailyCosts.platform_fee).label("platform_fees"),
    func.sum(DailyCosts.shipping_cost).label("shipping"),
    func.sum(DailyCosts.payment_fee).label("payment_fees"),
).filter(
    DailyCosts.sku == "SKU001",
    DailyCosts.cost_date.between(start_date, end_date)
).first()
```

---

### Return

**Table**: `returns`  
**Purpose**: Product returns/refunds tracking

**Columns**:
```
return_id      INT (Primary Key, Auto-increment)
return_date    DATE NOT NULL [indexed]
platform_id    VARCHAR(10) NOT NULL [FK: platforms, indexed]
sku            VARCHAR(20) NOT NULL [FK: products, indexed]
reason         VARCHAR(255)
units_returned INT DEFAULT 0
refund_amount  DECIMAL(18,2) DEFAULT 0
status         VARCHAR(50) DEFAULT 'Completed' [indexed]
created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
```

**Status Values**: 'Completed', 'Pending', etc.

**Relationships**:
- Many-to-One: platform, product

**Usage Example**:
```python
# Calculate return rate
from sqlalchemy import func

return_stats = db.query(
    func.sum(Return.units_returned).label("total_returned"),
    func.sum(Return.refund_amount).label("total_refunds")
).filter(
    Return.sku == "SKU001",
    Return.return_date >= start_date
).first()

# Return rate % = (units_returned / units_sold) * 100
```

---

### Cancellation

**Table**: `cancellations`  
**Purpose**: Cancelled orders tracking

**Columns**:
```
cancellation_id INT (Primary Key, Auto-increment)
cancellation_date DATE NOT NULL [indexed]
platform_id     VARCHAR(10) NOT NULL [FK: platforms, indexed]
sku             VARCHAR(20) NOT NULL [FK: products, indexed]
reason          VARCHAR(255)
units_cancelled INT DEFAULT 0
created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
```

**Relationships**:
- Many-to-One: platform, product

**Usage Example**:
```python
# Cancellation rate by platform
from sqlalchemy import func

cancellation_stats = db.query(
    Cancellation.platform_id,
    func.sum(Cancellation.units_cancelled).label("total_cancelled")
).filter(
    Cancellation.cancellation_date >= start_date
).group_by(Cancellation.platform_id).all()
```

---

## 3. Inventory Data Models

### InventoryDaily

**Table**: `inventory_daily`  
**Purpose**: Daily inventory snapshot at warehouse-product level

**Columns**:
```
inventory_id          INT (Primary Key, Auto-increment)
inventory_date        DATE NOT NULL [indexed]
warehouse_id          VARCHAR(20) NOT NULL [FK: warehouses, indexed]
sku                   VARCHAR(20) NOT NULL [FK: products, indexed]
opening_stock         INT DEFAULT 0
inbound_stock         INT DEFAULT 0
demand_units          INT DEFAULT 0
fulfilled_units       INT DEFAULT 0
closing_stock         INT DEFAULT 0
avg_daily_demand_7d   INT DEFAULT 0
days_of_cover         DECIMAL(10,2)
reorder_point         INT DEFAULT 0
recommended_reorder_qty INT DEFAULT 0
stockout              VARCHAR(10) DEFAULT 'No'
stock_status          VARCHAR(50) [indexed]
created_at            DATETIME DEFAULT CURRENT_TIMESTAMP
```

**Unique Constraint**: (inventory_date, warehouse_id, sku)  
**Composite Index**: (inventory_date, warehouse_id, sku)

**Stock Status Values**: 'Healthy', 'Low Stock', 'Critical', 'Stockout'  
**Stockout Values**: 'Yes', 'No'

**Relationships**:
- Many-to-One: warehouse, product

**Usage Example**:
```python
# Get critical stock alerts
critical_stock = db.query(InventoryDaily).filter(
    InventoryDaily.inventory_date == latest_date,
    InventoryDaily.stock_status == 'Critical'
).all()

for item in critical_stock:
    print(f"SKU: {item.sku}, Warehouse: {item.warehouse_id}, Stock: {item.closing_stock}")

# Calculate days of cover
# days_of_cover = closing_stock / avg_daily_demand_7d
```

---

### RegionalSales

**Table**: `regional_sales`  
**Purpose**: Regional demand analysis by warehouse

**Columns**:
```
regional_sales_id INT (Primary Key, Auto-increment)
sales_date        DATE NOT NULL [indexed]
warehouse_id      VARCHAR(20) NOT NULL [FK: warehouses, indexed]
region            VARCHAR(100) NOT NULL [indexed]
sku               VARCHAR(20) NOT NULL [FK: products, indexed]
units_sold        INT DEFAULT 0
net_sales         DECIMAL(18,2) DEFAULT 0
created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
```

**Relationships**:
- Many-to-One: warehouse, product

**Usage Example**:
```python
# Regional sales analysis
from sqlalchemy import func

regional_analysis = db.query(
    RegionalSales.region,
    func.sum(RegionalSales.units_sold).label("total_units"),
    func.sum(RegionalSales.net_sales).label("total_sales")
).filter(
    RegionalSales.sales_date >= start_date
).group_by(RegionalSales.region).all()
```

---

### ReplenishmentAlert

**Table**: `replenishment_alerts`  
**Purpose**: Actionable inventory alerts for procurement

**Columns**:
```
alert_id               INT (Primary Key, Auto-increment)
alert_date             DATE NOT NULL [indexed]
warehouse_id           VARCHAR(20) NOT NULL [FK: warehouses, indexed]
region                 VARCHAR(100) NOT NULL
sku                    VARCHAR(20) NOT NULL [FK: products, indexed]
closing_stock          INT DEFAULT 0
avg_daily_demand_7d    INT DEFAULT 0
days_of_cover          DECIMAL(10,2)
reorder_point          INT DEFAULT 0
recommended_reorder_qty INT DEFAULT 0
stock_status           VARCHAR(50) [indexed]
priority               VARCHAR(50) [indexed]
recommended_action     VARCHAR(255)
created_at             DATETIME DEFAULT CURRENT_TIMESTAMP
```

**Priority Values**: 'Critical', 'High', 'Medium', 'Low'  
**Stock Status Values**: 'Critical', 'Low Stock', 'Healthy'

**Relationships**:
- Many-to-One: warehouse, product

**Usage Example**:
```python
# Get high-priority alerts
high_priority = db.query(ReplenishmentAlert).filter(
    ReplenishmentAlert.alert_date == latest_date,
    ReplenishmentAlert.priority.in_(['Critical', 'High'])
).all()

for alert in high_priority:
    print(f"Action: {alert.recommended_action}")
    print(f"Recommend ordering: {alert.recommended_reorder_qty} units")
```

---

## 4. Configuration Models

### BusinessConfig

**Table**: `business_config`  
**Purpose**: Business rules and thresholds

**Columns**:
```
config_id      INT (Primary Key, Auto-increment)
config_key     VARCHAR(100) NOT NULL UNIQUE
config_value   VARCHAR(255)
unit_threshold VARCHAR(100)
description    TEXT
created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE
```

**Seed Configuration**:
```
ReportSchedule: 'Daily' (threshold: '06:00 AM IST')
ReportingGrain: 'Product × Platform × Date'
OrganicSalesRule: 'Total sales - ad-attributed sales'
ProfitRule: 'Net sales - refunds - product cost - fees - logistics - ads - other variable costs'
LossThreshold: 'Contribution < 0'
LowMarginThreshold: 'Margin < 15%'
HealthyMarginThreshold: 'Margin >= 15%'
```

**Usage Example**:
```python
# Get business configuration
from app.models import BusinessConfig

config = db.query(BusinessConfig).filter(
    BusinessConfig.config_key == 'LowMarginThreshold'
).first()

# Extract threshold value
if config:
    threshold_pct = float(config.config_value.split('<')[1].strip().rstrip('%'))
```

---

### SupplyChainConfig

**Table**: `supply_chain_config`  
**Purpose**: Supply chain and inventory thresholds

**Columns**:
```
config_id      INT (Primary Key, Auto-increment)
config_key     VARCHAR(100) NOT NULL UNIQUE
config_value   VARCHAR(255)
unit_threshold VARCHAR(100)
description    TEXT
created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE
```

**Seed Configuration**:
```
PrimaryGrain: 'Warehouse × Product × Date'
DemandWindow: '7' (unit_threshold: 'days')
CriticalCoverageDays: '3' (days)
LowStockCoverageDays: '7' (days)
StockoutRule: 'Closing stock = 0'
SafetyStock: '14' (days)
```

**Usage Example**:
```python
# Get supply chain config
supply_config = db.query(SupplyChainConfig).filter(
    SupplyChainConfig.config_key == 'CriticalCoverageDays'
).first()

critical_days = int(supply_config.config_value)
```

---

## 5. Usage Patterns

### Session Management

```python
from app.database import SessionLocal
from app.models import Product, DailySales

db = SessionLocal()
try:
    # Query operations
    product = db.query(Product).first()
finally:
    db.close()
```

### Create Records

```python
from datetime import datetime
from app.models import DailySales

new_sale = DailySales(
    sale_date=datetime.now(),
    platform_id="AMZ",
    sku="SKU001",
    orders=5,
    units_sold=7,
    gross_sales=5000.00,
    discount=500.00,
    net_sales=4500.00
)
db.add(new_sale)
db.commit()
```

### Join Queries

```python
from sqlalchemy import func

# Sales with product details
sales_with_products = db.query(
    DailySales.sale_date,
    Product.product_name,
    Platform.platform_name,
    func.sum(DailySales.net_sales).label("total_sales")
).join(Product, DailySales.sku == Product.sku
).join(Platform, DailySales.platform_id == Platform.platform_id
).filter(DailySales.sale_date >= start_date
).group_by(DailySales.sale_date, Product.product_name, Platform.platform_name
).all()
```

### Bulk Operations

```python
# Bulk insert
sales_records = [
    DailySales(sale_date=date, platform_id="AMZ", sku="SKU001", ...),
    DailySales(sale_date=date, platform_id="FLP", sku="SKU002", ...),
]
db.bulk_save_objects(sales_records)
db.commit()
```

---

## 6. Index Strategy

**Indexes by Table**:

| Table | Indexes |
|-------|---------|
| products | idx_sku, idx_active, idx_product_type |
| platforms | idx_active |
| warehouses | idx_region, idx_zone, idx_city, idx_status |
| daily_sales | idx_sale_date, idx_platform_id, idx_sku, idx_date_platform_sku |
| advertising | idx_ad_date, idx_platform_id, idx_sku, idx_date_platform_sku |
| daily_costs | idx_cost_date, idx_platform_id, idx_sku |
| returns | idx_return_date, idx_platform_id, idx_sku, idx_status |
| cancellations | idx_cancellation_date, idx_platform_id, idx_sku |
| inventory_daily | idx_inventory_date, idx_warehouse_id, idx_sku, idx_stock_status, idx_date_warehouse_sku |
| regional_sales | idx_sales_date, idx_warehouse_id, idx_region, idx_sku |
| replenishment_alerts | idx_alert_date, idx_warehouse_id, idx_sku, idx_priority, idx_stock_status |

---

## 7. Relationships Summary

**Master Data Relationships**:
- 1 Product ← Many DailySales, Advertising, DailyCosts, Returns, Cancellations, InventoryDaily, RegionalSales, ReplenishmentAlerts
- 1 Platform ← Many DailySales, Advertising, DailyCosts, Returns, Cancellations
- 1 Warehouse ← Many InventoryDaily, RegionalSales, ReplenishmentAlerts

**Cascade Delete**: Enabled for all transactional relationships (orphaned records deleted automatically)

---

## 8. Import Examples

```python
# Import all models
from app.models import (
    Product, Platform, Warehouse,
    DailySales, Advertising, DailyCosts, Return, Cancellation,
    InventoryDaily, RegionalSales, ReplenishmentAlert,
    BusinessConfig, SupplyChainConfig, Base
)

# Use in services
from app.models import Product, DailySales
from app.database import SessionLocal

def get_product_sales(sku: str, start_date, end_date):
    db = SessionLocal()
    try:
        return db.query(DailySales).join(
            Product, DailySales.sku == Product.sku
        ).filter(
            Product.sku == sku,
            DailySales.sale_date.between(start_date, end_date)
        ).all()
    finally:
        db.close()
```

---

## 9. Notes

- **Numeric Types**: All monetary values use `Decimal(18,2)` for precision
- **Indexes**: Composite indexes on (date, platform_id, sku) for common query patterns
- **Foreign Keys**: All FK relationships use `ON DELETE CASCADE` implicitly via SQLAlchemy
- **Timestamps**: All tables include `created_at` and `updated_at` tracking (config tables only)
- **Unique Constraints**: Enforced at DB level for transactional data
- **Character Set**: UTF-8MB4 for international character support
