from decimal import Decimal


def format_currency(value: Decimal) -> str:
    """Format decimal as Indian currency."""
    if not value:
        return "₹0"
    if value >= 10000000:
        return f"₹{(value / 10000000):.2f}Cr"
    if value >= 100000:
        return f"₹{(value / 100000):.2f}L"
    return f"₹{value:,.0f}"


def format_percentage(value: Decimal) -> str:
    """Format as percentage."""
    if not value:
        return "0%"
    return f"{float(value):.2f}%"


def format_roas(value: Decimal) -> str:
    """Format as ROAS multiplier."""
    if not value:
        return "0x"
    return f"{float(value):.2f}x"


def format_units(value: int) -> str:
    """Format units with K/M suffixes."""
    if value >= 1000000:
        return f"{(value / 1000000):.2f}M"
    if value >= 1000:
        return f"{(value / 1000):.2f}K"
    return str(value)
