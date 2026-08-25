from fastapi import Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
from app.database import get_db
from app.config import settings
from app.api.errors import ValidationError


def get_date_range(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> tuple[date, date]:
    """
    Validate and return date range.
    Defaults to last 30 days if not specified.
    """
    today = date.today()

    if start_date is None:
        start_date = today - timedelta(days=settings.DEFAULT_DAYS_BACK)

    if end_date is None:
        end_date = today

    # Validate date range
    if start_date > end_date:
        raise ValidationError("start_date must be before or equal to end_date")

    # Check max range
    days_diff = (end_date - start_date).days
    if days_diff > settings.MAX_DATE_RANGE_DAYS:
        raise ValidationError(
            f"Date range cannot exceed {settings.MAX_DATE_RANGE_DAYS} days"
        )

    return start_date, end_date


def get_pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> tuple[int, int]:
    """Validate pagination parameters."""
    return skip, limit
