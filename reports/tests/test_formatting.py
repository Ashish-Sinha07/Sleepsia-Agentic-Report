"""
Tests for formatting utilities.

Tests consistent formatting of currency, percentages, units, and other metrics.
"""

import pytest
from decimal import Decimal

from reports.utils.formatting import (
    format_currency,
    format_percentage,
    format_roas,
    format_acos,
    format_units,
    format_days,
    format_ratio,
    status_badge,
    truncate_text,
    format_margin_color,
    format_tacos_status,
    format_return_rate_status,
)


class TestCurrencyFormatting:
    """Test currency formatting function."""

    def test_format_large_amounts(self):
        """Test formatting of crore-level amounts."""
        assert format_currency(Decimal("10000000")) == "₹1.00Cr"
        assert format_currency(Decimal("50000000")) == "₹5.00Cr"

    def test_format_lakh_amounts(self):
        """Test formatting of lakh-level amounts."""
        assert format_currency(Decimal("100000")) == "₹1.00L"
        assert format_currency(Decimal("574500")) == "₹5.74L"
        assert format_currency(Decimal("1000000")) == "₹10.00L"

    def test_format_regular_amounts(self):
        """Test formatting of regular rupee amounts."""
        assert format_currency(Decimal("5000")) == "₹5,000"
        assert format_currency(Decimal("50000")) == "₹50,000"

    def test_format_small_amounts(self):
        """Test formatting of amounts under 1000."""
        assert format_currency(Decimal("500")) == "₹500"
        assert format_currency(Decimal("0")) == "₹0"

    def test_format_none_value(self):
        """Test formatting of None value."""
        assert format_currency(None) == "₹0"

    def test_format_negative_amounts(self):
        """Test formatting of negative amounts."""
        result = format_currency(Decimal("-100000"))
        assert "₹" in result
        assert "L" in result


class TestPercentageFormatting:
    """Test percentage formatting function."""

    def test_format_whole_percentages(self):
        """Test formatting whole numbers."""
        assert format_percentage(Decimal("50")) == "50.00%"
        assert format_percentage(Decimal("100")) == "100.00%"

    def test_format_decimal_percentages(self):
        """Test formatting decimal percentages."""
        assert format_percentage(Decimal("23.456")) == "23.46%"
        assert format_percentage(Decimal("5.1")) == "5.10%"

    def test_format_small_percentages(self):
        """Test formatting small percentages."""
        assert format_percentage(Decimal("0.5")) == "0.50%"
        assert format_percentage(Decimal("0.123")) == "0.12%"

    def test_format_precision_parameter(self):
        """Test precision parameter."""
        assert format_percentage(Decimal("23.456"), precision=1) == "23.5%"
        assert format_percentage(Decimal("23.456"), precision=3) == "23.456%"

    def test_format_none_value(self):
        """Test None value."""
        assert format_percentage(None) == "0.00%"


class TestROASFormatting:
    """Test ROAS (Return on Ad Spend) formatting."""

    def test_format_healthy_roas(self):
        """Test formatting of good ROAS values."""
        assert format_roas(Decimal("2.5")) == "2.50x"
        assert format_roas(Decimal("3.0")) == "3.00x"

    def test_format_none_roas(self):
        """Test None ROAS value."""
        assert format_roas(None) == "—"

    def test_format_low_roas(self):
        """Test formatting low ROAS."""
        assert format_roas(Decimal("0.8")) == "0.80x"


class TestUnitsFormatting:
    """Test unit quantity formatting."""

    def test_format_millions(self):
        """Test formatting of millions."""
        assert format_units(Decimal("1000000")) == "1.00M"
        assert format_units(Decimal("5000000")) == "5.00M"

    def test_format_thousands(self):
        """Test formatting of thousands."""
        assert format_units(Decimal("1000")) == "1.00K"
        assert format_units(Decimal("50000")) == "50.00K"

    def test_format_regular_units(self):
        """Test formatting of regular numbers."""
        assert format_units(Decimal("500")) == "500"
        assert format_units(Decimal("100")) == "100"

    def test_format_none_units(self):
        """Test None value."""
        assert format_units(None) == "0"


class TestDaysFormatting:
    """Test days of cover formatting."""

    def test_format_days(self):
        """Test formatting days of cover."""
        assert format_days(Decimal("6.4")) == "6.4d"
        assert format_days(Decimal("30.0")) == "30.0d"
        assert format_days(Decimal("0.5")) == "0.5d"

    def test_format_none_days(self):
        """Test None value."""
        assert format_days(None) == "—"


class TestStatusBadges:
    """Test status badge formatting."""

    def test_status_healthy(self):
        """Test healthy status."""
        assert status_badge("HEALTHY") == "✓ Healthy"

    def test_status_low(self):
        """Test low status."""
        assert status_badge("LOW") == "⚠ Low Stock"

    def test_status_critical(self):
        """Test critical status."""
        assert status_badge("CRITICAL") == "⚠ Critical"

    def test_status_stockout(self):
        """Test stockout status."""
        assert status_badge("STOCKOUT") == "✗ Stockout"

    def test_status_unknown(self):
        """Test unknown status returns as-is."""
        assert status_badge("UNKNOWN") == "UNKNOWN"


class TestTruncation:
    """Test text truncation."""

    def test_truncate_long_text(self):
        """Test truncation of long text."""
        result = truncate_text("This is a very long product name that exceeds maximum length", max_length=30)
        assert len(result) <= 30
        assert result.endswith("...")

    def test_truncate_short_text(self):
        """Test short text is not truncated."""
        result = truncate_text("Short", max_length=30)
        assert result == "Short"
        assert "..." not in result


class TestMarginColorCoding:
    """Test margin color coding for visual emphasis."""

    def test_high_margin_green(self):
        """Test high margin is green."""
        assert format_margin_color(Decimal("25")) == "GREEN"
        assert format_margin_color(Decimal("50")) == "GREEN"

    def test_moderate_margin_yellow(self):
        """Test moderate margin is yellow."""
        assert format_margin_color(Decimal("15")) == "YELLOW"
        assert format_margin_color(Decimal("18")) == "YELLOW"

    def test_low_margin_orange(self):
        """Test low margin is orange."""
        assert format_margin_color(Decimal("2.5")) == "ORANGE"
        assert format_margin_color(Decimal("4")) == "ORANGE"

    def test_negative_margin_red(self):
        """Test negative margin is red."""
        assert format_margin_color(Decimal("-10")) == "RED"
        assert format_margin_color(Decimal("-1")) == "RED"


class TestTACOSStatus:
    """Test TACoS (Total Advertising Cost of Sales) status."""

    def test_efficient_tacos(self):
        """Test efficient TACoS."""
        assert format_tacos_status(Decimal("15")) == "Efficient"
        assert format_tacos_status(Decimal("20")) == "Efficient"

    def test_moderate_tacos(self):
        """Test moderate TACoS."""
        assert format_tacos_status(Decimal("25")) == "Moderate"
        assert format_tacos_status(Decimal("30")) == "Moderate"

    def test_inefficient_tacos(self):
        """Test inefficient TACoS."""
        assert format_tacos_status(Decimal("40")) == "Inefficient"
        assert format_tacos_status(Decimal("50")) == "Inefficient"


class TestReturnRateStatus:
    """Test return rate status classification."""

    def test_excellent_return_rate(self):
        """Test excellent return rate."""
        assert format_return_rate_status(Decimal("1.0")) == "Excellent"
        assert format_return_rate_status(Decimal("1.5")) == "Excellent"

    def test_good_return_rate(self):
        """Test good return rate."""
        assert format_return_rate_status(Decimal("2.0")) == "Good"
        assert format_return_rate_status(Decimal("2.5")) == "Good"

    def test_concerning_return_rate(self):
        """Test concerning return rate."""
        assert format_return_rate_status(Decimal("3.0")) == "Concerning"
        assert format_return_rate_status(Decimal("4.0")) == "Concerning"

    def test_critical_return_rate(self):
        """Test critical return rate."""
        assert format_return_rate_status(Decimal("5.0")) == "Critical"
        assert format_return_rate_status(Decimal("10.0")) == "Critical"
