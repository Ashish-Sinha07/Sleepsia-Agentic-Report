# Sleepsia FastAPI Backend

FastAPI-based REST API backend for the Sleepsia Agentic Business Reporting System.

## Features

- **KPI Endpoints** (`/api/kpis`): Aggregate and daily key performance indicators
- **Platform Analysis** (`/api/platform-performance`): Platform-wise performance metrics
- **Product Analysis** (`/api/product-performance`): Product rankings and top/bottom products
- **Warehouse Management** (`/api/warehouses`): Warehouse inventory and status
- **Inventory** (`/api/inventory`): Stock levels and replenishment data
- **Alerts** (`/api/alerts`): Critical alerts and notifications
- **CORS Support**: Pre-configured for React frontend
- **Health Checks**: `/health` and `/ready` endpoints
- **Automatic Documentation**: Swagger UI at `/docs`

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file in the `backend` directory:

```ini
# Application
APP_ENV=development
DEBUG=True

# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sleepsia_reporting
DB_USER=sleepsia
DB_PASSWORD=sleepsia

# API
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Logging
LOG_LEVEL=INFO
SQL_ECHO=False
```

Or use the provided `.env.example` in the project root and copy it:

```bash
cd ..
cp .env.example backend/.env
# Edit backend/.env with your database credentials
```

### 3. Verify Database

Ensure your MySQL database is running and contains the Sleepsia schema:

```bash
mysql -h localhost -u sleepsia -p sleepsia_reporting < ../sql/schema.sql
```

### 4. Run the Server

**Development** (with auto-reload):

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production** (using Gunicorn):

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5. Access the API

- **Base URL**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`
- **Readiness Check**: `http://localhost:8000/ready`

## API Endpoints Summary

### KPIs
- `GET /api/kpis` - Aggregate KPIs for date range
- `GET /api/kpis/by-date` - Daily KPIs time series

### Platform Analysis
- `GET /api/platform-performance` - All platforms comparison

### Product Analysis
- `GET /api/product-performance` - All products summary
- `GET /api/product-performance/top` - Top products by revenue
- `GET /api/product-performance/bottom` - Bottom products by contribution

### Warehouse Management
- `GET /api/warehouses` - All warehouses with inventory summary

### Inventory
- `GET /api/inventory` - All inventory items with pagination
- `GET /api/inventory/low-stock` - Low stock SKUs
- `GET /api/inventory/stockouts` - Out-of-stock SKUs

### Alerts
- `GET /api/alerts` - All active alerts

## Query Parameters

All endpoints support filtering by date range:

```
GET /api/kpis?start_date=2026-08-01&end_date=2026-08-21
```

### Common Parameters
- `start_date` (date, YYYY-MM-DD): Start of date range (default: 30 days ago)
- `end_date` (date, YYYY-MM-DD): End of date range (default: today)
- `platform_id` (string): Filter by platform (optional)
- `sku` (string): Filter by product SKU (optional)
- `skip` (integer): Pagination offset (default: 0)
- `limit` (integer): Pagination limit (default: 100, max: 1000)

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Run specific test file:

```bash
pytest tests/test_kpis.py -v
```

Run with coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database session management
│   ├── api/
│   │   ├── errors.py        # Exception handling
│   │   ├── dependencies.py  # Dependency injection
│   │   └── routes/
│   │       ├── kpis.py
│   │       ├── platforms.py
│   │       ├── products.py
│   │       ├── warehouses.py
│   │       ├── inventory.py
│   │       └── alerts.py
│   ├── schemas/
│   │   ├── common.py        # Shared models
│   │   ├── kpi_schemas.py
│   │   ├── platform_schemas.py
│   │   ├── product_schemas.py
│   │   ├── warehouse_schemas.py
│   │   ├── inventory_schemas.py
│   │   └── alert_schemas.py
│   ├── services/
│   │   ├── kpi_service.py
│   │   ├── platform_service.py
│   │   ├── product_service.py
│   │   ├── warehouse_service.py
│   │   ├── inventory_service.py
│   │   └── alert_service.py
│   ├── utils/
│   │   └── formatting.py
│   ├── models/
│   └── middleware/
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_kpis.py
│   ├── test_platforms.py
│   ├── test_products.py
│   ├── test_warehouses.py
│   ├── test_inventory.py
│   └── test_alerts.py
├── requirements.txt
└── BACKEND_README.md
```

## Error Handling

All error responses follow a consistent format:

```json
{
  "success": false,
  "error": "Error message here",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-08-23T12:00:00.000000"
}
```

## CORS Configuration

The backend is pre-configured to accept requests from:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)

To add more origins, update `CORS_ORIGINS` in `.env`:

```ini
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "https://yourdomain.com"]
```

## Database Views Used

The backend queries these pre-created MySQL views:

- `vw_daily_kpi_summary`: Daily aggregate KPIs
- `vw_platform_performance`: Platform-wise metrics
- `vw_product_performance`: Product-wise metrics
- `vw_product_platform_daily`: Detailed transaction data
- `vw_warehouse_summary`: Warehouse status and inventory
- `vw_inventory_health`: Current inventory levels
- `replenishment_alerts`: Alert data (table, not view)

All database schema is read-only from the API perspective.

## Troubleshooting

### Database Connection Error

```
Error: (2003, "Can't connect to MySQL server on 'localhost' (111)")
```

**Solution**: Verify MySQL is running and credentials in `.env` are correct.

```bash
mysql -h localhost -u sleepsia -p
```

### CORS Error in Browser

```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution**: Verify the frontend URL is in `CORS_ORIGINS` in `.env` and restart the server.

### Import Error: No module named 'app'

**Solution**: Ensure you're running from the `backend` directory or add it to Python path:

```bash
cd backend
python -m pytest tests/
```

## Development Workflow

1. **Create feature branch**: `git checkout -b feature/new-endpoint`
2. **Make changes** to routes, schemas, or services
3. **Write tests** in `tests/test_*.py`
4. **Run tests**: `pytest tests/ -v`
5. **Format code**: `black app/ tests/` (optional)
6. **Commit**: `git commit -m "feat: add new endpoint"`
7. **Test manually** with frontend

## Performance Considerations

- All queries use database views (pre-aggregated data)
- Pagination is enforced (max 1000 items)
- Date ranges limited to 365 days
- Database connection pooling is configured
- Indexes are defined on common filter columns

## Security

- No SQL injection: All queries use parameterized statements
- No credential exposure: Database passwords in environment variables
- CORS properly configured
- Errors don't expose internal details in production

## Logging

Logs are output to console with format:

```
2026-08-23 12:00:00,123 - app.services.kpi_service - INFO - Fetching KPIs for 2026-08-01 to 2026-08-21
```

Change `LOG_LEVEL` in `.env` to DEBUG for detailed logging:

```ini
LOG_LEVEL=DEBUG
```

## Next Steps

- Add authentication (OAuth2, JWT)
- Implement caching layer (Redis)
- Add request rate limiting
- Deploy to production (Docker, K8s)
- Set up CI/CD pipeline

## Support

For issues or questions:
1. Check the Swagger documentation at `/docs`
2. Review test cases in `tests/`
3. Check application logs for error details
4. Verify database connectivity with `GET /ready`
