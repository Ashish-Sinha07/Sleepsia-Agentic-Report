from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.database import get_db
from app.services.inventory_service import InventoryService
from app.schemas.inventory_schemas import InventoryListResponse

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=InventoryListResponse)
async def get_inventory(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    warehouse_id: Optional[str] = Query(None),
    sku: Optional[str] = Query(None),
    platform_id: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get inventory items with pagination."""
    # Use start_date if provided, otherwise use end_date, otherwise use None (defaults to latest)
    filter_date = start_date or end_date
    return InventoryService.get_inventory(
        db, filter_date, warehouse_id, sku, platform_id, region, status, limit, skip
    )


@router.get("/low-stock", response_model=InventoryListResponse)
async def get_low_stock(
    db: Session = Depends(get_db),
    filter_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get low stock items."""
    return InventoryService.get_low_stock(db, filter_date, limit)


@router.get("/stockouts", response_model=InventoryListResponse)
async def get_stockouts(
    db: Session = Depends(get_db),
    filter_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get stockout items."""
    return InventoryService.get_stockouts(db, filter_date, limit)
