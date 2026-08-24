"""
Query Service: Low-level data fetching from MySQL for business metrics.

This service provides the foundation for fetching sales, products, advertising,
costs, inventory, and warehouse data. All numerical answers originate from
deterministic queries to ensure accuracy and compliance with business rules.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List, Dict, Any
from decimal import Decimal


class QueryService:
    """Service for fetching business data from MySQL."""

    # ============================================================================
    # SALES DATA
    # ============================================================================

    @staticmethod
    def get_sales(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
        sku: Optional[str] = None,
        warehouse_id: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Fetch sales transactions with optional filters.

        Args:
            db: Database session
            start_date: Start date for sales range
            end_date: End date for sales range
            platform_id: Filter by platform (optional)
            sku: Filter by SKU (optional)
            warehouse_id: Filter by warehouse (optional)
            region: Filter by region (optional)
            limit: Number of records to return
            offset: Offset for pagination

        Returns:
            Dictionary with sales data and metadata
        """
        query = """
        SELECT
            date,
            platform_id,
            platform,
            sku,
            product_name,
            warehouse_id,
            warehouse_name,
            region,
            orders,
            units_sold,
            gross_sales,
            discount,
            net_sales,
            ad_sales,
            organic_sales,
            ad_spend,
            contribution_inr,
            profit_margin_pct,
            roas,
            acos_pct
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        if sku:
            query += " AND sku = :sku"
            params["sku"] = sku

        if warehouse_id:
            query += " AND warehouse_id = :warehouse_id"
            params["warehouse_id"] = warehouse_id

        if region:
            query += " AND region = :region"
            params["region"] = region

        # Count total matching records
        count_query = f"SELECT COUNT(*) FROM ({query}) as subq"
        total = db.execute(text(count_query), params).scalar() or 0

        # Add pagination and ordering
        query += " ORDER BY date DESC, platform, sku LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        results = db.execute(text(query), params).fetchall()

        sales_data = [
            {
                "date": row[0],
                "platform_id": row[1],
                "platform": row[2],
                "sku": row[3],
                "product_name": row[4],
                "warehouse_id": row[5],
                "warehouse_name": row[6],
                "region": row[7],
                "orders": row[8] or 0,
                "units_sold": row[9] or 0,
                "gross_sales": float(row[10]) if row[10] else 0.0,
                "discount": float(row[11]) if row[11] else 0.0,
                "net_sales": float(row[12]) if row[12] else 0.0,
                "ad_sales": float(row[13]) if row[13] else 0.0,
                "organic_sales": float(row[14]) if row[14] else 0.0,
                "ad_spend": float(row[15]) if row[15] else 0.0,
                "contribution_inr": float(row[16]) if row[16] else 0.0,
                "profit_margin_pct": float(row[17]) if row[17] else None,
                "roas": float(row[18]) if row[18] else None,
                "acos_pct": float(row[19]) if row[19] else None,
            }
            for row in results
        ]

        return {
            "data": sales_data,
            "total": total,
            "limit": limit,
            "offset": offset,
            "filters": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "platform_id": platform_id,
                "sku": sku,
                "warehouse_id": warehouse_id,
                "region": region,
            },
        }

    # ============================================================================
    # AGGREGATED SALES METRICS
    # ============================================================================

    @staticmethod
    def get_sales_summary(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
        sku: Optional[str] = None,
        group_by: str = "platform",
    ) -> Dict[str, Any]:
        """
        Get aggregated sales metrics grouped by specified dimension.

        Args:
            db: Database session
            start_date: Start date for aggregation
            end_date: End date for aggregation
            platform_id: Filter by platform (optional)
            sku: Filter by SKU (optional)
            group_by: Group by 'platform', 'sku', or 'date'

        Returns:
            Dictionary with aggregated sales metrics
        """
        # Determine grouping logic
        if group_by == "platform":
            group_cols = "platform_id, platform"
            order_by = "net_sales DESC"
        elif group_by == "sku":
            group_cols = "sku, product_name"
            order_by = "net_sales DESC"
        elif group_by == "date":
            group_cols = "date"
            order_by = "date DESC"
        else:
            group_cols = "platform_id, platform"
            order_by = "net_sales DESC"

        query = f"""
        SELECT
            {group_cols},
            COALESCE(SUM(orders), 0) as total_orders,
            COALESCE(SUM(units_sold), 0) as total_units,
            COALESCE(SUM(gross_sales), 0) as total_gross_sales,
            COALESCE(SUM(discount), 0) as total_discount,
            COALESCE(SUM(net_sales), 0) as total_net_sales,
            COALESCE(SUM(ad_sales), 0) as total_ad_sales,
            COALESCE(SUM(organic_sales), 0) as total_organic_sales,
            COALESCE(SUM(ad_spend), 0) as total_ad_spend,
            COALESCE(SUM(contribution_inr), 0) as total_contribution,
            COALESCE(AVG(profit_margin_pct), NULL) as avg_profit_margin,
            COALESCE(AVG(roas), NULL) as avg_roas,
            COALESCE(AVG(acos_pct), NULL) as avg_acos
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        if sku:
            query += " AND sku = :sku"
            params["sku"] = sku

        query += f" GROUP BY {group_cols} ORDER BY {order_by}"

        results = db.execute(text(query), params).fetchall()

        summary_data = []
        for row in results:
            if group_by == "date":
                summary_data.append({
                    "date": row[0],
                    "orders": row[1] or 0,
                    "units": row[2] or 0,
                    "gross_sales": float(row[3]) if row[3] else 0.0,
                    "discount": float(row[4]) if row[4] else 0.0,
                    "net_sales": float(row[5]) if row[5] else 0.0,
                    "ad_sales": float(row[6]) if row[6] else 0.0,
                    "organic_sales": float(row[7]) if row[7] else 0.0,
                    "ad_spend": float(row[8]) if row[8] else 0.0,
                    "contribution": float(row[9]) if row[9] else 0.0,
                    "profit_margin_pct": float(row[10]) if row[10] else None,
                    "roas": float(row[11]) if row[11] else None,
                    "acos_pct": float(row[12]) if row[12] else None,
                })
            elif group_by == "sku":
                summary_data.append({
                    "sku": row[0],
                    "product_name": row[1],
                    "orders": row[2] or 0,
                    "units": row[3] or 0,
                    "gross_sales": float(row[4]) if row[4] else 0.0,
                    "discount": float(row[5]) if row[5] else 0.0,
                    "net_sales": float(row[6]) if row[6] else 0.0,
                    "ad_sales": float(row[7]) if row[7] else 0.0,
                    "organic_sales": float(row[8]) if row[8] else 0.0,
                    "ad_spend": float(row[9]) if row[9] else 0.0,
                    "contribution": float(row[10]) if row[10] else 0.0,
                    "profit_margin_pct": float(row[11]) if row[11] else None,
                    "roas": float(row[12]) if row[12] else None,
                    "acos_pct": float(row[13]) if row[13] else None,
                })
            else:  # platform
                summary_data.append({
                    "platform_id": row[0],
                    "platform": row[1],
                    "orders": row[2] or 0,
                    "units": row[3] or 0,
                    "gross_sales": float(row[4]) if row[4] else 0.0,
                    "discount": float(row[5]) if row[5] else 0.0,
                    "net_sales": float(row[6]) if row[6] else 0.0,
                    "ad_sales": float(row[7]) if row[7] else 0.0,
                    "organic_sales": float(row[8]) if row[8] else 0.0,
                    "ad_spend": float(row[9]) if row[9] else 0.0,
                    "contribution": float(row[10]) if row[10] else 0.0,
                    "profit_margin_pct": float(row[11]) if row[11] else None,
                    "roas": float(row[12]) if row[12] else None,
                    "acos_pct": float(row[13]) if row[13] else None,
                })

        return {
            "data": summary_data,
            "total": len(summary_data),
            "group_by": group_by,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }

    # ============================================================================
    # PRODUCTS
    # ============================================================================

    @staticmethod
    def get_products(
        db: Session,
        limit: int = 1000,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get list of all products.

        Args:
            db: Database session
            limit: Number of records to return
            offset: Offset for pagination

        Returns:
            Dictionary with product list and metadata
        """
        query = """
        SELECT DISTINCT
            sku,
            product_name,
            product_category,
            product_subcategory
        FROM vw_product_platform_daily
        ORDER BY product_name
        """

        # Count total products
        count_query = """
        SELECT COUNT(DISTINCT sku)
        FROM vw_product_platform_daily
        """
        total = db.execute(text(count_query)).scalar() or 0

        # Add pagination
        query += " LIMIT :limit OFFSET :offset"

        results = db.execute(
            text(query),
            {"limit": limit, "offset": offset}
        ).fetchall()

        products = [
            {
                "sku": row[0],
                "product_name": row[1],
                "category": row[2],
                "subcategory": row[3],
            }
            for row in results
        ]

        return {
            "data": products,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    # ============================================================================
    # ADVERTISING
    # ============================================================================

    @staticmethod
    def get_advertising(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
        sku: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get advertising performance data.

        Args:
            db: Database session
            start_date: Start date for ad data
            end_date: End date for ad data
            platform_id: Filter by platform (optional)
            sku: Filter by SKU (optional)
            limit: Number of records to return
            offset: Offset for pagination

        Returns:
            Dictionary with advertising metrics
        """
        query = """
        SELECT
            date,
            platform_id,
            platform,
            sku,
            product_name,
            COALESCE(ad_spend, 0) as ad_spend,
            COALESCE(ad_sales, 0) as ad_sales,
            COALESCE(units_sold, 0) as units_sold,
            COALESCE(orders, 0) as orders,
            COALESCE(roas, NULL) as roas,
            COALESCE(acos_pct, NULL) as acos_pct
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        AND ad_spend > 0
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        if sku:
            query += " AND sku = :sku"
            params["sku"] = sku

        # Count total matching records
        count_query = f"SELECT COUNT(*) FROM ({query}) as subq"
        total = db.execute(text(count_query), params).scalar() or 0

        # Add pagination and ordering
        query += " ORDER BY date DESC, platform, sku LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        results = db.execute(text(query), params).fetchall()

        ad_data = [
            {
                "date": row[0],
                "platform_id": row[1],
                "platform": row[2],
                "sku": row[3],
                "product_name": row[4],
                "ad_spend": float(row[5]) if row[5] else 0.0,
                "ad_sales": float(row[6]) if row[6] else 0.0,
                "units_sold": row[7] or 0,
                "orders": row[8] or 0,
                "roas": float(row[9]) if row[9] else None,
                "acos_pct": float(row[10]) if row[10] else None,
            }
            for row in results
        ]

        return {
            "data": ad_data,
            "total": total,
            "limit": limit,
            "offset": offset,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }

    @staticmethod
    def get_advertising_summary(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get aggregated advertising metrics.

        Args:
            db: Database session
            start_date: Start date for aggregation
            end_date: End date for aggregation
            platform_id: Filter by platform (optional)

        Returns:
            Dictionary with aggregated ad metrics
        """
        query = """
        SELECT
            platform_id,
            platform,
            COALESCE(SUM(ad_spend), 0) as total_ad_spend,
            COALESCE(SUM(ad_sales), 0) as total_ad_sales,
            COALESCE(SUM(units_sold), 0) as total_units,
            COALESCE(SUM(orders), 0) as total_orders,
            COALESCE(AVG(roas), NULL) as avg_roas,
            COALESCE(AVG(acos_pct), NULL) as avg_acos
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        AND ad_spend > 0
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        query += " GROUP BY platform_id, platform ORDER BY total_ad_spend DESC"

        results = db.execute(text(query), params).fetchall()

        summary = [
            {
                "platform_id": row[0],
                "platform": row[1],
                "ad_spend": float(row[2]) if row[2] else 0.0,
                "ad_sales": float(row[3]) if row[3] else 0.0,
                "units": row[4] or 0,
                "orders": row[5] or 0,
                "roas": float(row[6]) if row[6] else None,
                "acos_pct": float(row[7]) if row[7] else None,
            }
            for row in results
        ]

        return {
            "data": summary,
            "total": len(summary),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }

    # ============================================================================
    # COSTS
    # ============================================================================

    @staticmethod
    def get_costs(
        db: Session,
        start_date: date,
        end_date: date,
        cost_type: Optional[str] = None,
        platform_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get cost-related data including product costs, platform fees, etc.

        Args:
            db: Database session
            start_date: Start date for cost data
            end_date: End date for cost data
            cost_type: Filter by cost type (optional)
            platform_id: Filter by platform (optional)

        Returns:
            Dictionary with cost metrics
        """
        query = """
        SELECT
            date,
            platform_id,
            platform,
            sku,
            product_name,
            COALESCE(net_sales, 0) as net_sales,
            COALESCE(gross_sales, 0) as gross_sales,
            COALESCE(discount, 0) as discount,
            COALESCE(ad_spend, 0) as ad_spend,
            COALESCE(contribution_inr, 0) as contribution,
            COALESCE(profit_margin_pct, NULL) as profit_margin_pct,
            units_sold
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        query += " ORDER BY date DESC, platform, sku"

        results = db.execute(text(query), params).fetchall()

        cost_data = [
            {
                "date": row[0],
                "platform_id": row[1],
                "platform": row[2],
                "sku": row[3],
                "product_name": row[4],
                "net_sales": float(row[5]) if row[5] else 0.0,
                "gross_sales": float(row[6]) if row[6] else 0.0,
                "discount": float(row[7]) if row[7] else 0.0,
                "ad_spend": float(row[8]) if row[8] else 0.0,
                "contribution": float(row[9]) if row[9] else 0.0,
                "profit_margin_pct": float(row[10]) if row[10] else None,
                "units_sold": row[11] or 0,
            }
            for row in results
        ]

        return {
            "data": cost_data,
            "total": len(cost_data),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }

    @staticmethod
    def get_costs_summary(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get aggregated cost metrics by platform.

        Args:
            db: Database session
            start_date: Start date for aggregation
            end_date: End date for aggregation
            platform_id: Filter by platform (optional)

        Returns:
            Dictionary with aggregated cost metrics
        """
        query = """
        SELECT
            platform_id,
            platform,
            COALESCE(SUM(gross_sales), 0) as total_gross_sales,
            COALESCE(SUM(discount), 0) as total_discount,
            COALESCE(SUM(net_sales), 0) as total_net_sales,
            COALESCE(SUM(ad_spend), 0) as total_ad_spend,
            COALESCE(SUM(contribution_inr), 0) as total_contribution,
            COALESCE(AVG(profit_margin_pct), NULL) as avg_profit_margin,
            COALESCE(SUM(units_sold), 0) as total_units
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        query += " GROUP BY platform_id, platform ORDER BY total_net_sales DESC"

        results = db.execute(text(query), params).fetchall()

        summary = [
            {
                "platform_id": row[0],
                "platform": row[1],
                "gross_sales": float(row[2]) if row[2] else 0.0,
                "discount": float(row[3]) if row[3] else 0.0,
                "net_sales": float(row[4]) if row[4] else 0.0,
                "ad_spend": float(row[5]) if row[5] else 0.0,
                "contribution": float(row[6]) if row[6] else 0.0,
                "profit_margin_pct": float(row[7]) if row[7] else None,
                "units": row[8] or 0,
            }
            for row in results
        ]

        return {
            "data": summary,
            "total": len(summary),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }

    # ============================================================================
    # INVENTORY
    # ============================================================================

    @staticmethod
    def get_inventory(
        db: Session,
        filter_date: Optional[date] = None,
        warehouse_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get inventory levels by warehouse and SKU.

        Args:
            db: Database session
            filter_date: Date for inventory snapshot (defaults to today)
            warehouse_id: Filter by warehouse (optional)
            status: Filter by stock status (optional)
            limit: Number of records to return
            offset: Offset for pagination

        Returns:
            Dictionary with inventory data
        """
        if filter_date is None:
            filter_date = date.today()

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
        ).scalar() or 0

        # Add pagination and ordering
        query += " ORDER BY warehouse_id, sku LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        results = db.execute(text(query), params).fetchall()

        inventory = [
            {
                "warehouse_id": row[0],
                "warehouse_name": row[1],
                "sku": row[2],
                "product_name": row[3],
                "closing_stock": row[4] or 0,
                "avg_daily_demand_7d": float(row[5]) if row[5] else 0.0,
                "days_of_cover": float(row[6]) if row[6] else None,
                "reorder_point": row[7] or 0,
                "recommended_reorder_qty": row[8] or 0,
                "stock_status": row[9] or "Unknown",
            }
            for row in results
        ]

        return {
            "data": inventory,
            "total": count_result,
            "limit": limit,
            "offset": offset,
            "filter_date": filter_date.isoformat(),
        }

    @staticmethod
    def get_inventory_summary(
        db: Session,
        filter_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Get aggregated inventory summary by warehouse.

        Args:
            db: Database session
            filter_date: Date for inventory snapshot (defaults to today)

        Returns:
            Dictionary with inventory summary
        """
        if filter_date is None:
            filter_date = date.today()

        query = """
        SELECT
            warehouse_id,
            warehouse_name,
            COALESCE(SUM(CASE WHEN stock_status = 'Healthy' THEN 1 ELSE 0 END), 0) as healthy_skus,
            COALESCE(SUM(CASE WHEN stock_status = 'Low Stock' THEN 1 ELSE 0 END), 0) as low_stock_skus,
            COALESCE(SUM(CASE WHEN stock_status = 'Critical' THEN 1 ELSE 0 END), 0) as critical_skus,
            COALESCE(SUM(CASE WHEN stock_status = 'Stockout' THEN 1 ELSE 0 END), 0) as stockout_skus,
            COALESCE(SUM(closing_stock), 0) as total_inventory
        FROM vw_inventory_health
        WHERE date = :filter_date
        GROUP BY warehouse_id, warehouse_name
        ORDER BY warehouse_name
        """

        results = db.execute(text(query), {"filter_date": filter_date}).fetchall()

        summary = [
            {
                "warehouse_id": row[0],
                "warehouse_name": row[1],
                "healthy_skus": row[2] or 0,
                "low_stock_skus": row[3] or 0,
                "critical_skus": row[4] or 0,
                "stockout_skus": row[5] or 0,
                "total_inventory": row[6] or 0,
            }
            for row in results
        ]

        return {
            "data": summary,
            "total": len(summary),
            "filter_date": filter_date.isoformat(),
        }

    # ============================================================================
    # WAREHOUSES
    # ============================================================================

    @staticmethod
    def get_warehouses(
        db: Session,
        filter_date: Optional[date] = None,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get warehouse information with inventory health.

        Args:
            db: Database session
            filter_date: Date for inventory snapshot (defaults to today)
            region: Filter by region (optional)

        Returns:
            Dictionary with warehouse data
        """
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
            {
                "warehouse_id": row[0],
                "warehouse_name": row[1],
                "region": row[2],
                "zone": row[3],
                "city": row[4],
                "latitude": float(row[5]) if row[5] else None,
                "longitude": float(row[6]) if row[6] else None,
                "healthy_skus": row[7] or 0,
                "low_stock_skus": row[8] or 0,
                "critical_skus": row[9] or 0,
                "stockout_skus": row[10] or 0,
                "total_inventory": row[11] or 0,
                "warehouse_health": row[12] or "Unknown",
            }
            for row in results
        ]

        return {
            "data": warehouses,
            "total": len(warehouses),
        }

    @staticmethod
    def get_warehouse_by_id(
        db: Session,
        warehouse_id: str,
    ) -> Dict[str, Any]:
        """
        Get detailed information for a specific warehouse.

        Args:
            db: Database session
            warehouse_id: Warehouse ID to fetch

        Returns:
            Dictionary with warehouse details
        """
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
        WHERE w.warehouse_id = :warehouse_id
        """

        result = db.execute(
            text(query),
            {"warehouse_id": warehouse_id}
        ).fetchone()

        if not result:
            return {"data": None, "error": "Warehouse not found"}

        warehouse = {
            "warehouse_id": result[0],
            "warehouse_name": result[1],
            "region": result[2],
            "zone": result[3],
            "city": result[4],
            "latitude": float(result[5]) if result[5] else None,
            "longitude": float(result[6]) if result[6] else None,
            "healthy_skus": result[7] or 0,
            "low_stock_skus": result[8] or 0,
            "critical_skus": result[9] or 0,
            "stockout_skus": result[10] or 0,
            "total_inventory": result[11] or 0,
            "warehouse_health": result[12] or "Unknown",
        }

        return {"data": warehouse}
