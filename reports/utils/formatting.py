"""
Formatting Utilities for Reports

Provides consistent formatting for currency, percentages, units, and other metrics
used in PDF and Excel reports.

All formatting functions follow Indian numbering conventions where applicable.
"""

from decimal import Decimal
from typing import Union, Optional


def format_currency(value: Union[int, float, Decimal], precision: int = 0) -> str:
    """
    Format currency value in Indian Rupees.

    Examples:
        format_currency(1000000) -> "₹10.00L"
        format_currency(100000) -> "₹1.00L"
        format_currency(5000) -> "₹5,000"

    Args:
        value: Numeric value to format
        precision: Decimal places (default 0 for INR)

    Returns:
        Formatted currency string with ₹ symbol and Indian units (L for Lakhs, Cr for Crores)
    """
    if value is None:
        return "₹0"

    val = Decimal(str(value))

    # Crore (10,000,000)
    if abs(val) >= Decimal("10000000"):
        crores = val / Decimal("10000000")
        return f"₹{crores:.2f}Cr"

    # Lakh (100,000)
    if abs(val) >= Decimal("100000"):
        lakhs = val / Decimal("100000")
        return f"₹{lakhs:.2f}L"

    # Regular rupees with comma separator
    int_val = int(val)
    return f"₹{int_val:,}"


def format_percentage(value: Union[int, float, Decimal], precision: int = 2) -> str:
    """
    Format percentage value.

    Examples:
        format_percentage(23.456) -> "23.46%"
        format_percentage(5.1) -> "5.10%"

    Args:
        value: Numeric value (0-100)
        precision: Decimal places

    Returns:
        Formatted percentage string
    """
    if value is None:
        return "0.00%"

    val = Decimal(str(value))
    format_str = f"{{:.{precision}f}}%"
    return format_str.format(val)


def format_roas(value: Union[int, float, Decimal], precision: int = 2) -> str:
    """
    Format Return on Ad Spend as a multiplier.

    Examples:
        format_roas(2.5) -> "2.50x"
        format_roas(None) -> "—"

    Args:
        value: ROAS value (typically 1.5x to 3.5x)
        precision: Decimal places

    Returns:
        Formatted ROAS string with 'x' suffix
    """
    if value is None:
        return "—"

    val = Decimal(str(value))
    format_str = f"{{:.{precision}f}}x"
    return format_str.format(val)


def format_acos(value: Union[int, float, Decimal], precision: int = 2) -> str:
    """
    Format Ad Cost of Sale (ACOS) as percentage.

    ACOS is the inverse of ROAS - lower is better.

    Examples:
        format_acos(40.5) -> "40.50%"
        format_acos(None) -> "—"

    Args:
        value: ACOS value (typically 25% to 60%)
        precision: Decimal places

    Returns:
        Formatted ACOS string
    """
    if value is None:
        return "—"

    val = Decimal(str(value))
    format_str = f"{{:.{precision}f}}%"
    return format_str.format(val)


def format_units(value: Union[int, float, Decimal], precision: int = 2) -> str:
    """
    Format unit quantities with compact notation.

    Examples:
        format_units(1000000) -> "1.00M"
        format_units(50000) -> "50.00K"
        format_units(500) -> "500"

    Args:
        value: Number of units
        precision: Decimal places

    Returns:
        Formatted unit string
    """
    if value is None:
        return "0"

    val = Decimal(str(value))

    # Million
    if abs(val) >= Decimal("1000000"):
        millions = val / Decimal("1000000")
        format_str = f"{{:.{precision}f}}M"
        return format_str.format(millions)

    # Thousand
    if abs(val) >= Decimal("1000"):
        thousands = val / Decimal("1000")
        format_str = f"{{:.{precision}f}}K"
        return format_str.format(thousands)

    # Regular numbers
    return str(int(val))


def format_days(value: Union[int, float, Decimal], precision: int = 1) -> str:
    """
    Format days of cover or similar duration metrics.

    Examples:
        format_days(6.4) -> "6.4d"
        format_days(None) -> "—"

    Args:
        value: Number of days
        precision: Decimal places

    Returns:
        Formatted days string
    """
    if value is None:
        return "—"

    val = Decimal(str(value))
    format_str = f"{{:.{precision}f}}d"
    return format_str.format(val)


def format_ratio(value: Union[int, float, Decimal]) -> str:
    """
    Format numeric ratio (e.g., organic/paid split).

    Examples:
        format_ratio(1.5) -> "1.50"
        format_ratio(0.75) -> "0.75"

    Args:
        value: Ratio value

    Returns:
        Formatted ratio string
    """
    if value is None:
        return "—"

    val = Decimal(str(value))
    return f"{val:.2f}"


def status_badge(status: str) -> str:
    """
    Format status as a badge label.

    Examples:
        status_badge("HEALTHY") -> "✓ Healthy"
        status_badge("CRITICAL") -> "⚠ Critical"

    Args:
        status: Status string

    Returns:
        Formatted status badge
    """
    status_map = {
        "HEALTHY": "✓ Healthy",
        "LOW": "⚠ Low Stock",
        "CRITICAL": "⚠ Critical",
        "STOCKOUT": "✗ Stockout",
        "PROFITABLE": "✓ Profitable",
        "LOSS": "✗ Loss",
        "EFFICIENT": "✓ Efficient",
        "REVIEW": "⚠ Review",
        "INEFFICIENT": "✗ Inefficient",
    }
    return status_map.get(status, status)


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to maximum length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated text with '...' if needed
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def format_margin_color(margin: Decimal) -> str:
    """
    Determine color coding for margin values in reports.

    Used for visual emphasis in Excel and conditional formatting.

    Args:
        margin: Margin percentage value

    Returns:
        Color hex code or status indicator
    """
    margin_val = Decimal(str(margin))

    if margin_val >= Decimal("20"):
        return "GREEN"  # Healthy
    elif margin_val >= Decimal("5"):
        return "YELLOW"  # Moderate
    elif margin_val >= Decimal("0"):
        return "ORANGE"  # Low
    else:
        return "RED"  # Loss-making


def format_tacos_status(tacos: Decimal) -> str:
    """
    Determine status based on TACoS (Total Advertising Cost of Sales) efficiency.

    Args:
        tacos: TACoS percentage

    Returns:
        Status string: "Efficient", "Moderate", or "Inefficient"
    """
    tacos_val = Decimal(str(tacos))

    if tacos_val <= Decimal("20"):
        return "Efficient"
    elif tacos_val <= Decimal("30"):
        return "Moderate"
    else:
        return "Inefficient"


def format_return_rate_status(return_rate: Decimal) -> str:
    """
    Determine status based on return rate percentage.

    Args:
        return_rate: Return rate percentage

    Returns:
        Status string: "Excellent", "Good", "Concerning", or "Critical"
    """
    rate = Decimal(str(return_rate))

    if rate <= Decimal("1.5"):
        return "Excellent"
    elif rate <= Decimal("2.5"):
        return "Good"
    elif rate <= Decimal("4.0"):
        return "Concerning"
    else:
        return "Critical"
