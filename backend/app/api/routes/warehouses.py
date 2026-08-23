from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.database import get_db
from app.services.warehouse_service import WarehouseService
from app.schemas.warehouse_schemas import WarehouseListResponse

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get("", response_model=WarehouseListResponse)
async def get_warehouses(
    db: Session = Depends(get_db),
    filter_date: Optional[date] = Query(None),
    region: Optional[str] = Query(None),
):
    """Get all warehouses with inventory summary."""
    return WarehouseService.get_warehouses(db, filter_date, region)
