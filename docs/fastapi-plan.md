# FastAPI Backend Implementation Plan

**Date**: August 23, 2026  
**Status**: Planning Phase (Ready for Review)  
**Scope**: Sleepsia Agentic Business Reporting System - FastAPI Backend Layer

---

## Executive Summary

This document outlines the complete FastAPI backend architecture for the Sleepsia Agentic Business Reporting System. The backend serves a React dashboard frontend with REST APIs for analytics, reporting, inventory, and AI business assistant functionality.

**Key Principle**: The backend is the system of record for all business calculations and decisions. The frontend displays data only; all business logic, metrics, and analytics remain on the backend.

---

## 1. Backend Architecture Overview

### 1.1 Architecture Stack

```
React Frontend (Vite + Tailwind CSS)
        ↓
REST API (FastAPI + Pydantic)
        ↓
Analytics Layer (Metrics Engine, Analysis Agents)
        ↓
MySQL Database (SQLAlchemy ORM)
```

### 1.2 Technology Choices

**Web Framework**: FastAPI 0.100+
- Automatic API documentation (Swagger/ReDoc)
- Built-in request validation (Pydantic)
- Async support for concurrent requests
- Type hints for safety
- Fast response times

**ORM**: SQLAlchemy 2.0+
- Connection pooling
- Query building
- Lazy loading support
- Integration with MySQL

**Database Driver**: PyMySQL or mysql-connector-python
- Pure Python implementation
- No system dependencies
- Good performance for reads

**Configuration Management**: pydantic-settings
- Environment variable loading
- Type-safe configuration
- Support for .env files

**Data Processing**: Pandas
- Aggregations and transformations
- Time series operations
- Easy DataFrame manipulation

**HTTP Client**: httpx (for external calls if needed)
- Async support
- Similar API to requests

**Testing**: pytest
- Fixture-based setup
- Parametrized tests
- Async test support

---

## 2. Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database session management
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── kpis.py           # /api/kpis/*
│   │   │   ├── platforms.py      # /api/platform-performance/*
│   │   │   ├── products.py       # /api/product-performance/*
│   │   │   ├── advertising.py    # /api/advertising/*
│   │   │   ├── profitability.py  # /api/profitability/*
│   │   │   ├── inventory.py      # /api/inventory/*
│   │   │   ├── warehouses.py     # /api/warehouses/*
│   │   │   ├── alerts.py         # /api/alerts/*
│   │   │   ├── ai.py             # /api/ai/*
│   │   │   └── reports.py        # /api/reports/*
│   │   │
│   │   ├── dependencies.py        # Shared dependencies (db session, auth)
│   │   └── errors.py              # Error handling & responses
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── kpi_schemas.py         # Request/response models for KPIs
│   │   ├── filter_schemas.py      # Reusable filter models
│   │   ├── platform_schemas.py    # Platform response models
│   │   ├── product_schemas.py     # Product response models
│   │   ├── advertising_schemas.py # Advertising response models
│   │   ├── profitability_schemas.py
│   │   ├── inventory_schemas.py
│   │   ├── warehouse_schemas.py
│   │   ├── alert_schemas.py
│   │   ├── ai_schemas.py
│   │   └── report_schemas.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── database_models.py     # SQLAlchemy ORM models
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── kpi_service.py         # KPI calculations
│   │   ├── platform_service.py    # Platform aggregations
│   │   ├── product_service.py     # Product aggregations
│   │   ├── advertising_service.py # Ad efficiency analysis
│   │   ├── profitability_service.py
│   │   ├── inventory_service.py
│   │   ├── warehouse_service.py
│   │   ├── alert_service.py
│   │   ├── ai_service.py          # AI integration
│   │   ├── chart_service.py       # Chart data preparation
│   │   └── report_service.py      # Report generation
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── formatting.py          # Currency, percentage, date formatting
│   │   ├── filters.py             # Filter parsing & validation
│   │   ├── pagination.py          # Pagination helpers
│   │   ├── dates.py               # Date range calculations
│   │   └── caching.py             # Simple in-memory caching
│   │
│   └── middleware/
│       ├── __init__.py
│       ├── cors.py                # CORS configuration
│       ├── error_handler.py       # Global error handling
│       └── logging.py             # Request/response logging
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Shared pytest fixtures
│   ├── test_kpis.py
│   ├── test_platforms.py
│   ├── test_products.py
│   ├── test_advertising.py
│   ├── test_profitability.py
│   ├── test_inventory.py
│   ├── test_warehouses.py
│   ├── test_alerts.py
│   ├── test_ai.py
│   └── test_reports.py
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── Dockerfile                     # Optional: Docker support

# At project root
docs/
├── fastapi-plan.md                # This file
├── api-reference.md               # Complete API endpoint reference (TBD)
└── integration-guide.md           # Backend-frontend integration (TBD)
```

---

## 3. Endpoint Inventory

### 3.1 KPIs Endpoints

These endpoints return key performance indicators for the selected date range.

| Method | Endpoint | Purpose | Database Source |
|--------|----------|---------|-----------------|
| GET | `/api/kpis` | Get aggregate KPIs | `vw_daily_kpi_summary` |
| GET | `/api/kpis/by-date` | Get KPIs for each date in range | `vw_daily_kpi_summary` (grouped) |
| GET | `/api/kpis/by-platform` | Get KPIs by platform | `vw_platform_performance` (filtered) |
| GET | `/api/kpis/by-product` | Get KPIs by product/SKU | `vw_product_performance` (filtered) |

**Query Parameters**:
```
start_date: string (ISO 8601)   # Default: 30 days ago
end_date: string (ISO 8601)     # Default: today
platform_id: string             # Optional: filter by platform
sku: string                      # Optional: filter by product
region: string                   # Optional: filter by region
```

**Response Structure** (example):
```json
{
  "period": {
    "start_date": "2026-08-01",
    "end_date": "2026-08-21"
  },
  "kpis": {
    "total_revenue": 4250000,
    "net_revenue": 4050000,
    "total_profit": 820000,
    "profit_margin_pct": 20.2,
    "units_sold": 15000,
    "orders": 1200,
    "ad_spend": 450000,
    "roas": 3.2,
    "return_rate_pct": 3.5,
    "cancellation_rate_pct": 2.1,
    "organic_sales": 3200000,
    "ad_attributed_sales": 850000
  },
  "trends": {
    "revenue_trend": "upward",
    "profit_trend": "stable",
    "return_rate_trend": "downward"
  },
  "comparisons": {
    "vs_previous_period": {
      "revenue_change_pct": 12.4,
      "profit_change_pct": 8.7
    }
  }
}
```

### 3.2 Platform Performance Endpoints

| Method | Endpoint | Purpose | Source |
|--------|----------|---------|--------|
| GET | `/api/platform-performance` | All platforms comparison | `vw_platform_performance` |
| GET | `/api/platform-performance/{platform_id}` | Single platform details | `vw_product_platform_daily` (filtered) |
| GET | `/api/platform-performance/trend` | Platform trend over time | `vw_product_platform_daily` (time-grouped) |

**Response**: List of platform metrics with revenue, units, ROAS, ACOS, profit margin, etc.

### 3.3 Product Performance Endpoints

| Method | Endpoint | Purpose | Source |
|--------|----------|---------|--------|
| GET | `/api/product-performance` | All products summary | `vw_product_performance` |
| GET | `/api/product-performance/{sku}` | Single product details | `vw_product_platform_daily` (filtered) |
| GET | `/api/top-products` | Top N products by revenue | `vw_product_performance` (sorted, limit) |
| GET | `/api/bottom-products` | Bottom N products by contribution | `vw_product_performance` (sorted, limit) |
| GET | `/api/products/opportunity-matrix` | Product quadrant analysis | `vw_product_performance` (computed) |

**Query Parameters**:
```
limit: integer (default: 10)     # For top/bottom products
sort_by: string                  # revenue | contribution | units | margin
order: string                    # asc | desc (default: desc)
platform_id: string              # Optional filter
```

### 3.4 Advertising Endpoints

| Method | Endpoint | Purpose | Source |
|--------|----------|---------|--------|
| GET | `/api/advertising/summary` | Overall ad performance KPIs | `vw_product_platform_daily` (ad cols) |
| GET | `/api/advertising/by-platform` | Ad metrics by platform | `vw_product_platform_daily` (grouped) |
| GET | `/api/advertising/by-product` | Ad metrics by product | `vw_product_platform_daily` (grouped) |
| GET | `/api/advertising/efficiency` | Product ad efficiency ranking | `vw_product_platform_daily` (ROAS/ACOS) |

**Response includes**: Ad spend, ROAS, ACOS, attributed sales, impressions, clicks, CTR

### 3.5 Profitability Endpoints

| Method | Endpoint | Purpose | Source |
|--------|----------|---------|--------|
| GET | `/api/profitability/summary` | Overall profitability KPIs | `vw_profitability` |
| GET | `/api/profitability/by-platform` | Profitability by platform | `vw_profitability` (grouped) |
| GET | `/api/profitability/by-product` | Profitability by product | `vw_profitability` (grouped) |
| GET | `/api/profitability/cost-breakdown` | Cost structure analysis | `vw_product_platform_daily` (cost cols summed) |

**Response includes**: Contribution, profit margin, profitability status (Healthy/At Risk/Loss)

### 3.6 Inventory Endpoints

| Method | Endpoint | Purpose | Source |
|--------|----------|---------|--------|
| GET | `/api/inventory` | Inventory summary | `vw_inventory_health` |
| GET | `/api/inventory/by-warehouse` | Inventory by warehouse | `inventory_daily` (grouped) |
| GET | `/api/inventory/low-stock` | Low stock SKUs | `inventory_daily` (filtered by status) |
| GET | `/api/inventory/stockouts` | Out-of-stock SKUs | `inventory_daily` (where stockout='Yes') |
| GET | `/api/inventory/trend` | Inventory trend over time | `inventory_daily` (time-grouped) |

**Query Parameters**:
```
warehouse_id: string             # Optional filter
status: string                   # Healthy | Low Stock | Critical | Stockout
sort_by: string                  # days_of_cover | closing_stock | product_name
limit: integer                   # Default: 100
```

### 3.7 Warehouse Endpoints

| Method | Endpoint | Purpose | Source |
|--------|----------|---------|--------|
| GET | `/api/warehouses` | All warehouses with location & status | `vw_warehouse_summary` |
| GET | `/api/warehouses/{warehouse_id}` | Single warehouse details | `warehouses` + `vw_inventory_health` |
| GET | `/api/warehouses/{warehouse_id}/inventory` | Warehouse inventory detail | `inventory_daily` (filtered) |
| GET | `/api/warehouses/{warehouse_id}/replenishment` | Replenishment recommendations | `replenishment_alerts` (filtered) |

**Response includes**: Warehouse name, region, city, latitude, longitude, stock status, health indicator, SKU counts

### 3.8 Alerts Endpoints

| Method | Endpoint | Purpose | Source |
|--------|----------|---------|--------|
| GET | `/api/alerts` | All active alerts | `replenishment_alerts` + computed |
| GET | `/api/alerts/critical` | Critical priority alerts | `replenishment_alerts` (where priority='Critical') |
| GET | `/api/alerts/by-type` | Alerts grouped by type | Various (stockout, low margin, high return, etc.) |
| GET | `/api/alerts/summary` | Alert counts by severity | Computed aggregation |

**Alert Types**:
- Stockout (inventory)
- Low Stock (inventory)
- Unprofitable Product (profitability)
- Poor ROAS (advertising)
- High Return Rate (quality)
- High Cancellation Rate (quality)

### 3.9 AI Assistant Endpoints

| Method | Endpoint | Purpose | Source |
|--------|----------|---------|--------|
| POST | `/api/ai/chat` | Send message to AI assistant | Multiple (analytics + agents) |
| GET | `/api/ai/suggested-questions` | Get pre-built question prompts | Static configuration |
| POST | `/api/ai/analyze` | Get analysis for specific question | Analytics layer |

**Request** (POST /api/ai/chat):
```json
{
  "message": "Which platform is most profitable?",
  "filters": {
    "start_date": "2026-08-01",
    "end_date": "2026-08-21",
    "platform_id": null,
    "sku": null
  },
  "context": "dashboard"  // or "profitability" page, etc.
}
```

**Response**:
```json
{
  "response": "Amazon is the most profitable platform...",
  "analysis_type": "platform_profitability",
  "key_metrics": {
    "top_platform": "Amazon",
    "top_platform_contribution": 320000,
    "top_platform_margin_pct": 22.5
  },
  "supporting_data": [
    {
      "platform": "Amazon",
      "contribution": 320000,
      "margin_pct": 22.5
    }
  ],
  "confidence": "high",
  "data_completeness_pct": 100
}
```

### 3.10 Reports Endpoints

| Method | Endpoint | Purpose | Source |
|--------|----------|---------|--------|
| GET | `/api/reports/types` | Available report types | Static config |
| POST | `/api/reports/generate` | Generate a new report | Analytics + Report agent |
| GET | `/api/reports/{report_id}` | Get report details | `reports` table (TBD) |
| GET | `/api/reports/{report_id}/download` | Download report (PDF/Excel) | Generated file |

**Request** (POST /api/reports/generate):
```json
{
  "report_type": "management_summary",
  "date_range": {
    "start_date": "2026-08-01",
    "end_date": "2026-08-21"
  },
  "filters": {
    "platform_id": null,
    "sku": null
  },
  "format": "pdf"  // or "excel"
}
```

### 3.11 Chart Data Endpoints

These return data specifically formatted for chart rendering.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/revenue-chart` | Time series: date → revenue |
| GET | `/api/profit-trend` | Time series: date → profit |
| GET | `/api/platform-comparison` | Bar chart data: platform → metrics |
| GET | `/api/product-matrix` | Scatter plot: revenue vs margin |
| GET | `/api/cost-breakdown` | Pie chart: cost components |
| GET | `/api/organic-vs-ad` | Donut: organic vs ad-attributed |

**Response Structure** (example for `/api/revenue-chart`):
```json
{
  "chart_type": "line",
  "data": [
    {"date": "2026-08-01", "revenue": 150000, "profit": 25000},
    {"date": "2026-08-02", "revenue": 165000, "profit": 28000},
    ...
  ],
  "series": [
    {"key": "revenue", "name": "Revenue", "color": "#3b82f6"},
    {"key": "profit", "name": "Profit", "color": "#10b981"}
  ]
}
```

---

## 4. Request/Response Schema Design

### 4.1 Reusable Filter Model

```python
class DateRangeFilter(BaseModel):
    start_date: date = Field(default_factory=lambda: date.today() - timedelta(days=30))
    end_date: date = Field(default_factory=date.today)
    
class PlatformFilter(BaseModel):
    platform_id: Optional[str] = None  # All if None
    
class ProductFilter(BaseModel):
    sku: Optional[str] = None
    product_name: Optional[str] = None
    
class WarehouseFilter(BaseModel):
    warehouse_id: Optional[str] = None
    region: Optional[str] = None
    
class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
    
class SortParams(BaseModel):
    sort_by: str = "date"
    order: Literal["asc", "desc"] = "desc"
```

### 4.2 Standard Response Wrapper

All endpoints should follow a consistent response structure:

```python
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    timestamp: datetime
    request_id: str
```

### 4.3 KPI Response Schema

```python
class KpiMetrics(BaseModel):
    total_revenue: Decimal
    net_revenue: Decimal
    total_profit: Decimal
    profit_margin_pct: Decimal
    units_sold: int
    orders: int
    ad_spend: Decimal
    roas: Optional[Decimal]
    acos_pct: Optional[Decimal]
    return_rate_pct: Decimal
    cancellation_rate_pct: Decimal
    organic_sales: Decimal
    ad_attributed_sales: Decimal
    
class KpiResponse(BaseModel):
    period: DateRange
    kpis: KpiMetrics
    trends: Optional[Dict[str, str]]
    comparisons: Optional[Dict[str, Any]]
```

### 4.4 Error Response Schema

```python
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str
```

---

## 5. Database Access Strategy

### 5.1 Connection Management

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,           # Test connections
    pool_size=10,
    max_overflow=20,
    echo=settings.SQL_ECHO,       # Log SQL if DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 5.2 ORM Models

SQLAlchemy models should reflect the database schema but be used sparingly (mostly for master data):

```python
# models/database_models.py
from sqlalchemy import Column, String, Date, Decimal, Integer, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    sku = Column(String(20), primary_key=True)
    product_name = Column(String(255), nullable=False)
    product_cost = Column(Decimal(18,2), nullable=False)
    # ... other columns

class DailySales(Base):
    __tablename__ = "daily_sales"
    sales_id = Column(Integer, primary_key=True)
    sale_date = Column(Date, nullable=False, index=True)
    platform_id = Column(String(10), ForeignKey("platforms.platform_id"), index=True)
    sku = Column(String(20), ForeignKey("products.sku"), index=True)
    # ... other columns
```

### 5.3 Direct SQL Queries (for Analytics)

Most analytics queries should use direct SQL against views:

```python
# services/kpi_service.py
from sqlalchemy import text

def get_daily_kpis(db: Session, start_date: date, end_date: date) -> Dict:
    query = """
    SELECT 
        SUM(total_orders) as total_orders,
        SUM(total_units_sold) as total_units_sold,
        SUM(total_net_sales) as total_net_sales,
        ...
    FROM vw_daily_kpi_summary
    WHERE date BETWEEN :start_date AND :end_date
    """
    result = db.execute(
        text(query),
        {"start_date": start_date, "end_date": end_date}
    ).fetchone()
    return dict(result)
```

### 5.4 Parameterized Queries (Safety)

**Always use parameterized queries to prevent SQL injection**:

```python
# ✓ CORRECT
query = text("""
    SELECT * FROM daily_sales 
    WHERE platform_id = :platform_id AND sale_date = :sale_date
""")
db.execute(query, {"platform_id": platform, "sale_date": date})

# ✗ WRONG
query = f"SELECT * FROM daily_sales WHERE platform_id = '{platform}'"
```

---

## 6. Filtering & Pagination Strategy

### 6.1 Query Parameter Validation

All filter parameters should be validated at the API layer:

```python
from fastapi import Query

@app.get("/api/products")
async def get_products(
    db: Session = Depends(get_db),
    start_date: date = Query(default=date.today() - timedelta(days=30)),
    end_date: date = Query(default=date.today()),
    platform_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    # Validation happens automatically
    # Invalid params return 422 Unprocessable Entity
    pass
```

### 6.2 Pagination Pattern

Large result sets must be paginated server-side:

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool

def paginate_query(query, skip: int, limit: int):
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return PaginatedResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )
```

### 6.3 Filtering Pattern

Filters should be optional and composable:

```python
def build_query(db: Session, filters: Dict[str, Any]):
    query = db.query(vw_product_platform_daily)
    
    if filters.get("start_date"):
        query = query.filter(vw_product_platform_daily.c.date >= filters["start_date"])
    
    if filters.get("end_date"):
        query = query.filter(vw_product_platform_daily.c.date <= filters["end_date"])
    
    if filters.get("platform_id"):
        query = query.filter(vw_product_platform_daily.c.platform_id == filters["platform_id"])
    
    return query
```

---

## 7. Error Handling Strategy

### 7.1 Exception Classes

```python
# api/errors.py

class SleepsiaException(Exception):
    """Base exception"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code

class ValidationError(SleepsiaException):
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)

class ResourceNotFound(SleepsiaException):
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", "NOT_FOUND", 404)

class DatabaseError(SleepsiaException):
    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR", 500)
```

### 7.2 Global Error Handler

```python
# middleware/error_handler.py

from fastapi.responses import JSONResponse

@app.exception_handler(SleepsiaException)
async def sleepsia_exception_handler(request: Request, exc: SleepsiaException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "error_code": exc.code,
            "request_id": request.headers.get("x-request-id"),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log unexpected errors
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR",
            "request_id": request.headers.get("x-request-id"),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
```

---

## 8. CORS Configuration

### 8.1 CORS Middleware Setup

```python
# middleware/cors.py
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI, settings: Settings):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:3000", "http://localhost:5173"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

### 8.2 Environment Configuration

```ini
# .env
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "https://sleepsia.example.com"]
```

---

## 9. Configuration Management

### 9.1 Settings Class

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    DEBUG: bool = False
    
    # Database
    DB_HOST: str
    DB_PORT: int = 3306
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DATABASE_URL: str = ""  # Computed property
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_TITLE: str = "Sleepsia Analytics API"
    API_VERSION: str = "1.0.0"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    SQL_ECHO: bool = False
    
    # Analytics
    DEFAULT_DAYS_BACK: int = 30
    MAX_DATE_RANGE_DAYS: int = 365
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
```

### 9.2 Environment Variables (.env)

```ini
APP_ENV=development
DEBUG=True

DB_HOST=localhost
DB_PORT=3306
DB_NAME=sleepsia_reporting
DB_USER=sleepsia
DB_PASSWORD=sleepsia

API_HOST=0.0.0.0
API_PORT=8000

CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

LOG_LEVEL=INFO
SQL_ECHO=False
```

---

## 10. Database Access Patterns by Endpoint Type

### 10.1 KPI Endpoints (Simple Aggregation)

```
Source: vw_daily_kpi_summary or vw_platform_performance
Pattern: Filter by date range, return aggregated metrics
Caching: Cache for 1-5 minutes (historical data is stable)
```

### 10.2 Chart Endpoints (Time Series)

```
Source: vw_daily_kpi_summary or vw_product_platform_daily
Pattern: Group by date, order by date, return time-indexed data
Caching: Cache for 5 minutes
Pagination: Not needed (time series usually fits in memory)
```

### 10.3 Table Endpoints (Detailed Data)

```
Source: vw_product_performance or vw_product_platform_daily
Pattern: Filter, sort, paginate
Caching: Minimal/none (user might apply different filters quickly)
```

### 10.4 Analysis Endpoints (Multiple Views)

```
Source: Multiple views combined in service layer
Pattern: Join data from multiple views, compute metrics
Caching: Cache intermediate results (expensive joins)
```

---

## 11. Testing Strategy

### 11.1 Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_kpis.py             # KPI endpoint tests
├── test_platforms.py        # Platform endpoint tests
├── test_products.py         # Product endpoint tests
├── test_services.py         # Service layer tests
├── test_filters.py          # Filter parsing tests
└── fixtures/
    ├── sample_data.py       # Test data
    └── mock_db.py           # Mock database
```

### 11.2 Test Fixtures

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    # Create in-memory SQLite database for testing
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///:memory:")
    # ... setup tables ...
    yield Session(engine)

@pytest.fixture
def mock_filters():
    return {
        "start_date": date(2026, 8, 1),
        "end_date": date(2026, 8, 21),
        "platform_id": None,
    }
```

### 11.3 Test Examples

```python
# tests/test_kpis.py

def test_get_kpis_success(client, mock_filters):
    response = client.get(
        "/api/kpis",
        params=mock_filters
    )
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "period" in data

def test_get_kpis_invalid_date_range(client):
    response = client.get(
        "/api/kpis",
        params={
            "start_date": "2026-08-21",
            "end_date": "2026-08-01",  # end before start
        }
    )
    assert response.status_code == 400

def test_get_kpis_pagination(client):
    # Test that limit is enforced
    response = client.get(
        "/api/products",
        params={"limit": 2000}  # Exceeds max
    )
    assert response.status_code == 422  # Validation error
```

---

## 12. Integration Strategy with React Frontend

### 12.1 API Client Configuration

Frontend uses Axios with these conventions:

```javascript
// dashboard/src/services/api.js
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
});
```

**Expected Port**: 8000 (matches FastAPI default)

### 12.2 Request Flow

```
React Component
    ↓
analyticsApi.getKPIs(filters)
    ↓
axios.get('/api/kpis', { params: filters })
    ↓
FastAPI: GET /api/kpis?start_date=...&end_date=...
    ↓
Service Layer (KpiService)
    ↓
Database (views)
    ↓
Response JSON
    ↓
React: setState(data)
    ↓
Re-render
```

### 12.3 Filter Parameter Mapping

Frontend filters → Backend query params:

```javascript
const filters = {
  startDate: "2026-08-01",
  endDate: "2026-08-21",
  platform: "amazon",
  product: null,
  region: null,
};

// Transforms to:
// GET /api/kpis?start_date=2026-08-01&end_date=2026-08-21&platform_id=amazon
```

### 12.4 Response Format Expectations

Frontend expects consistent response structures (see Section 4: Request/Response Schema).

**Never return raw database records**—always transform to client-friendly format:

```python
# ✗ WRONG: Raw database columns
SELECT * FROM vw_product_performance

# ✓ CORRECT: Transform to camelCase with clear structure
{
  "items": [
    {
      "sku": "SLP-1001",
      "productName": "Contour Pillow",
      "revenue": 425000,
      "profitMarginPct": 22.5,
      "profitabilityStatus": "Healthy"
    }
  ],
  "total": 45
}
```

---

## 13. Integration with Existing Agents

### 13.1 Analysis Layer Integration

The backend should leverage existing analytics agents:

```python
# services/ai_service.py
from agents.llm_analysis_agent import LLMAnalysisAgent
from analytics.metrics_engine import MetricsEngine
from analytics.analysis_input import AnalysisInput

class AiService:
    def __init__(self):
        self.llm_agent = LLMAnalysisAgent(api_key=settings.ANTHROPIC_API_KEY)
        self.metrics_engine = MetricsEngine()
    
    def analyze_question(self, question: str, filters: Dict) -> Dict:
        # Fetch metrics from database
        metrics = self._fetch_metrics(filters)
        
        # Create analysis input
        analysis_input = AnalysisInput(
            analysis_date=date.today(),
            analysis_type="product",
            product_metrics=metrics,
            # ... other fields
        )
        
        # Get LLM analysis
        result = self.llm_agent.analyze(analysis_input)
        
        return {
            "response": result.summary,
            "key_metrics": result.key_metrics,
            "confidence": result.confidence,
        }
```

### 13.2 Orchestration Integration

If workflow orchestration is needed:

```python
# services/orchestration_service.py
from analytics.orchestration import WorkflowOrchestrator

class OrchestrationService:
    def __init__(self):
        self.orchestrator = WorkflowOrchestrator(...)
    
    def generate_daily_reports(self, report_date: date):
        result = self.orchestrator.execute(report_date)
        # Store result path in database for user download
        # Return success/failure status
        return result
```

### 13.3 Existing Agent Compatibility

All existing agents remain in their current locations:
- `agents/validation_agent.py` – validation
- `agents/analysis_agent.py` – rule-based analysis
- `agents/llm_analysis_agent.py` – Claude-powered analysis
- `agents/insight_recommendation_agent.py` – insights
- `agents/report_agent.py` – report narratives

The FastAPI backend **calls** these agents, not replaces them.

---

## 14. Development and Deployment Commands

### 14.1 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with local database credentials

# Run database migrations (if needed)
# mysql -h localhost -u sleepsia -p sleepsia_reporting < sql/schema.sql

# Start FastAPI dev server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# The API is now at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
# ReDoc at http://localhost:8000/redoc
```

### 14.2 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_kpis.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### 14.3 Production Deployment

```bash
# Using Gunicorn with Uvicorn workers
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --port 8000

# Or using Docker (optional)
docker build -t sleepsia-backend .
docker run -p 8000:8000 --env-file .env sleepsia-backend
```

---

## 15. Key Files and Patterns

### 15.1 Main Application Entry Point

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api.routes import kpis, platforms, products, advertising, profitability, inventory, warehouses, alerts, ai, reports

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
    )
    
    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Routes
    app.include_router(kpis.router, prefix="/api")
    app.include_router(platforms.router, prefix="/api")
    app.include_router(products.router, prefix="/api")
    app.include_router(advertising.router, prefix="/api")
    app.include_router(profitability.router, prefix="/api")
    app.include_router(inventory.router, prefix="/api")
    app.include_router(warehouses.router, prefix="/api")
    app.include_router(alerts.router, prefix="/api")
    app.include_router(ai.router, prefix="/api")
    app.include_router(reports.router, prefix="/api")
    
    # Health check
    @app.get("/health")
    def health_check():
        return {"status": "healthy"}
    
    return app

app = create_app()
```

### 15.2 Service Layer Pattern

```python
# services/kpi_service.py
from sqlalchemy.orm import Session
from datetime import date

class KpiService:
    @staticmethod
    def get_daily_kpis(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> Dict:
        """Get aggregated KPIs for date range"""
        query = """
        SELECT 
            SUM(total_orders) as total_orders,
            ...
        FROM vw_daily_kpi_summary
        WHERE date BETWEEN :start_date AND :end_date
        """
        if platform_id:
            query += " AND platform_id = :platform_id"
        
        result = db.execute(
            text(query),
            {"start_date": start_date, "end_date": end_date, "platform_id": platform_id}
        ).fetchone()
        
        return KpiService._format_response(result)
    
    @staticmethod
    def _format_response(db_row) -> Dict:
        """Transform raw database values to API format"""
        return {
            "totalOrders": int(db_row.total_orders),
            "netRevenue": float(db_row.net_sales),
            # ... etc
        }
```

### 15.3 Route Pattern

```python
# api/routes/kpis.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.database import get_db
from app.services.kpi_service import KpiService
from app.schemas import KpiResponse

router = APIRouter(tags=["KPIs"])

@router.get("/kpis", response_model=KpiResponse)
async def get_kpis(
    db: Session = Depends(get_db),
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end_date: date = Query(default=date.today()),
    platform_id: Optional[str] = Query(None),
):
    """Get aggregate KPIs for selected period"""
    kpis = KpiService.get_daily_kpis(db, start_date, end_date, platform_id)
    return KpiResponse(
        period={"start_date": start_date, "end_date": end_date},
        kpis=kpis
    )
```

---

## 16. Risks, Ambiguities & Assumptions

### 16.1 Potential Risks

1. **Database Connection Stability**
   - Risk: Network instability might cause frequent disconnections
   - Mitigation: Implement connection pooling with `pool_pre_ping=True`

2. **Performance on Large Date Ranges**
   - Risk: Querying 1+ year of data might be slow
   - Mitigation: Enforce `MAX_DATE_RANGE_DAYS`, implement caching, suggest aggregation APIs

3. **LLM API Failures**
   - Risk: Claude API downtime or errors
   - Mitigation: Implement retry logic, fallback responses, circuit breaker pattern

4. **Concurrent User Load**
   - Risk: Multiple simultaneous requests might overwhelm database
   - Mitigation: Implement caching, rate limiting, database connection pooling

### 16.2 Ambiguities Resolved

1. **Financial Metric Calculations**: Use existing `MetricsEngine` from analytics layer (not LLM)
2. **View vs Raw Data**: Use views for most endpoints, raw tables only for master data
3. **Response Format**: Use camelCase in JSON (frontend convention) vs snake_case in database
4. **Pagination**: Always server-side, default 100 items, max 1000
5. **Date Defaults**: Default to 30 days back from today

### 16.3 Assumptions Made

1. **Database is Always Available**: No offline-first capability
2. **Authentication Not Required**: MVP assumes trusted internal use
3. **Single Deployment**: No multi-region or sharding complexity
4. **Synchronous Processing**: No long-running async jobs (future enhancement)
5. **Timezone**: All dates treated as IST (India Standard Time)
6. **Data Quality**: Database validation already passed (data is clean)

---

## 17. Next Steps After Approval

Once this plan is approved:

1. **Database Verification** (0.5 hours)
   - Confirm all views exist and are working
   - Validate data types and indexes
   - Test sample queries

2. **Project Scaffolding** (1 hour)
   - Create directory structure
   - Generate `__init__.py` files
   - Create `main.py` and `config.py`

3. **Core Infrastructure** (2 hours)
   - Database session management
   - CORS setup
   - Error handling middleware
   - Configuration management

4. **Endpoint Implementation** (8-10 hours)
   - Each endpoint group (KPIs, Platforms, Products, etc.)
   - Request/response validation
   - Service layer logic
   - Database queries

5. **Testing** (4 hours)
   - Unit tests for services
   - Integration tests for endpoints
   - Fixture setup
   - Test database

6. **Integration & Validation** (2 hours)
   - Connect frontend to backend
   - Verify all endpoints work with real data
   - Performance validation

7. **Documentation** (1 hour)
   - API reference (auto-generated via Swagger)
   - Environment variables guide
   - Deployment instructions

**Total Estimated Time**: 18-20 hours

---

## 18. Success Criteria

The FastAPI backend is complete and ready for integration when:

- [ ] All 10 endpoint groups are implemented and tested
- [ ] All endpoints return data matching frontend expectations
- [ ] Database views and queries are optimized (< 1 second response time)
- [ ] Error handling returns 4xx/5xx with clear error messages
- [ ] CORS is properly configured for frontend access
- [ ] All environment variables are documented
- [ ] Swagger/ReDoc documentation is complete
- [ ] Tests cover all major endpoints
- [ ] Frontend successfully calls backend endpoints with real data
- [ ] No unhandled exceptions or memory leaks

---

## Appendix A: Database View Summary

| View Name | Purpose | Primary Use |
|-----------|---------|-------------|
| `vw_product_platform_daily` | Atomic transactional data with all metrics | Detailed analysis, drill-downs |
| `vw_platform_performance` | Aggregated metrics by platform | Platform comparison, KPIs |
| `vw_product_performance` | Aggregated metrics by product | Product rankings, analysis |
| `vw_profitability` | Profitability metrics and status | Profitability page |
| `vw_inventory_health` | Inventory status and coverage | Inventory page |
| `vw_warehouse_summary` | Warehouse status and metrics | Warehouse map, inventory |
| `vw_regional_performance` | Regional sales and demand | Regional analysis |
| `vw_daily_kpi_summary` | High-level daily business metrics | Dashboard KPIs |

---

## Appendix B: Glossary

- **ROAS**: Return on Ad Spend (attributed sales / ad spend)
- **ACOS**: Ad Cost of Sale ((ad spend / attributed sales) * 100)
- **CTR**: Click-Through Rate ((clicks / impressions) * 100)
- **Contribution**: Net Sales minus all variable costs
- **Profit Margin %**: (Contribution / Net Sales) * 100
- **Organic Sales**: Total sales minus ad-attributed sales
- **Days of Cover**: Current inventory / average daily demand
- **SKU**: Stock Keeping Unit (product identifier)

---

**Document Status**: READY FOR REVIEW  
**Last Updated**: August 23, 2026  
**Author**: FastAPI Planning Agent  
**Next Action**: User Review & Approval
