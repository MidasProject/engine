"""Example demonstrating the technical indicators utilities.

This example shows how to use various technical indicators:
- Simple Moving Averages (SMA) for prices and volumes
- Bollinger Bands
- RSI (Relative Strength Index)
- Volume indicators
- Support/Resistance levels
- Trend detection
"""

from decimal import Decimal

from engine import (
    BollingerBands,
    Candle,
    IndicatorUtils,
    MovingAverages,
    PriceIndicators,
    SupportResistance,
    TrendIndicators,
    VolumeIndicators,
)

# Constants to replace magic numbers
UPTREND_PERIOD = 20
SIDEWAYS_PERIOD = 35
MIN_CANDLES_FOR_VOLUME = 10
MIN_CANDLES_FOR_OBV = 5
RSI_OVERSOLD_THRESHOLD = 30
RSI_OVERBOUGHT_THRESHOLD = 70
MIN_CANDLES_FOR_PRICE_CHANGE = 2
MIN_CANDLES_FOR_SUPPORT_RESISTANCE = 20
MIN_VALUES_FOR_CROSSOVER = 2


def create_sample_price_data() -> list[Candle]:
    """Create sample candle data with realistic price movements."""
    candles = []
    base_price = Decimal("50000")

    # Create 50 candles with trending price action
    for i in range(50):
        # Create some realistic price movement
        if i < UPTREND_PERIOD:
            # Uptrend
            trend = Decimal(str(i * 50))
        elif i < SIDEWAYS_PERIOD:
            # Sideways with volatility
            trend = Decimal(str(UPTREND_PERIOD * 50 + (i % 3 - 1) * 100))
        else:
            # Downtrend
            trend = Decimal(str(UPTREND_PERIOD * 50 - (i - SIDEWAYS_PERIOD) * 80))

        # Add some randomness
        noise = Decimal(str((i % 7 - 3) * 20))
        current_price = base_price + trend + noise

        # Create realistic OHLC
        open_price = current_price - Decimal("10")
        high_price = current_price + Decimal("50")
        low_price = current_price - Decimal("50")
        close_price = current_price

        # Volume varies with price movement
        volume = Decimal("1.0") + Decimal(str(abs(i % 5))) * Decimal("0.5")

        candle = Candle(
            open_time=1640000000000 + (i * 60000),
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume,
            close_time=1640000000000 + (i * 60000) + 59999,
            quote_asset_volume=close_price * volume,
            number_of_trades=100 + i,
            taker_buy_base=volume * Decimal("0.6"),
            taker_buy_quote=close_price * volume * Decimal("0.6"),
        )
        candles.append(candle)

    return candles


def demonstrate_moving_averages(candles: list[Candle]) -> None:
    """Demonstrate moving average calculations."""
    print("\n📈 Moving Averages:")
    print("-" * 30)

    # SMA for different periods
    sma_10 = MovingAverages.sma_from_candles(candles, 10, "close")
    sma_20 = MovingAverages.sma_from_candles(candles, 20, "close")

    print(f"  SMA(10): ${sma_10:.2f}" if sma_10 else "  SMA(10): Not enough data")
    print(f"  SMA(20): ${sma_20:.2f}" if sma_20 else "  SMA(20): Not enough data")

    # Volume SMA
    volume_sma = MovingAverages.volume_sma(candles, 10)
    print(f"  Volume SMA(10): {volume_sma:.3f}" if volume_sma else "  Volume SMA(10): Not enough data")

    # EMA
    close_prices = [candle.close for candle in candles]
    ema_12 = MovingAverages.ema(close_prices, 12)
    print(f"  EMA(12): ${ema_12:.2f}" if ema_12 else "  EMA(12): Not enough data")


def demonstrate_bollinger_bands(candles: list[Candle]) -> None:
    """Demonstrate Bollinger Band calculations."""
    print("\n📊 Bollinger Bands:")
    print("-" * 30)

    bb_result = BollingerBands.bollinger_bands_from_candles(candles, 20, Decimal("2"), "close")

    if bb_result:
        upper, middle, lower = bb_result
        current_price = candles[-1].close

        print(f"  Upper Band: ${upper:.2f}")
        print(f"  Middle Band (SMA): ${middle:.2f}")
        print(f"  Lower Band: ${lower:.2f}")
        print(f"  Current Price: ${current_price:.2f}")

        # Calculate position within bands
        position = BollingerBands.bollinger_band_position(current_price, upper, lower)
        print(f"  Position in Bands: {position:.2%} (0%=lower, 100%=upper)")

        # Trading signals
        if position <= Decimal("0.1"):
            print("  📉 Signal: Near lower band - potential buy signal")
        elif position >= Decimal("0.9"):
            print("  📈 Signal: Near upper band - potential sell signal")
        else:
            print("  ➡️ Signal: Price within normal range")
    else:
        print("  Not enough data for Bollinger Bands")


def demonstrate_volume_indicators(candles: list[Candle]) -> None:
    """Demonstrate volume indicator calculations."""
    print("\n📊 Volume Indicators:")
    print("-" * 30)

    if len(candles) >= MIN_CANDLES_FOR_VOLUME:
        current_volume = candles[-1].volume
        avg_volume = VolumeIndicators.volume_sma(candles, MIN_CANDLES_FOR_VOLUME)

        if avg_volume:
            volume_ratio = VolumeIndicators.volume_ratio(current_volume, avg_volume)
            is_high_vol = VolumeIndicators.is_high_volume(current_volume, avg_volume)

            print(f"  Current Volume: {current_volume:.3f}")
            print(f"  Average Volume(10): {avg_volume:.3f}")
            print(f"  Volume Ratio: {volume_ratio:.2f}x")
            print(f"  High Volume: {'Yes' if is_high_vol else 'No'} (>1.5x average)")

    # On-Balance Volume
    if len(candles) >= MIN_CANDLES_FOR_OBV:
        obv_values = VolumeIndicators.on_balance_volume(candles[-5:])
        if obv_values:
            print(f"  OBV (last 5): {[float(v) for v in obv_values[-3:]]}")


def demonstrate_price_indicators(candles: list[Candle]) -> None:
    """Demonstrate price-based indicators."""
    print("\n💹 Price Indicators:")
    print("-" * 30)

    # RSI
    rsi = PriceIndicators.rsi(candles, 14)
    if rsi:
        print(f"  RSI(14): {rsi:.2f}")
        if rsi < RSI_OVERSOLD_THRESHOLD:
            print("  📉 RSI Signal: Oversold - potential buy signal")
        elif rsi > RSI_OVERBOUGHT_THRESHOLD:
            print("  📈 RSI Signal: Overbought - potential sell signal")
        else:
            print("  ➡️ RSI Signal: Neutral zone")

    # ATR
    atr = PriceIndicators.atr(candles, 14)
    if atr:
        print(f"  ATR(14): ${atr:.2f} (Average True Range)")

    # Price range
    price_range = IndicatorUtils.price_range(candles, 20)
    if price_range:
        print(f"  Price Range(20): ${price_range:.2f}")


def demonstrate_trend_indicators(candles: list[Candle]) -> None:
    """Demonstrate trend detection."""
    print("\n📈 Trend Analysis:")
    print("-" * 30)

    # Trend detection
    is_up = TrendIndicators.is_uptrend(candles, 10)
    is_down = TrendIndicators.is_downtrend(candles, 10)

    print(f"  Uptrend (10 periods): {'Yes' if is_up else 'No'}")
    print(f"  Downtrend (10 periods): {'Yes' if is_down else 'No'}")

    if not is_up and not is_down:
        print("  📊 Trend: Sideways/Consolidation")
    elif is_up:
        print("  📈 Trend: Bullish")
    elif is_down:
        print("  📉 Trend: Bearish")

    # Price change
    if len(candles) >= MIN_CANDLES_FOR_PRICE_CHANGE:
        current_price = candles[-1].close
        previous_price = candles[-2].close
        change_pct = TrendIndicators.price_change_percentage(current_price, previous_price)
        print(f"  Last Period Change: {change_pct:.2f}%")


def demonstrate_support_resistance(candles: list[Candle]) -> None:
    """Demonstrate support and resistance calculations."""
    print("\n🏗️ Support & Resistance:")
    print("-" * 30)

    if len(candles) >= MIN_CANDLES_FOR_SUPPORT_RESISTANCE:
        support_levels, resistance_levels = SupportResistance.calculate_support_resistance_levels(
            candles, lookback=5, min_touches=2
        )

        current_price = candles[-1].close

        print(f"  Current Price: ${current_price:.2f}")
        print(f"  Support Levels: {[f'${float(level):.2f}' for level in support_levels[:3]]}")
        print(f"  Resistance Levels: {[f'${float(level):.2f}' for level in resistance_levels[:3]]}")

        # Find nearest levels
        if support_levels:
            nearest_support = max(level for level in support_levels if level < current_price)
            distance_to_support = ((current_price - nearest_support) / current_price) * 100
            print(f"  Nearest Support: ${nearest_support:.2f} ({distance_to_support:.1f}% below)")

        if resistance_levels:
            nearest_resistance = min(level for level in resistance_levels if level > current_price)
            distance_to_resistance = ((nearest_resistance - current_price) / current_price) * 100
            print(f"  Nearest Resistance: ${nearest_resistance:.2f} ({distance_to_resistance:.1f}% above)")
    else:
        print("  Not enough data for support/resistance calculation")


def demonstrate_crossover_detection(candles: list[Candle]) -> None:
    """Demonstrate crossover detection."""
    print("\n🔄 Crossover Detection:")
    print("-" * 30)

    if len(candles) >= MIN_CANDLES_FOR_SUPPORT_RESISTANCE:
        # Calculate two different SMAs
        sma_values_10 = []
        sma_values_20 = []

        for i in range(len(candles)):
            candles_subset = candles[: i + 1]
            sma_10 = MovingAverages.sma_from_candles(candles_subset, 10, "close")
            sma_20 = MovingAverages.sma_from_candles(candles_subset, 20, "close")

            if sma_10 is not None:
                sma_values_10.append(sma_10)
            if sma_20 is not None:
                sma_values_20.append(sma_20)

        if len(sma_values_10) >= MIN_VALUES_FOR_CROSSOVER and len(sma_values_20) >= MIN_VALUES_FOR_CROSSOVER:
            bullish_cross = IndicatorUtils.crossover(sma_values_10, sma_values_20)
            bearish_cross = IndicatorUtils.crossunder(sma_values_10, sma_values_20)

            print(f"  SMA(10): ${sma_values_10[-1]:.2f}")
            print(f"  SMA(20): ${sma_values_20[-1]:.2f}")
            print(f"  Bullish Crossover: {'Yes' if bullish_cross else 'No'}")
            print(f"  Bearish Crossover: {'Yes' if bearish_cross else 'No'}")

            if bullish_cross:
                print("  🚀 Signal: Golden Cross - Strong buy signal!")
            elif bearish_cross:
                print("  📉 Signal: Death Cross - Strong sell signal!")
        else:
            print("  Not enough data for crossover detection")


def main():
    """Demonstrate all technical indicators."""
    print("📊 Technical Indicators Utilities Example")
    print("=" * 50)

    # Create sample data
    candles = create_sample_price_data()
    print(f"Generated {len(candles)} candles for analysis")
    print(f"Price range: ${candles[0].close:.2f} to ${candles[-1].close:.2f}")

    # Demonstrate each category of indicators
    demonstrate_moving_averages(candles)
    demonstrate_bollinger_bands(candles)
    demonstrate_volume_indicators(candles)
    demonstrate_price_indicators(candles)
    demonstrate_trend_indicators(candles)
    demonstrate_support_resistance(candles)
    demonstrate_crossover_detection(candles)

    print("\n✅ Technical Indicators Benefits:")
    print("  - 🎯 Reusable across all strategies")
    print("  - 📊 Comprehensive indicator library")
    print("  - 🔧 Easy to extend with new indicators")
    print("  - 💹 Professional-grade calculations")
    print("  - 📈 Support for price and volume analysis")
    print("  - 🎪 Crossover and signal detection")

    print("\n🎉 Technical indicators example completed!")


if __name__ == "__main__":
    main()
