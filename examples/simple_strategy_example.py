"""Simple example demonstrating the new SOLID-compliant MidasEngine.

This example shows how to:
1. Create a simple trading strategy
2. Use the new BacktestEngine with dependency injection
3. Run a backtest with proper SOLID architecture
"""

from datetime import datetime
from decimal import Decimal

# Import from the new engine structure
from engine import (
    AccountData,
    BacktestEngine,
    Candle,
    EngineComponentFactory,
    FeeConfig,
    IndicatorUtils,
    MovingAverages,
    OrderData,
    OrderSide,
    OrderType,
    PositionData,
    Strategy,
)


class SimpleMovingAverageStrategy(Strategy):
    """A simple moving average crossover strategy example."""

    def __init__(self, short_period: int = 10, long_period: int = 20):
        """Initialize the strategy with MA periods."""
        super().__init__(
            name="Simple MA Crossover",
            parameters={
                "short_period": short_period,
                "long_period": long_period,
            },
        )
        self.short_period = short_period
        self.long_period = long_period
        self.candle_history = []
        self.position_open = False

    def on_candle(self, candle: Candle, account: AccountData) -> list[OrderData]:
        """Process new candle and generate trading signals."""
        # Add current candle to history
        self.candle_history.append(candle)

        # Keep only the data we need
        max_history = max(self.short_period, self.long_period) + 1
        if len(self.candle_history) > max_history:
            self.candle_history = self.candle_history[-max_history:]

        # Calculate moving averages using the new technical indicators
        short_ma = MovingAverages.sma_from_candles(self.candle_history, self.short_period, "close")
        long_ma = MovingAverages.sma_from_candles(self.candle_history, self.long_period, "close")

        orders = []

        # Need both MAs to generate signals
        if short_ma is None or long_ma is None:
            return orders

        # Calculate previous MAs for crossover detection
        if len(self.candle_history) >= max(self.short_period, self.long_period) + 1:
            prev_candles = self.candle_history[:-1]  # All but the last candle
            prev_short_ma = MovingAverages.sma_from_candles(prev_candles, self.short_period, "close")
            prev_long_ma = MovingAverages.sma_from_candles(prev_candles, self.long_period, "close")

            if prev_short_ma is not None and prev_long_ma is not None:
                # Create MA lists for crossover detection
                short_ma_list = [prev_short_ma, short_ma]
                long_ma_list = [prev_long_ma, long_ma]

                # Use IndicatorUtils for crossover detection
                bullish_crossover = IndicatorUtils.crossover(short_ma_list, long_ma_list)
                bearish_crossover = IndicatorUtils.crossunder(short_ma_list, long_ma_list)

                # Buy signal: bullish crossover
                if not self.position_open and bullish_crossover:
                    # Create a market buy order
                    order = OrderData(
                        symbol="BTCUSDT",
                        side=OrderSide.BUY,
                        quantity=Decimal("0.01"),  # Small position size
                        order_id="",  # Will be set by order manager
                        order_type=OrderType.MARKET,
                        created_at=datetime.now(),
                    )
                    orders.append(order)
                    self.position_open = True

                # Sell signal: bearish crossover
                elif self.position_open and bearish_crossover:
                    # Create a market sell order
                    order = OrderData(
                        symbol="BTCUSDT",
                        side=OrderSide.SELL,
                        quantity=Decimal("0.01"),
                        order_id="",
                        order_type=OrderType.MARKET,
                        created_at=datetime.now(),
                    )
                    orders.append(order)
                    self.position_open = False

        return orders

    def on_order_filled(self, order: OrderData, account: AccountData) -> None:
        """Handle order fills."""
        print(f"Order filled: {order.side.value} {order.quantity} at {order.order_id}")

    def on_position_opened(self, position: PositionData, account: AccountData) -> None:
        """Handle position opening."""
        print(f"Position opened: {position.side.value} {position.size} at {position.entry_price}")

    def on_position_closed(self, position: PositionData, account: AccountData) -> None:
        """Handle position closing."""
        print(f"Position closed: {position.side.value} PnL: {position.realized_pnl}")


def create_sample_candles() -> list[Candle]:
    """Create sample candle data for testing."""
    candles = []
    base_price = Decimal("50000")  # Starting BTC price

    # Generate 100 candles with some price movement
    TREND_CHANGE_POINT = 50
    TOTAL_CANDLES = 100

    for i in range(TOTAL_CANDLES):
        # Simple price simulation - trending up then down
        if i < TREND_CHANGE_POINT:
            price_change = Decimal(str(i * 10))  # Upward trend
        else:
            price_change = Decimal(str((TOTAL_CANDLES - i) * 10))  # Downward trend

        current_price = base_price + price_change

        candle = Candle(
            open_time=1640000000000 + (i * 60000),  # 1 minute intervals
            open=current_price - Decimal("5"),
            high=current_price + Decimal("10"),
            low=current_price - Decimal("10"),
            close=current_price,
            volume=Decimal("1.5"),
            close_time=1640000000000 + (i * 60000) + 59999,
            quote_asset_volume=current_price * Decimal("1.5"),
            number_of_trades=100,
            taker_buy_base=Decimal("0.8"),
            taker_buy_quote=current_price * Decimal("0.8"),
        )
        candles.append(candle)

    return candles


def main():
    """Main example function."""
    print("🚀 MidasEngine SOLID Architecture Example")
    print("=" * 50)

    # 1. Create custom fee configuration
    fee_config = FeeConfig(
        maker_fee_rate=Decimal("0.001"),  # 0.1%
        taker_fee_rate=Decimal("0.0015"),  # 0.15%
    )

    # 2. Create component factory with custom config
    factory = EngineComponentFactory(fee_config)

    # 3. Initialize the backtest engine with dependency injection
    engine = BacktestEngine(
        initial_balance=Decimal("10000"),  # $10,000 starting balance
        base_currency="USDT",
        fee_config=fee_config,
        component_factory=factory,
    )

    # 4. Create our strategy
    strategy = SimpleMovingAverageStrategy(short_period=5, long_period=15)

    # 5. Generate sample data
    candles = create_sample_candles()

    # 6. Run the backtest
    print(f"Running backtest with {len(candles)} candles...")
    results = engine.run_backtest(strategy, candles, "BTCUSDT")

    # 7. Display results
    print("\n📊 Backtest Results:")
    print("=" * 30)
    print(f"Strategy: {results.metrics.strategy_name}")
    print(f"Initial Balance: ${results.metrics.initial_balance}")
    print(f"Final Balance: ${results.metrics.final_balance}")
    print(f"Total Return: {results.metrics.total_return:.2f}%")
    print(f"Total Trades: {results.metrics.total_trades}")
    print(f"Winning Trades: {results.metrics.winning_trades}")
    print(f"Win Rate: {results.metrics.win_rate:.2f}%")
    print(f"Profit Factor: {results.metrics.profit_factor:.2f}")
    print(f"Max Drawdown: {results.metrics.max_drawdown:.2f}%")
    print(f"Total Fees: ${results.metrics.total_fees}")

    # 8. Show account summary
    print("\n🏦 Account Summary:")
    account_summary = engine.get_account_summary()
    for key, value in account_summary.items():
        print(f"{key}: {value}")

    print("\n✅ Example completed successfully!")
    print("The new SOLID architecture provides:")
    print("- Clean separation of concerns")
    print("- Easy dependency injection")
    print("- Testable components")
    print("- Extensible design")


if __name__ == "__main__":
    main()
