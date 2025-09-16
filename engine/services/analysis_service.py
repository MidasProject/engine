"""Analysis service implementations."""

from ..enums import TradeStatus
from ..interfaces import IBacktestAnalyzer, ITradeAnalyzer
from ..models import BacktestMetrics, BacktestResultData, TradeData


class TradeAnalyzer(ITradeAnalyzer):
    """Service for trade analysis operations."""

    def analyze_trade(self, trade: TradeData) -> dict:
        """Analyze a single trade and return metrics."""
        return {
            "trade_id": trade.trade_id,
            "symbol": trade.symbol,
            "side": trade.position_side.value,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "quantity": trade.entry_quantity,
            "leverage": trade.leverage,
            "realized_pnl": trade.realized_pnl,
            "pnl_percentage": self.calculate_pnl_percentage(trade),
            "total_fees": trade.total_fees,
            "duration_minutes": self.calculate_trade_duration(trade),
            "is_profitable": self.is_winning_trade(trade),
            "status": trade.status.value,
            "entry_time": trade.entry_time,
            "exit_time": trade.exit_time,
            "max_price": trade.max_price,
            "min_price": trade.min_price,
            "max_unrealized_pnl": trade.max_unrealized_pnl,
            "min_unrealized_pnl": trade.min_unrealized_pnl,
        }

    def calculate_trade_duration(self, trade: TradeData) -> float | None:
        """Calculate trade duration in minutes."""
        if trade.exit_time is None:
            return None
        duration_seconds = (trade.exit_time - trade.entry_time).total_seconds()
        return duration_seconds / 60.0

    def calculate_pnl_percentage(self, trade: TradeData) -> float:
        """Calculate PnL as percentage of entry value."""
        entry_value = trade.entry_price * trade.entry_quantity
        if entry_value == 0:
            return 0.0
        return float((trade.realized_pnl / entry_value) * 100)

    def is_winning_trade(self, trade: TradeData) -> bool:
        """Check if trade is profitable."""
        return trade.realized_pnl > 0


class BacktestAnalyzer(IBacktestAnalyzer):
    """Service for backtest analysis operations."""

    def __init__(self, trade_analyzer: ITradeAnalyzer):
        """Initialize with trade analyzer dependency."""
        self.trade_analyzer = trade_analyzer

    def analyze_backtest(self, result_data: BacktestResultData) -> BacktestMetrics:
        """Analyze backtest results and calculate metrics."""
        trades = result_data.trades
        metrics = result_data.metrics

        # Calculate trade statistics
        closed_trades = [t for t in trades if t.status == TradeStatus.CLOSED]
        winning_trades = [t for t in closed_trades if self.trade_analyzer.is_winning_trade(t)]
        losing_trades = [t for t in closed_trades if not self.trade_analyzer.is_winning_trade(t)]

        # Update metrics
        metrics.total_trades = len(trades)
        metrics.closed_trades = len(closed_trades)
        metrics.winning_trades = len(winning_trades)
        metrics.losing_trades = len(losing_trades)

        # Calculate performance metrics
        metrics.total_pnl = sum(t.realized_pnl for t in closed_trades)
        metrics.total_fees = sum(t.total_fees for t in trades)
        metrics.net_pnl = metrics.total_pnl - metrics.total_fees

        if metrics.initial_balance > 0:
            metrics.total_return = ((metrics.final_balance - metrics.initial_balance) / metrics.initial_balance) * 100

        metrics.win_rate = self.calculate_win_rate(closed_trades)
        metrics.profit_factor = self.calculate_profit_factor(closed_trades)
        metrics.max_drawdown = self.calculate_max_drawdown(closed_trades, float(metrics.initial_balance))

        # Calculate average win/loss
        if winning_trades:
            metrics.average_win = sum(t.realized_pnl for t in winning_trades) / len(winning_trades)
        if losing_trades:
            metrics.average_loss = sum(t.realized_pnl for t in losing_trades) / len(losing_trades)

        # Calculate average trade duration
        durations = [self.trade_analyzer.calculate_trade_duration(t) for t in closed_trades]
        valid_durations = [d for d in durations if d is not None]
        if valid_durations:
            metrics.average_trade_duration = sum(valid_durations) / len(valid_durations)

        return metrics

    def calculate_win_rate(self, trades: list[TradeData]) -> float:
        """Calculate win rate from trades."""
        if not trades:
            return 0.0

        winning_trades = sum(1 for t in trades if self.trade_analyzer.is_winning_trade(t))
        return (winning_trades / len(trades)) * 100

    def calculate_profit_factor(self, trades: list[TradeData]) -> float:
        """Calculate profit factor from trades."""
        gross_profit = sum(t.realized_pnl for t in trades if t.realized_pnl > 0)
        gross_loss = abs(sum(t.realized_pnl for t in trades if t.realized_pnl < 0))

        if gross_loss == 0:
            return 999999.0 if gross_profit > 0 else 0.0

        return float(gross_profit / gross_loss)

    def calculate_max_drawdown(self, trades: list[TradeData], initial_balance: float) -> float:
        """Calculate maximum drawdown from trades."""
        if not trades:
            return 0.0

        max_balance = initial_balance
        max_dd = 0.0
        current_balance = initial_balance

        for trade in trades:
            if trade.status == TradeStatus.CLOSED:
                current_balance += float(trade.realized_pnl)
                max_balance = max(max_balance, current_balance)
                if max_balance > 0:
                    drawdown = (max_balance - current_balance) / max_balance * 100
                    max_dd = max(max_dd, drawdown)

        return max_dd

    def generate_performance_report(self, metrics: BacktestMetrics) -> dict:
        """Generate comprehensive performance report."""
        return {
            "strategy_name": metrics.strategy_name,
            "symbol": metrics.symbol,
            "period": f"{metrics.start_time} to {metrics.end_time}",
            "initial_balance": metrics.initial_balance,
            "final_balance": metrics.final_balance,
            "total_return": metrics.total_return,
            "net_pnl": metrics.net_pnl,
            "total_trades": metrics.total_trades,
            "closed_trades": metrics.closed_trades,
            "winning_trades": metrics.winning_trades,
            "losing_trades": metrics.losing_trades,
            "win_rate": metrics.win_rate,
            "profit_factor": metrics.profit_factor,
            "max_drawdown": metrics.max_drawdown,
            "average_trade_duration_minutes": metrics.average_trade_duration,
            "average_win": metrics.average_win,
            "average_loss": metrics.average_loss,
            "total_fees": metrics.total_fees,
        }
