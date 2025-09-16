"""Price calculation utilities for the trading engine."""

from decimal import ROUND_HALF_UP, Decimal


class PriceUtils:
    """Utility class for price calculations and formatting."""

    @staticmethod
    def round_price(price: Decimal, decimal_places: int = 8) -> Decimal:
        """Round price to specified decimal places."""
        quantize_str = "0." + "0" * decimal_places
        return price.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_percentage_change(old_price: Decimal, new_price: Decimal) -> Decimal:
        """Calculate percentage change between two prices."""
        if old_price == 0:
            return Decimal("0")

        change = ((new_price - old_price) / old_price) * 100
        return PriceUtils.round_price(change, 2)

    @staticmethod
    def calculate_average_price(prices: list[Decimal]) -> Decimal:
        """Calculate average price from a list of prices."""
        if not prices:
            return Decimal("0")

        total = sum(prices)
        return total / len(prices)

    @staticmethod
    def calculate_weighted_average_price(prices: list[Decimal], weights: list[Decimal]) -> Decimal:
        """Calculate weighted average price."""
        if not prices or not weights or len(prices) != len(weights):
            return Decimal("0")

        total_weighted = sum(price * weight for price, weight in zip(prices, weights, strict=False))
        total_weight = sum(weights)

        if total_weight == 0:
            return Decimal("0")

        return total_weighted / total_weight

    @staticmethod
    def calculate_price_range(high: Decimal, low: Decimal) -> Decimal:
        """Calculate price range (high - low)."""
        return high - low

    @staticmethod
    def calculate_midpoint_price(high: Decimal, low: Decimal) -> Decimal:
        """Calculate midpoint price between high and low."""
        return (high + low) / 2

    @staticmethod
    def is_price_within_range(price: Decimal, min_price: Decimal, max_price: Decimal) -> bool:
        """Check if price is within specified range."""
        return min_price <= price <= max_price

    @staticmethod
    def calculate_tick_size(price: Decimal, tick_size: Decimal) -> Decimal:
        """Round price to nearest tick size."""
        if tick_size == 0:
            return price

        return (price / tick_size).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * tick_size

    @staticmethod
    def format_price(price: Decimal, symbol: str = "$", decimal_places: int = 2) -> str:
        """Format price for display."""
        rounded_price = PriceUtils.round_price(price, decimal_places)
        return f"{symbol}{rounded_price:,.{decimal_places}f}"

    @staticmethod
    def parse_price_string(price_str: str) -> Decimal:
        """Parse price string to Decimal."""
        # Remove common currency symbols and commas
        cleaned = price_str.replace("$", "").replace(",", "").strip()
        try:
            return Decimal(cleaned)
        except Exception as e:
            raise ValueError(f"Invalid price string: {price_str}") from e
