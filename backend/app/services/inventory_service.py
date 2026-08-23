from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from decimal import Decimal
from app.schemas.inventory_schemas import InventoryListResponse, InventoryItem


class InventoryService:
    """Service for inventory operations."""

    @staticmethod
    def get_inventory(
        db: Session,
        filter_date: Optional[date] = None,
        warehouse_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> InventoryListResponse:
        """Get inventory items with pagination."""
        if filter_date is None:
            filter_date = date.today()

        # Use vw_inventory_health for current inventory data
        query = """
        SELECT
            warehouse_id,
            warehouse_name,
            sku,
            product_name,
            closing_stock,
            avg_daily_demand_7d,
            days_of_cover,
            reorder_point,
            recommended_reorder_qty,
            stock_status
        FROM vw_inventory_health
        WHERE date = :filter_date
        """

        params = {"filter_date": filter_date}

        if warehouse_id:
            query += " AND warehouse_id = :warehouse_id"
            params["warehouse_id"] = warehouse_id

        if status:
            query += " AND stock_status = :status"
            params["status"] = status

        # Count total
        count_result = db.execute(
            text(f"SELECT COUNT(*) FROM ({query}) as subq"),
            params,
        ).scalar()

        # Add pagination and ordering
        query += " ORDER BY warehouse_id, sku LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        results = db.execute(text(query), params).fetchall()

        inventory = [
            InventoryItem(
                warehouse_id=row[0],
                warehouse_name=row[1],
                sku=row[2],
                product_name=row[3],
                closing_stock=row[4] or 0,
                avg_daily_demand_7d=row[5] or 0,
                days_of_cover=row[6],
                reorder_point=row[7] or 0,
                recommended_reorder_qty=row[8] or 0,
                stock_status=row[9] or "Unknown",
            )
            for row in results
        ]

        return InventoryListResponse(
            inventory=inventory,
            total=count_result or 0,
        )

    @staticmethod
    def get_low_stock(
        db: Session,
        filter_date: Optional[date] = None,
        limit: int = 100,
    ) -> InventoryListResponse:
        """Get low stock items."""
        return InventoryService.get_inventory(
            db,
            filter_date=filter_date,
            status="Low Stock",
            limit=limit,
        )

    @staticmethod
    def get_stockouts(
        db: Session,
        filter_date: Optional[date] = None,
        limit: int = 100,
    ) -> InventoryListResponse:
        """Get stockout items."""
        return InventoryService.get_inventory(
            db,
            filter_date=filter_date,
            status="Stockout",
            limit=limit,
        )
