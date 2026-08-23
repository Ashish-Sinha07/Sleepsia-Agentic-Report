from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.database import get_db
from app.services.product_service import ProductService
from app.schemas.product_schemas import (
    ProductPerformanceResponse,
    TopProductsResponse,
)
from app.api.dependencies import get_date_range

router = APIRouter(prefix="/product-performance", tags=["Products"])


@router.get("", response_model=ProductPerformanceResponse)
async def get_product_performance(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    platform_id: Optional[str] = Query(None),
    sku: Optional[str] = Query(None),
):
    """Get performance metrics for all products."""
    start_date, end_date = date_range
    return ProductService.get_product_performance(
        db, start_date, end_date, platform_id, sku
    )


@router.get("/top", response_model=TopProductsResponse)
async def get_top_products(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("revenue"),
):
    """Get top products by specified metric."""
    start_date, end_date = date_range
    return ProductService.get_top_products(db, start_date, end_date, limit, sort_by)


@router.get("/bottom", response_model=TopProductsResponse)
async def get_bottom_products(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    limit: int = Query(10, ge=1, le=100),
):
    """Get bottom/unprofitable products by contribution."""
    start_date, end_date = date_range
    return ProductService.get_bottom_products(db, start_date, end_date, limit)
