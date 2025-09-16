"""Technical indicator calculations for trading strategies.

This module provides commonly used technical indicators that can be used
across different trading strategies. All indicators work with price and volume data.
"""

import math
from decimal import Decimal

from ..models import Candle

# Constants for magic number avoidance
MIN_CANDLES_FOR_TRUE_RANGE = 2
MIN_VALUES_FOR_CROSSOVER = 2


class MovingAverages:
    """Moving average calculations for prices and volumes."""

    @staticmethod
    def sma(values: list[Decimal], period: int) -> Decimal | None:
        """Calculate Simple Moving Average.

        Args:
            values: List of values (prices, volumes, etc.)
            period: Number of periods for the moving average

        Returns:
            SMA value or None if insufficient data
        """
        if len(values) < period:
            return None

        recent_values = values[-period:]
        return sum(recent_values) / period

    @staticmethod
    def sma_from_candles(candles: list[Candle], period: int, price_type: str = "close") -> Decimal | None:
        """Calculate SMA from candle data.

        Args:
            candles: List of candle data
            period: Number of periods for the moving average
            price_type: Type of price to use ("open", "high", "low", "close")

        Returns:
            SMA value or None if insufficient data
        """
        if len(candles) < period:
            return None

        if price_type == "open":
            values = [candle.open for candle in candles[-period:]]
        elif price_type == "high":
            values = [candle.high for candle in candles[-period:]]
        elif price_type == "low":
            values = [candle.low for candle in candles[-period:]]
        elif price_type == "close":
            values = [candle.close for candle in candles[-period:]]
        else:
            raise ValueError(f"Invalid price_type: {price_type}")

        return MovingAverages.sma(values, period)

    @staticmethod
    def volume_sma(candles: list[Candle], period: int) -> Decimal | None:
        """Calculate SMA of volume.

        Args:
            candles: List of candle data
            period: Number of periods for the moving average

        Returns:
            Volume SMA value or None if insufficient data
        """
        if len(candles) < period:
            return None

        volumes = [candle.volume for candle in candles[-period:]]
        return MovingAverages.sma(volumes, period)

    @staticmethod
    def ema(values: list[Decimal], period: int, smoothing: Decimal = Decimal("2")) -> Decimal | None:
        """Calculate Exponential Moving Average.

        Args:
            values: List of values
            period: Number of periods for the moving average
            smoothing: Smoothing factor (default 2)

        Returns:
            EMA value or None if insufficient data
        """
        if len(values) < period:
            return None

        # Calculate multiplier
        multiplier = smoothing / (period + 1)

        # Start with SMA for the first EMA value
        sma = MovingAverages.sma(values[:period], period)
        if sma is None:
            return None

        ema = sma

        # Calculate EMA for remaining values
        for value in values[period:]:
            ema = (value * multiplier) + (ema * (1 - multiplier))

        return ema

    @staticmethod
    def wma(values: list[Decimal], period: int) -> Decimal | None:
        """Calculate Weighted Moving Average.

        Args:
            values: List of values
            period: Number of periods for the moving average

        Returns:
            WMA value or None if insufficient data
        """
        if len(values) < period:
            return None

        recent_values = values[-period:]
        weights = [Decimal(str(i + 1)) for i in range(period)]

        weighted_sum = sum(value * weight for value, weight in zip(recent_values, weights, strict=False))
        weight_sum = sum(weights)

        return weighted_sum / weight_sum


class BollingerBands:
    """Bollinger Band calculations."""

    @staticmethod
    def calculate_bollinger_bands(
        values: list[Decimal], period: int, std_dev_multiplier: Decimal = Decimal("2")
    ) -> tuple[Decimal, Decimal, Decimal] | None:
        """Calculate Bollinger Bands.

        Args:
            values: List of price values
            period: Number of periods for the moving average
            std_dev_multiplier: Standard deviation multiplier (default 2)

        Returns:
            Tuple of (upper_band, middle_band, lower_band) or None if insufficient data
        """
        if len(values) < period:
            return None

        # Calculate middle band (SMA)
        middle_band = MovingAverages.sma(values, period)
        if middle_band is None:
            return None

        # Calculate standard deviation
        recent_values = values[-period:]
        variance = sum((value - middle_band) ** 2 for value in recent_values) / period
        std_dev = Decimal(str(math.sqrt(float(variance))))

        # Calculate bands
        upper_band = middle_band + (std_dev * std_dev_multiplier)
        lower_band = middle_band - (std_dev * std_dev_multiplier)

        return upper_band, middle_band, lower_band

    @staticmethod
    def bollinger_bands_from_candles(
        candles: list[Candle], period: int, std_dev_multiplier: Decimal = Decimal("2"), price_type: str = "close"
    ) -> tuple[Decimal, Decimal, Decimal] | None:
        """Calculate Bollinger Bands from candle data.

        Args:
            candles: List of candle data
            period: Number of periods for the moving average
            std_dev_multiplier: Standard deviation multiplier
            price_type: Type of price to use ("open", "high", "low", "close")

        Returns:
            Tuple of (upper_band, middle_band, lower_band) or None if insufficient data
        """
        if len(candles) < period:
            return None

        if price_type == "open":
            values = [candle.open for candle in candles]
        elif price_type == "high":
            values = [candle.high for candle in candles]
        elif price_type == "low":
            values = [candle.low for candle in candles]
        elif price_type == "close":
            values = [candle.close for candle in candles]
        else:
            raise ValueError(f"Invalid price_type: {price_type}")

        return BollingerBands.calculate_bollinger_bands(values, period, std_dev_multiplier)

    @staticmethod
    def bollinger_band_position(current_price: Decimal, upper: Decimal, lower: Decimal) -> Decimal:
        """Calculate position within Bollinger Bands (0-1 scale).

        Args:
            current_price: Current price
            upper: Upper Bollinger Band
            lower: Lower Bollinger Band

        Returns:
            Position within bands (0 = lower band, 1 = upper band, 0.5 = middle)
        """
        if upper == lower:
            return Decimal("0.5")

        return (current_price - lower) / (upper - lower)


class VolumeIndicators:
    """Volume-based technical indicators."""

    @staticmethod
    def volume_sma(candles: list[Candle], period: int) -> Decimal | None:
        """Calculate Simple Moving Average of volume."""
        return MovingAverages.volume_sma(candles, period)

    @staticmethod
    def volume_ratio(current_volume: Decimal, average_volume: Decimal) -> Decimal:
        """Calculate volume ratio compared to average.

        Args:
            current_volume: Current period volume
            average_volume: Average volume

        Returns:
            Volume ratio (1.0 = average, >1.0 = above average)
        """
        if average_volume == 0:
            return Decimal("0")
        return current_volume / average_volume

    @staticmethod
    def is_high_volume(current_volume: Decimal, average_volume: Decimal, threshold: Decimal = Decimal("1.5")) -> bool:
        """Check if current volume is significantly higher than average.

        Args:
            current_volume: Current period volume
            average_volume: Average volume
            threshold: Multiplier threshold (default 1.5x)

        Returns:
            True if volume is above threshold
        """
        ratio = VolumeIndicators.volume_ratio(current_volume, average_volume)
        return ratio >= threshold

    @staticmethod
    def on_balance_volume(candles: list[Candle]) -> list[Decimal]:
        """Calculate On-Balance Volume (OBV).

        Args:
            candles: List of candle data

        Returns:
            List of OBV values
        """
        if not candles:
            return []

        obv_values = [Decimal("0")]

        for i in range(1, len(candles)):
            prev_close = candles[i - 1].close
            current_close = candles[i].close
            current_volume = candles[i].volume

            if current_close > prev_close:
                # Price up, add volume
                obv_values.append(obv_values[-1] + current_volume)
            elif current_close < prev_close:
                # Price down, subtract volume
                obv_values.append(obv_values[-1] - current_volume)
            else:
                # Price unchanged, OBV unchanged
                obv_values.append(obv_values[-1])

        return obv_values


class PriceIndicators:
    """Price-based technical indicators."""

    @staticmethod
    def rsi(candles: list[Candle], period: int = 14) -> Decimal | None:
        """Calculate Relative Strength Index (RSI).

        Args:
            candles: List of candle data
            period: Number of periods (default 14)

        Returns:
            RSI value (0-100) or None if insufficient data
        """
        if len(candles) < period + 1:
            return None

        # Calculate price changes
        gains = []
        losses = []

        for i in range(1, len(candles)):
            change = candles[i].close - candles[i - 1].close
            if change > 0:
                gains.append(change)
                losses.append(Decimal("0"))
            elif change < 0:
                gains.append(Decimal("0"))
                losses.append(abs(change))
            else:
                gains.append(Decimal("0"))
                losses.append(Decimal("0"))

        if len(gains) < period:
            return None

        # Calculate average gains and losses
        avg_gain = MovingAverages.sma(gains[-period:], period)
        avg_loss = MovingAverages.sma(losses[-period:], period)

        if avg_loss == 0:
            return Decimal("100")  # RSI = 100 when no losses

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def typical_price(candle: Candle) -> Decimal:
        """Calculate typical price (HLC/3).

        Args:
            candle: Candle data

        Returns:
            Typical price
        """
        return (candle.high + candle.low + candle.close) / 3

    @staticmethod
    def true_range(candles: list[Candle]) -> list[Decimal]:
        """Calculate True Range for each candle.

        Args:
            candles: List of candle data

        Returns:
            List of True Range values
        """
        if len(candles) < MIN_CANDLES_FOR_TRUE_RANGE:
            return []

        tr_values = []

        for i in range(1, len(candles)):
            current = candles[i]
            previous = candles[i - 1]

            # True Range = max(high-low, |high-prev_close|, |low-prev_close|)
            hl = current.high - current.low
            hc = abs(current.high - previous.close)
            lc = abs(current.low - previous.close)

            tr = max(hl, hc, lc)
            tr_values.append(tr)

        return tr_values

    @staticmethod
    def atr(candles: list[Candle], period: int = 14) -> Decimal | None:
        """Calculate Average True Range (ATR).

        Args:
            candles: List of candle data
            period: Number of periods (default 14)

        Returns:
            ATR value or None if insufficient data
        """
        tr_values = PriceIndicators.true_range(candles)
        if len(tr_values) < period:
            return None

        return MovingAverages.sma(tr_values[-period:], period)


class TrendIndicators:
    """Trend-based technical indicators."""

    @staticmethod
    def macd(
        candles: list[Candle], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9
    ) -> tuple[Decimal, Decimal, Decimal] | None:
        """Calculate MACD (Moving Average Convergence Divergence).

        Args:
            candles: List of candle data
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line EMA period (default 9)

        Returns:
            Tuple of (macd_line, signal_line, histogram) or None if insufficient data
        """
        if len(candles) < slow_period:
            return None

        prices = [candle.close for candle in candles]

        # Calculate EMAs
        fast_ema = MovingAverages.ema(prices, fast_period)
        slow_ema = MovingAverages.ema(prices, slow_period)

        if fast_ema is None or slow_ema is None:
            return None

        # MACD line
        macd_line = fast_ema - slow_ema

        # For signal line, we'd need to calculate EMA of MACD values
        # Simplified version - return MACD line, 0 signal, macd histogram
        signal_line = Decimal("0")  # Simplified
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def price_change_percentage(current_price: Decimal, previous_price: Decimal) -> Decimal:
        """Calculate price change percentage.

        Args:
            current_price: Current price
            previous_price: Previous price

        Returns:
            Price change percentage
        """
        if previous_price == 0:
            return Decimal("0")
        return ((current_price - previous_price) / previous_price) * 100

    @staticmethod
    def is_uptrend(candles: list[Candle], lookback: int = 5) -> bool:
        """Check if price is in an uptrend.

        Args:
            candles: List of candle data
            lookback: Number of periods to look back

        Returns:
            True if in uptrend
        """
        if len(candles) < lookback + 1:
            return False

        recent_candles = candles[-lookback - 1 :]
        first_price = recent_candles[0].close
        last_price = recent_candles[-1].close

        return last_price > first_price

    @staticmethod
    def is_downtrend(candles: list[Candle], lookback: int = 5) -> bool:
        """Check if price is in a downtrend.

        Args:
            candles: List of candle data
            lookback: Number of periods to look back

        Returns:
            True if in downtrend
        """
        if len(candles) < lookback + 1:
            return False

        recent_candles = candles[-lookback - 1 :]
        first_price = recent_candles[0].close
        last_price = recent_candles[-1].close

        return last_price < first_price


class SupportResistance:
    """Support and resistance level calculations."""

    @staticmethod
    def find_local_highs(candles: list[Candle], lookback: int = 5) -> list[tuple[int, Decimal]]:
        """Find local high points in price data.

        Args:
            candles: List of candle data
            lookback: Number of periods to look back/forward

        Returns:
            List of (index, price) tuples for local highs
        """
        highs = []

        for i in range(lookback, len(candles) - lookback):
            current_high = candles[i].high

            # Check if this is higher than surrounding candles
            is_local_high = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and candles[j].high >= current_high:
                    is_local_high = False
                    break

            if is_local_high:
                highs.append((i, current_high))

        return highs

    @staticmethod
    def find_local_lows(candles: list[Candle], lookback: int = 5) -> list[tuple[int, Decimal]]:
        """Find local low points in price data.

        Args:
            candles: List of candle data
            lookback: Number of periods to look back/forward

        Returns:
            List of (index, price) tuples for local lows
        """
        lows = []

        for i in range(lookback, len(candles) - lookback):
            current_low = candles[i].low

            # Check if this is lower than surrounding candles
            is_local_low = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and candles[j].low <= current_low:
                    is_local_low = False
                    break

            if is_local_low:
                lows.append((i, current_low))

        return lows

    @staticmethod
    def calculate_support_resistance_levels(
        candles: list[Candle], lookback: int = 10, min_touches: int = 2
    ) -> tuple[list[Decimal], list[Decimal]]:
        """Calculate support and resistance levels.

        Args:
            candles: List of candle data
            lookback: Lookback period for finding highs/lows
            min_touches: Minimum number of touches to confirm level

        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        highs = SupportResistance.find_local_highs(candles, lookback)
        lows = SupportResistance.find_local_lows(candles, lookback)

        # Group similar price levels (within 1% of each other)
        tolerance = Decimal("0.01")  # 1%

        resistance_levels = []
        support_levels = []

        # Process highs for resistance
        high_prices = [price for _, price in highs]
        resistance_levels = SupportResistance._group_similar_levels(high_prices, tolerance, min_touches)

        # Process lows for support
        low_prices = [price for _, price in lows]
        support_levels = SupportResistance._group_similar_levels(low_prices, tolerance, min_touches)

        return support_levels, resistance_levels

    @staticmethod
    def _group_similar_levels(prices: list[Decimal], tolerance: Decimal, min_touches: int) -> list[Decimal]:
        """Group similar price levels together."""
        if not prices:
            return []

        sorted_prices = sorted(prices)
        groups = []
        current_group = [sorted_prices[0]]

        for price in sorted_prices[1:]:
            # Check if price is within tolerance of current group average
            group_avg = sum(current_group) / len(current_group)
            price_diff = abs(price - group_avg) / group_avg

            if price_diff <= tolerance:
                current_group.append(price)
            else:
                # Finalize current group if it has enough touches
                if len(current_group) >= min_touches:
                    groups.append(sum(current_group) / len(current_group))
                current_group = [price]

        # Don't forget the last group
        if len(current_group) >= min_touches:
            groups.append(sum(current_group) / len(current_group))

        return groups


class IndicatorUtils:
    """Utility functions for technical indicators."""

    @staticmethod
    def crossover(values1: list[Decimal], values2: list[Decimal]) -> bool:
        """Check if values1 crosses above values2 (bullish crossover).

        Args:
            values1: First series (e.g., fast MA)
            values2: Second series (e.g., slow MA)

        Returns:
            True if bullish crossover occurred
        """
        if len(values1) < MIN_VALUES_FOR_CROSSOVER or len(values2) < MIN_VALUES_FOR_CROSSOVER:
            return False

        # Current: values1 > values2
        # Previous: values1 <= values2
        return values1[-1] > values2[-1] and values1[-2] <= values2[-2]

    @staticmethod
    def crossunder(values1: list[Decimal], values2: list[Decimal]) -> bool:
        """Check if values1 crosses below values2 (bearish crossover).

        Args:
            values1: First series (e.g., fast MA)
            values2: Second series (e.g., slow MA)

        Returns:
            True if bearish crossover occurred
        """
        if len(values1) < MIN_VALUES_FOR_CROSSOVER or len(values2) < MIN_VALUES_FOR_CROSSOVER:
            return False

        # Current: values1 < values2
        # Previous: values1 >= values2
        return values1[-1] < values2[-1] and values1[-2] >= values2[-2]

    @staticmethod
    def highest_high(candles: list[Candle], period: int) -> Decimal | None:
        """Find highest high in the given period.

        Args:
            candles: List of candle data
            period: Number of periods to look back

        Returns:
            Highest high value or None if insufficient data
        """
        if len(candles) < period:
            return None

        recent_candles = candles[-period:]
        return max(candle.high for candle in recent_candles)

    @staticmethod
    def lowest_low(candles: list[Candle], period: int) -> Decimal | None:
        """Find lowest low in the given period.

        Args:
            candles: List of candle data
            period: Number of periods to look back

        Returns:
            Lowest low value or None if insufficient data
        """
        if len(candles) < period:
            return None

        recent_candles = candles[-period:]
        return min(candle.low for candle in recent_candles)

    @staticmethod
    def price_range(candles: list[Candle], period: int) -> Decimal | None:
        """Calculate price range (highest high - lowest low) for the period.

        Args:
            candles: List of candle data
            period: Number of periods to look back

        Returns:
            Price range or None if insufficient data
        """
        highest = IndicatorUtils.highest_high(candles, period)
        lowest = IndicatorUtils.lowest_low(candles, period)

        if highest is None or lowest is None:
            return None

        return highest - lowest
