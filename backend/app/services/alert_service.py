from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from backend.app.schemas.alert_schemas import AlertsResponse, Alert


class AlertService:
    """Service for alerts and monitoring."""

    @staticmethod
    def get_alerts(
        db: Session,
        filter_date: Optional[date] = None,
        priority: Optional[str] = None,
        limit: int = 100,
    ) -> AlertsResponse:
        """Get active alerts from replenishment_alerts table."""
        if filter_date is None:
            filter_date = date.today()

        query = """
        SELECT
            alert_id,
            priority,
            'Replenishment' as alert_type,
            sku,
            warehouse_id,
            stock_status,
            'Stock' as metric,
            CAST(closing_stock AS CHAR) as current_value,
            CAST(reorder_point AS CHAR) as threshold,
            recommended_action,
            alert_date
        FROM replenishment_alerts
        WHERE alert_date = :filter_date
        """

        params = {"filter_date": filter_date}

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
                platform=row[4],
                metric=row[6],
                current_value=row[7],
                threshold=row[8],
                recommendation=row[9],
                created_at=row[10],
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
