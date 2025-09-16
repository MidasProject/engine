"""Backtest result data models."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from .trades import TradeData


@dataclass
class BacktestMetrics:
    """Backtest performance metrics data structure.

    This is a pure data model containing backtest metrics without analysis logic.
    """

    strategy_name: str
    symbol: str
    start_time: datetime
    end_time: datetime
    initial_balance: Decimal
    final_balance: Decimal

    # Trade statistics
    total_trades: int = 0
    closed_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0

    # Performance metrics
    total_pnl: Decimal = Decimal("0")
    total_fees: Decimal = Decimal("0")
    net_pnl: Decimal = Decimal("0")
    total_return: Decimal = Decimal("0")
    win_rate: Decimal = Decimal("0")
    max_drawdown: Decimal = Decimal("0")
    profit_factor: Decimal = Decimal("0")
    average_win: Decimal = Decimal("0")
    average_loss: Decimal = Decimal("0")
    average_trade_duration: float | None = None


@dataclass
class BacktestResultData:
    """Container for backtest results data.

    This is a pure data model containing backtest results without analysis logic.
    """

    metrics: BacktestMetrics
    trades: list[TradeData] = field(default_factory=list)
