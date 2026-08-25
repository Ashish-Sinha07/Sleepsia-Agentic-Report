from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import sys
from pathlib import Path
from sqlalchemy import text
from app.config import settings
from app.api.errors import SleepsiaException

# Add parent directory to Python path for analytics module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.api.routes import kpis, platforms, products, warehouses, inventory, alerts, advertising, ai_assistant, reports

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    # Initialize database
    from app.database import init_db
    init_db()

    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(SleepsiaException)
    async def sleepsia_exception_handler(request: Request, exc: SleepsiaException):
        """Handle Sleepsia exceptions."""
        logger.error(f"Sleepsia exception: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.message,
                "error_code": exc.code,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error" if not settings.DEBUG else str(exc),
                "error_code": "INTERNAL_ERROR",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    # Health check endpoints
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

    @app.get("/ready")
    async def readiness_check(request: Request):
        """Readiness check endpoint - verify database connectivity."""
        try:
            from app.database import SessionLocal

            db = SessionLocal()
            # Simple query to verify database connection
            db.execute(text("SELECT 1"))
            db.close()
            return {
                "ready": True,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Readiness check failed: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "ready": False,
                    "error": "Database connection failed",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

    # Include routers
    app.include_router(kpis.router, prefix="/api")
    app.include_router(platforms.router, prefix="/api")
    app.include_router(products.router, prefix="/api")
    app.include_router(warehouses.router, prefix="/api")
    app.include_router(inventory.router, prefix="/api")
    app.include_router(alerts.router, prefix="/api")
    app.include_router(advertising.router, prefix="/api")
    app.include_router(ai_assistant.router, prefix="/api")
    app.include_router(reports.router, prefix="/api")

    logger.info(f"FastAPI app created with {len(app.routes)} routes")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
