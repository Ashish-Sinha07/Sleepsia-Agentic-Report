from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from decimal import Decimal
from backend.app.schemas.warehouse_schemas import WarehouseListResponse, WarehouseInfo


class WarehouseService:
    """Service for warehouse operations."""

    @staticmethod
    def get_warehouses(
        db: Session,
        filter_date: Optional[date] = None,
        region: Optional[str] = None,
    ) -> WarehouseListResponse:
        """Get all warehouses with inventory summary."""
        if filter_date is None:
            filter_date = date.today()

        query = """
        SELECT
            w.warehouse_id,
            w.warehouse_name,
            w.region,
            w.zone,
            w.city,
            w.latitude,
            w.longitude,
            COALESCE(ws.healthy_skus, 0) as healthy_skus,
            COALESCE(ws.low_stock_skus, 0) as low_stock_skus,
            COALESCE(ws.critical_skus, 0) as critical_skus,
            COALESCE(ws.stockout_skus, 0) as stockout_skus,
            COALESCE(ws.total_stock_units, 0) as total_stock_units,
            COALESCE(ws.warehouse_health, 'Unknown') as warehouse_health
        FROM warehouses w
        LEFT JOIN vw_warehouse_summary ws ON w.warehouse_id = ws.warehouse_id
        WHERE 1=1
        """

        params = {}

        if region:
            query += " AND w.region = :region"
            params["region"] = region

        query += " ORDER BY w.warehouse_name"

        results = db.execute(text(query), params).fetchall()

        warehouses = [
            WarehouseInfo(
                warehouse_id=row[0],
                warehouse_name=row[1],
                region=row[2],
                zone=row[3],
                city=row[4],
                latitude=row[5],
                longitude=row[6],
                healthy_skus=row[7] or 0,
                low_stock_skus=row[8] or 0,
                lowStockSkus=row[8] or 0,  # For frontend
                critical_skus=row[9] or 0,
                stockout_skus=row[10] or 0,
                stockoutSkus=row[10] or 0,  # For frontend
                total_stock_units=row[11] or 0,
                totalInventory=row[11] or 0,  # For frontend
                warehouse_health=row[12] or "Unknown",
                health_status=row[12] or "Unknown",  # For frontend
            )
            for row in results
        ]

        return WarehouseListResponse(
            warehouses=warehouses,
            total=len(warehouses),
        )
