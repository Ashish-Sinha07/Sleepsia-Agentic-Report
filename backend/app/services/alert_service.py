from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.schemas.alert_schemas import AlertsResponse, Alert


class AlertService:
    """Service for alerts and monitoring."""

    @staticmethod
    def get_alerts(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        priority: Optional[str] = None,
        limit: int = 100,
    ) -> AlertsResponse:
        """Get active alerts from replenishment_alerts table within a date range.

        Alerts are sparse, sporadic events (not a daily snapshot for every
        SKU), so filtering to a single exact day - as this used to do - misses
        real alerts that fall on nearby dates within the user's selected
        range. Matching the range-based filtering used by every other
        endpoint (KPIs, platforms, products, ...) fixes that.
        """
        if start_date is None or end_date is None:
            try:
                bounds = db.execute(
                    text("SELECT MIN(alert_date), MAX(alert_date) FROM replenishment_alerts")
                ).first()
                min_date, max_date = (bounds[0], bounds[1]) if bounds else (None, None)
            except Exception:
                min_date, max_date = None, None
            if start_date is None:
                start_date = min_date or date.today()
            if end_date is None:
                end_date = max_date or date.today()

        query = """
        SELECT
            ra.alert_id,
            ra.priority,
            'Replenishment' as alert_type,
            ra.sku,
            p.product_name,
            ra.warehouse_id,
            ra.region,
            ra.stock_status,
            'Stock' as metric,
            ra.closing_stock as current_value,
            ra.reorder_point as threshold,
            COALESCE(ra.avg_daily_demand_7d, 0) as avg_daily_demand,
            COALESCE(ra.days_of_cover, 0) as days_of_cover,
            COALESCE(ra.recommended_reorder_qty, 0) as recommended_reorder_qty,
            ra.recommended_action,
            ra.alert_date
        FROM replenishment_alerts ra
        LEFT JOIN products p ON ra.sku = p.sku
        WHERE ra.alert_date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if priority:
            query += " AND priority = :priority"
            params["priority"] = priority

        query += " ORDER BY alert_date DESC LIMIT :limit"
        params["limit"] = limit

        results = db.execute(text(query), params).fetchall()

        # Map priority to severity
        priority_to_severity = {
            "Critical": "CRITICAL",
            "High": "HIGH",
            "Medium": "MEDIUM",
            "Low": "LOW",
        }

        alerts = [
            Alert(
                alert_id=str(row[0]),
                severity=priority_to_severity.get(row[1], "MEDIUM"),
                alert_type=row[2],
                entity=row[3],
                product_name=row[4],
                warehouse=row[5],
                region=row[6],
                metric=row[8],
                current_value=int(row[9]),
                threshold=int(row[10]),
                gap=int(row[9]) - int(row[10]),
                avg_daily_demand=int(row[11]),
                days_of_cover=float(row[12]),
                recommended_reorder_qty=int(row[13]),
                stock_status=row[7],
                recommendation=row[14],
                created_at=row[15],
            )
            for row in results
        ]

        # Count by severity
        critical_count = sum(1 for a in alerts if a.severity == "CRITICAL")
        high_count = sum(1 for a in alerts if a.severity == "HIGH")
        medium_count = sum(1 for a in alerts if a.severity == "MEDIUM")

        return AlertsResponse(
            alerts=alerts,
            total=len(alerts),
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
        )

    @staticmethod
    def get_alerts_summary(
        db: Session,
        filter_date: Optional[date] = None,
    ) -> dict:
        """Get alert counts by severity."""
        if filter_date is None:
            filter_date = date.today()

        query = """
        SELECT
            priority,
            COUNT(*) as count
        FROM replenishment_alerts
        WHERE alert_date = :filter_date
        GROUP BY priority
        """

        results = db.execute(
            text(query),
            {"filter_date": filter_date},
        ).fetchall()

        counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for row in results:
            priority = row[0].lower() if row[0] else "low"
            counts[priority] = row[1]

        return counts
