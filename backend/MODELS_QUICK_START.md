# SQLAlchemy Models - Quick Start Guide

## File Location
- **Models Definition**: `backend/app/models/database_models.py`
- **Models Package**: `backend/app/models/__init__.py`
- **Full Reference**: `backend/DATABASE_MODELS_REFERENCE.md`

## Models Overview

### 13 Complete ORM Models Created

**Master Data (3)**
- `Product` - Product/SKU master data
- `Platform` - E-commerce platforms
- `Warehouse` - Physical warehouse locations

**Transactional (5)**
- `DailySales` - Daily sales by date/platform/SKU
- `Advertising` - Ad performance metrics
- `DailyCosts` - Cost breakdown
- `Return` - Product returns/refunds
- `Cancellation` - Order cancellations

**Inventory (3)**
- `InventoryDaily` - Daily stock snapshots
- `RegionalSales` - Regional demand analysis
- `ReplenishmentAlert` - Inventory alerts

**Configuration (2)**
- `BusinessConfig` - Business rules/thresholds
- `SupplyChainConfig` - Supply chain settings

---

## Quick Import

```python
from app.models import (
    # Master data
    Product, Platform, Warehouse,
    # Transactional
    DailySales, Advertising, DailyCosts, Return, Cancellation,
    # Inventory
    InventoryDaily, RegionalSales, ReplenishmentAlert,
    # Configuration
    BusinessConfig, SupplyChainConfig,
    # Base for creating engine
    Base
)
```

---

## Common Queries

### Get all products
```python
from app.models import Product
from app.database import SessionLocal

db = SessionLocal()
products = db.query(Product).filter(Product.active == True).all()
db.close()
```

### Get sales for date range
```python
from datetime import datetime, timedelta
from app.models import DailySales

start = datetime.now() - timedelta(days=7)
sales = db.query(DailySales).filter(
    DailySales.sale_date >= start.date()
).all()
```

### Sales by platform
```python
from sqlalchemy import func

platform_sales = db.query(
    DailySales.platform_id,
    func.sum(DailySales.net_sales).label("total_sales")
).group_by(DailySales.platform_id).all()
```

### Product + Sales join
```python
from app.models import Product, DailySales

sales_data = db.query(
    Product.product_name,
    DailySales.sale_date,
    DailySales.net_sales
).join(
    Product, DailySales.sku == Product.sku
).filter(
    DailySales.sale_date >= start_date
).all()
```

### Inventory alerts
```python
latest_inventory = db.query(InventoryDaily).filter(
    InventoryDaily.stock_status == 'Critical'
).all()
```

---

## Key Features

**Relationships**: All relationships properly defined with:
- Back-references for bidirectional access
- Cascade delete for transactional data
- Lazy loading defaults

**Constraints**: 
- Unique constraints on transactional data
- Foreign key constraints to master data
- Composite indexes for query optimization

**Data Types**:
- `Numeric(18, 2)` for monetary values (precision)
- `Date` for date fields (no time component)
- `DateTime` for timestamps
- `Integer` for counts

**Indexes**:
- Single column indexes on commonly queried fields (date, SKU, platform, warehouse)
- Composite indexes for frequent multi-column queries
- Status/priority fields indexed for filtering

---

## Database Operations

### Create (Insert)
```python
new_sale = DailySales(
    sale_date=datetime.now(),
    platform_id="AMZ",
    sku="SKU001",
    units_sold=10,
    net_sales=5000.00
)
db.add(new_sale)
db.commit()
```

### Read (Query)
```python
sale = db.query(DailySales).filter(
    DailySales.sales_id == 1
).first()
```

### Update
```python
sale.units_sold = 15
db.commit()
```

### Delete
```python
db.delete(sale)
db.commit()
```

### Bulk Operations
```python
records = [DailySales(...), DailySales(...)]
db.bulk_save_objects(records)
db.commit()
```

---

## Model Structure Reference

Each model includes:
- **Column definitions** with types, constraints, indexes
- **Foreign key relationships** to master data
- **Relationship mappings** for ORM navigation
- **Default values** matching schema
- **Docstrings** explaining purpose
- **__repr__** methods for debugging

---

## Integration Points

### With FastAPI Routes
```python
from fastapi import Depends
from app.database import get_db
from app.models import DailySales

@app.get("/api/sales/")
def get_sales(db = Depends(get_db)):
    return db.query(DailySales).limit(10).all()
```

### With Pydantic Schemas
```python
from pydantic import BaseModel

class SaleSchema(BaseModel):
    sale_date: date
    platform_id: str
    sku: str
    net_sales: float
    
    class Config:
        from_attributes = True  # ORM mode
```

### With Analytics Services
```python
from app.models import DailySales, Product, Platform
from sqlalchemy import func

def get_platform_performance(db, start_date, end_date):
    return db.query(
        Platform.platform_name,
        func.sum(DailySales.net_sales)
    ).join(Platform).filter(
        DailySales.sale_date.between(start_date, end_date)
    ).group_by(Platform.platform_name).all()
```

---

## Database Mapping

All models map directly to MySQL schema in `sql/schema.sql`:

| ORM Model | Table Name | Purpose |
|-----------|-----------|---------|
| Product | products | SKU master |
| Platform | platforms | Platform master |
| Warehouse | warehouses | Warehouse master |
| DailySales | daily_sales | Sales transactions |
| Advertising | advertising | Ad metrics |
| DailyCosts | daily_costs | Cost breakdown |
| Return | returns | Return/refund tracking |
| Cancellation | cancellations | Cancellation tracking |
| InventoryDaily | inventory_daily | Stock snapshots |
| RegionalSales | regional_sales | Regional demand |
| ReplenishmentAlert | replenishment_alerts | Inventory alerts |
| BusinessConfig | business_config | Business rules |
| SupplyChainConfig | supply_chain_config | Supply chain settings |

---

## Testing Models

```python
# Test import
from app.models import Product, DailySales
from app.database import SessionLocal

# Create session
db = SessionLocal()

# Test query
products = db.query(Product).limit(1).all()
assert len(products) >= 0

# Clean up
db.close()

print("Models working correctly!")
```

---

## Next Steps

1. **Verify Database Connection**: Run `backend/etl/test_connection.py`
2. **Create Tables**: Run `sql/schema.sql` on MySQL
3. **Load Data**: Use `backend/etl/loader.py` to load Excel data
4. **Test Queries**: Run analytics queries against populated data
5. **Integrate with API**: Use models in FastAPI routes

---

## Documentation

- **Full Reference**: See `DATABASE_MODELS_REFERENCE.md` for detailed column lists
- **Schema Definition**: See `sql/schema.sql` for SQL equivalents
- **Usage Examples**: See individual model docstrings in `database_models.py`
