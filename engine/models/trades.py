"""Trade data models for backtesting results."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from ..enums import OrderSide, OrderType, PositionSide, TradeStatus


@dataclass
class TradeData:
    """Core trade data structure.

    This is a pure data model containing trade information without business logic.
    """

    # Trade identification
    trade_id: str
    symbol: str

    # Order information
    entry_order_type: OrderType
    entry_side: OrderSide
    entry_quantity: Decimal
    entry_price: Decimal
    entry_time: datetime
    entry_order_id: str

    # Position information
    position_side: PositionSide
    leverage: int
    position_id: str

    # Exit information
    exit_order_type: OrderType | None = None
    exit_price: Decimal | None = None
    exit_time: datetime | None = None
    exit_order_id: str | None = None

    # Trade status
    status: TradeStatus = TradeStatus.OPEN

    # PnL and fees
    realized_pnl: Decimal = Decimal("0")
    total_fees: Decimal = Decimal("0")

    # Price tracking
    max_price: Decimal = Decimal("0")
    min_price: Decimal = Decimal("0")
    max_unrealized_pnl: Decimal = Decimal("0")
    min_unrealized_pnl: Decimal = Decimal("0")
