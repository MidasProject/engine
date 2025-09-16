"""Modern backtesting engine built with SOLID principles and dependency injection."""

from datetime import datetime
from decimal import Decimal

from .enums import OrderStatus, PositionStatus, TradeStatus
from .factories import EngineComponentFactory
from .interfaces import (
    IAccountManager,
    IBacktestAnalyzer,
    IFeeCalculator,
    IOrderManager,
    IPositionManager,
    IStrategy,
    ITradeAnalyzer,
)
from .models import (
    AccountData,
    BacktestMetrics,
    BacktestResultData,
    Candle,
    FeeConfig,
    OrderData,
    PositionData,
    TradeData,
)
from .strategy import Strategy
from .utils import IDGenerator


class BacktestEngine:
    """Modern backtesting engine with dependency injection and SOLID principles.

    This engine uses composition and dependency injection to create a flexible,
    testable, and maintainable backtesting system.
    """

    def __init__(
        self,
        initial_balance: Decimal,
        base_currency: str = "USDT",
        fee_config: FeeConfig | None = None,
        component_factory: EngineComponentFactory | None = None,
    ):
        """Initialize the backtesting engine with dependencies.

        Args:
            initial_balance: Starting account balance
            base_currency: Base currency for trading
            fee_config: Fee configuration
            component_factory: Factory for creating engine components
        """
        self.initial_balance = initial_balance
        self.base_currency = base_currency

        # Initialize factory and create all components with proper DI
        self._factory = component_factory or EngineComponentFactory(fee_config)
        self._components = self._factory.create_full_engine_components()

        # Extract services for easy access
        self._account_manager: IAccountManager = self._components["account_manager"]
        self._order_manager: IOrderManager = self._components["order_manager"]
        self._position_manager: IPositionManager = self._components["position_manager"]
        self._fee_calculator: IFeeCalculator = self._components["fee_calculator"]
        self._trade_analyzer: ITradeAnalyzer = self._components["trade_analyzer"]
        self._backtest_analyzer: IBacktestAnalyzer = self._components["backtest_analyzer"]

        # Initialize ID generator and account
        self._id_generator = IDGenerator()
        self._account = self._create_initial_account()

        # State tracking
        self._current_trades: dict[str, TradeData] = {}  # position_id -> trade
        self._completed_trades: list[TradeData] = []

    def _create_initial_account(self) -> AccountData:
        """Create the initial trading account."""
        account_id = self._id_generator.generate_account_id()
        return self._account_manager.create_account(account_id, self.initial_balance, self.base_currency)

    def _create_position_from_order(self, order: OrderData, fill_price: Decimal) -> PositionData:
        """Create a position from a filled order."""
        position_id = self._id_generator.generate_position_id()

        # Determine position side and size
        if order.side.value == "BUY":
            position_side = "LONG"
            position_size = order.quantity
        else:  # SELL
            position_side = "SHORT"
            position_size = -order.quantity

        return self._position_manager.create_position(
            symbol=order.symbol,
            side=position_side,
            size=position_size,
            entry_price=fill_price,
            leverage=1,  # Default leverage for spot trading
            position_id=position_id,
        )

    def _create_trade_from_order_and_position(self, order: OrderData, position: PositionData) -> TradeData:
        """Create a trade record from order and position."""
        trade_factory = self._components["trade_factory"]

        return trade_factory.create_trade(
            symbol=order.symbol,
            entry_order_type=order.order_type,
            entry_side=order.side,
            entry_quantity=order.quantity,
            entry_price=position.entry_price,
            entry_order_id=order.order_id,
            position_side=position.side,
            leverage=position.leverage,
            position_id=position.position_id,
        )

    def _process_order_execution(self, order: OrderData, current_price: Decimal) -> None:
        """Process the execution of an order."""
        # Create position
        position = self._create_position_from_order(order, current_price)

        # Add position to account
        self._account_manager.add_position(self._account, position)

        # Create trade record
        trade = self._create_trade_from_order_and_position(order, position)
        self._current_trades[position.position_id] = trade

        # Calculate and apply fees
        fee = self._fee_calculator.calculate_order_fee(
            order.order_type, order.quantity, current_price, self.base_currency
        )
        fee.order_id = order.order_id

        # Update account with fee (this would be handled by fee service in production)
        self._account.total_fees_paid += fee.amount

    def _update_positions_and_trades(self, current_price: Decimal) -> None:
        """Update all open positions and trades with current price."""
        for position_id, trade in self._current_trades.items():
            position = self._account_manager.get_position(self._account, position_id)
            if position and position.status == PositionStatus.OPEN:
                # Update position price
                self._position_manager.update_position_price(position, current_price)

                # Update trade tracking
                trade.max_price = max(trade.max_price, current_price)
                trade.min_price = min(trade.min_price, current_price)

                # Update unrealized PnL tracking
                unrealized_pnl = position.unrealized_pnl
                trade.max_unrealized_pnl = max(trade.max_unrealized_pnl, unrealized_pnl)
                trade.min_unrealized_pnl = min(trade.min_unrealized_pnl, unrealized_pnl)

    def _close_position(self, position_id: str, close_price: Decimal, close_order_id: str) -> None:
        """Close a position and complete the trade."""
        position = self._account_manager.get_position(self._account, position_id)
        if not position or position.status != PositionStatus.OPEN:
            return

        # Close the position
        realized_pnl = self._position_manager.close_position_full(position, close_price)

        # Update account PnL
        self._account.total_pnl += realized_pnl

        # Complete the trade if it exists
        if position_id in self._current_trades:
            trade = self._current_trades[position_id]

            # Close the trade
            trade.exit_price = close_price
            trade.exit_time = datetime.now()
            trade.exit_order_id = close_order_id
            trade.status = TradeStatus.CLOSED
            trade.realized_pnl = realized_pnl

            # Calculate exit fees
            exit_fee = self._fee_calculator.calculate_order_fee(
                trade.entry_order_type,  # Assuming same type for exit
                trade.entry_quantity,
                close_price,
                self.base_currency,
            )
            trade.total_fees += exit_fee.amount

            # Adjust PnL for fees
            trade.realized_pnl -= trade.total_fees

            # Move to completed trades
            self._completed_trades.append(trade)
            del self._current_trades[position_id]

    def run_backtest(self, strategy: IStrategy, candles: list[Candle], symbol: str) -> BacktestResultData:
        """Run backtest with given strategy and data.

        Args:
            strategy: Trading strategy to test
            candles: Historical candle data
            symbol: Trading symbol

        Returns:
            BacktestResultData with comprehensive results
        """
        if not candles:
            raise ValueError("No candle data provided")

        start_time = datetime.fromtimestamp(candles[0].open_time / 1000)
        end_time = datetime.fromtimestamp(candles[-1].close_time / 1000)

        print(f"Starting backtest: {strategy.get_strategy_name()}")
        print(f"Symbol: {symbol}")
        print(f"Period: {start_time} to {end_time}")
        print(f"Candles: {len(candles)}")
        print(f"Initial Balance: {self.initial_balance} {self.base_currency}")

        # Process each candle
        for i, candle in enumerate(candles):
            current_price = candle.close

            # Update positions and trades with current price
            self._update_positions_and_trades(current_price)

            # Process pending orders
            executed_orders = self._order_manager.process_orders(current_price, self._account)

            # Handle executed orders
            for order in executed_orders:
                if order.status == OrderStatus.FILLED:
                    self._process_order_execution(order, current_price)

            # Let strategy process the candle and generate new orders
            try:
                new_orders = strategy.on_candle(candle, self._account)

                # Place new orders
                for order in new_orders:
                    self._order_manager.place_order(order)

            except Exception as e:
                print(f"Strategy error at candle {i}: {e}")
                continue

            # Progress reporting
            if i % 1000 == 0:
                progress = (i / len(candles)) * 100
                print(f"Progress: {progress:.1f}% - Price: {current_price}")

        # Close any remaining open positions at final price
        final_price = candles[-1].close
        remaining_positions = list(self._current_trades.keys())

        for position_id in remaining_positions:
            self._close_position(position_id, final_price, "final_close")

        # Calculate final balance
        final_balance = self._account_manager.get_total_equity(self._account, self.base_currency)

        # Create backtest metrics
        metrics = BacktestMetrics(
            strategy_name=strategy.get_strategy_name(),
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            initial_balance=self.initial_balance,
            final_balance=final_balance,
        )

        # Create result data
        result_data = BacktestResultData(metrics=metrics, trades=self._completed_trades.copy())

        # Analyze results
        analyzed_metrics = self._backtest_analyzer.analyze_backtest(result_data)
        result_data.metrics = analyzed_metrics

        print("\nBacktest completed!")
        print(f"Final Balance: {final_balance} {self.base_currency}")
        print(f"Total Return: {analyzed_metrics.total_return:.2f}%")
        print(f"Total Trades: {analyzed_metrics.total_trades}")
        print(f"Win Rate: {analyzed_metrics.win_rate:.2f}%")

        return result_data

    def get_account_summary(self) -> dict:
        """Get current account summary."""
        return {
            "account_id": self._account.account_id,
            "total_equity": self._account_manager.get_total_equity(self._account, self.base_currency),
            "total_pnl": self._account.total_pnl,
            "total_fees_paid": self._account.total_fees_paid,
            "open_positions": len(self._current_trades),
            "completed_trades": len(self._completed_trades),
        }

    def reset_engine(self) -> None:
        """Reset the engine for a new backtest."""
        self._account = self._create_initial_account()
        self._current_trades.clear()
        self._completed_trades.clear()
        self._id_generator.reset_all_counters()


# Backward compatibility - keep the old Strategy class import available
# Users can import from either location during transition
__all__ = ["BacktestEngine", "Strategy"]
