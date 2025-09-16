"""Analysis and reporting interfaces."""

from abc import ABC, abstractmethod

from ..models import BacktestMetrics, BacktestResultData, TradeData


class ITradeAnalyzer(ABC):
    """Interface for trade analysis operations."""

    @abstractmethod
    def analyze_trade(self, trade: TradeData) -> dict:
        """Analyze a single trade and return metrics."""
        pass

    @abstractmethod
    def calculate_trade_duration(self, trade: TradeData) -> float | None:
        """Calculate trade duration in minutes."""
        pass

    @abstractmethod
    def calculate_pnl_percentage(self, trade: TradeData) -> float:
        """Calculate PnL as percentage of entry value."""
        pass

    @abstractmethod
    def is_winning_trade(self, trade: TradeData) -> bool:
        """Check if trade is profitable."""
        pass


class IBacktestAnalyzer(ABC):
    """Interface for backtest analysis operations."""

    @abstractmethod
    def analyze_backtest(self, result_data: BacktestResultData) -> BacktestMetrics:
        """Analyze backtest results and calculate metrics."""
        pass

    @abstractmethod
    def calculate_win_rate(self, trades: list[TradeData]) -> float:
        """Calculate win rate from trades."""
        pass

    @abstractmethod
    def calculate_profit_factor(self, trades: list[TradeData]) -> float:
        """Calculate profit factor from trades."""
        pass

    @abstractmethod
    def calculate_max_drawdown(self, trades: list[TradeData], initial_balance: float) -> float:
        """Calculate maximum drawdown from trades."""
        pass

    @abstractmethod
    def generate_performance_report(self, metrics: BacktestMetrics) -> dict:
        """Generate comprehensive performance report."""
        pass
