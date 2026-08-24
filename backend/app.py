"""FastAPI application for Sleepsia Agentic Reporting System."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routes import (
    kpis,
    platform_performance,
    product_performance,
    advertising,
    profitability,
    inventory,
    warehouses,
    alerts,
    ai_assistant,
    reports,
)
from backend.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sleepsia Agentic Reporting System",
    description="Business Intelligence and Analytics API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(kpis.router, prefix="/api", tags=["KPIs"])
app.include_router(platform_performance.router, prefix="/api", tags=["Platform Performance"])
app.include_router(product_performance.router, prefix="/api", tags=["Product Performance"])
app.include_router(advertising.router, prefix="/api", tags=["Advertising"])
app.include_router(profitability.router, prefix="/api", tags=["Profitability"])
app.include_router(inventory.router, prefix="/api", tags=["Inventory"])
app.include_router(warehouses.router, prefix="/api", tags=["Warehouses"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(ai_assistant.router, prefix="/api", tags=["AI Assistant"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Sleepsia Agentic Reporting System",
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check logs for details."},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
