from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from decimal import Decimal
from backend.app.schemas.product_schemas import (
    ProductPerformanceResponse,
    ProductMetric,
    TopProductsResponse,
)


class ProductService:
    """Service for product analysis."""

    @staticmethod
    def get_product_performance(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
        sku: Optional[str] = None,
    ) -> ProductPerformanceResponse:
        """Get performance metrics for all products."""
        query = """
        SELECT
            sku,
            product_name,
            platform_id,
            platform,
            COALESCE(SUM(gross_sales), 0) as gross_sales,
            COALESCE(SUM(net_sales), 0) as net_sales,
            COALESCE(SUM(units_sold), 0) as units_sold,
            COALESCE(SUM(orders), 0) as orders,
            COALESCE(SUM(ad_spend), 0) as ad_spend,
            COALESCE(AVG(roas), NULL) as roas,
            COALESCE(AVG(acos_pct), NULL) as acos,
            COALESCE(SUM(contribution_inr), 0) as contribution,
            COALESCE(AVG(profit_margin_pct), NULL) as profit_margin,
            COALESCE(SUM(units_returned), 0) as units_returned,
            COALESCE(SUM(units_cancelled), 0) as units_cancelled,
            COALESCE(AVG(organic_share_pct), NULL) as organic_share
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

        query += " GROUP BY sku, product_name, platform_id, platform ORDER BY net_sales DESC"

        results = db.execute(text(query), params).fetchall()

        products = []
        for row in results:
            units_sold = row[6] or 0

            metric = ProductMetric(
                sku=row[0],
                product_name=row[1],
                platform_id=row[2],
                platform=row[3],
                revenue=row[5] or Decimal(0),
                units_sold=units_sold,
                orders=row[7] or 0,
                ad_spend=row[8] or Decimal(0),
                roas=row[9],
                acos_pct=row[10],
                contribution=row[11] or Decimal(0),
                profit_margin_pct=row[12],
                units_returned=row[13] or 0,
                units_cancelled=row[14] or 0,
                ad_share_pct=row[15],
                margin=row[12],  # For frontend compatibility
            )
            products.append(metric)

        return ProductPerformanceResponse(
            products=products,
            total=len(products),
        )

    @staticmethod
    def get_top_products(
        db: Session,
        start_date: date,
        end_date: date,
        limit: int = 10,
        sort_by: str = "revenue",
    ) -> TopProductsResponse:
        """Get top products by specified metric."""
        # Determine sort column
        sort_column = {
            "revenue": "net_sales",
            "contribution": "contribution_inr",
            "units": "units_sold",
            "margin": "profit_margin_pct",
        }.get(sort_by, "net_sales")

        query = f"""
        SELECT
            sku,
            product_name,
            NULL as platform_id,
            NULL as platform,
            COALESCE(SUM(gross_sales), 0) as gross_sales,
            COALESCE(SUM(net_sales), 0) as net_sales,
            COALESCE(SUM(units_sold), 0) as units_sold,
            COALESCE(SUM(orders), 0) as orders,
            COALESCE(SUM(ad_spend), 0) as ad_spend,
            COALESCE(AVG(roas), NULL) as roas,
            COALESCE(AVG(acos_pct), NULL) as acos,
            COALESCE(SUM(contribution_inr), 0) as contribution,
            COALESCE(AVG(profit_margin_pct), NULL) as profit_margin,
            COALESCE(SUM(units_returned), 0) as units_returned,
            COALESCE(SUM(units_cancelled), 0) as units_cancelled,
            COALESCE(AVG(organic_share_pct), NULL) as organic_share
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        GROUP BY sku, product_name
        ORDER BY {sort_column} DESC
        LIMIT :limit
        """

        results = db.execute(
            text(query),
            {"start_date": start_date, "end_date": end_date, "limit": limit},
        ).fetchall()

        products = [
            ProductMetric(
                sku=row[0],
                product_name=row[1],
                revenue=row[5] or Decimal(0),
                units_sold=row[6] or 0,
                orders=row[7] or 0,
                ad_spend=row[8] or Decimal(0),
                roas=row[9],
                acos_pct=row[10],
                contribution=row[11] or Decimal(0),
                profit_margin_pct=row[12],
                units_returned=row[13] or 0,
                units_cancelled=row[14] or 0,
                ad_share_pct=row[15],
            )
            for row in results
        ]

        return TopProductsResponse(
            products=products,
            total=len(products),
            sort_by=sort_by,
            limit=limit,
        )

    @staticmethod
    def get_bottom_products(
        db: Session,
        start_date: date,
        end_date: date,
        limit: int = 10,
    ) -> TopProductsResponse:
        """Get bottom/unprofitable products by contribution."""
        query = """
        SELECT
            sku,
            product_name,
            NULL as platform_id,
            NULL as platform,
            COALESCE(SUM(gross_sales), 0) as gross_sales,
            COALESCE(SUM(net_sales), 0) as net_sales,
            COALESCE(SUM(units_sold), 0) as units_sold,
            COALESCE(SUM(orders), 0) as orders,
            COALESCE(SUM(ad_spend), 0) as ad_spend,
            COALESCE(AVG(roas), NULL) as roas,
            COALESCE(AVG(acos_pct), NULL) as acos,
            COALESCE(SUM(contribution_inr), 0) as contribution,
            COALESCE(AVG(profit_margin_pct), NULL) as profit_margin,
            COALESCE(SUM(units_returned), 0) as units_returned,
            COALESCE(SUM(units_cancelled), 0) as units_cancelled,
            COALESCE(AVG(organic_share_pct), NULL) as organic_share
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        GROUP BY sku, product_name
        ORDER BY contribution ASC
        LIMIT :limit
        """

        results = db.execute(
            text(query),
            {"start_date": start_date, "end_date": end_date, "limit": limit},
        ).fetchall()

        products = [
            ProductMetric(
                sku=row[0],
                product_name=row[1],
                revenue=row[5] or Decimal(0),
                units_sold=row[6] or 0,
                orders=row[7] or 0,
                ad_spend=row[8] or Decimal(0),
                roas=row[9],
                acos_pct=row[10],
                contribution=row[11] or Decimal(0),
                profit_margin_pct=row[12],
                units_returned=row[13] or 0,
                units_cancelled=row[14] or 0,
                ad_share_pct=row[15],
            )
            for row in results
        ]

        return TopProductsResponse(
            products=products,
            total=len(products),
            sort_by="contribution",
            limit=limit,
        )
