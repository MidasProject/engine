"""Data classes for trading operations and order management."""

# Standard library imports
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderSide(Enum):
    """Order side enumeration."""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """Order type enumeration."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"


class OrderStatus(Enum):
    """Order status enumeration."""

    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class TradeStatus(Enum):
    """Trade status enumeration."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


@dataclass
class BaseTrade:
    """Base trade data structure representing a completed trade.

    Attributes:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        entry_price: Price at which the position was opened
        exit_price: Price at which the position was closed
        entry_time: Timestamp when trade was opened
        exit_time: Timestamp when trade was closed
        quantity: Trade quantity in base asset
        side: Trade side (BUY/SELL)
        status: Current trade status
        error: Error message if any
        error_code: Error code if any
        error_message: Detailed error message if any
    """

    symbol: str
    entry_price: float
    exit_price: float | None
    entry_time: datetime
    exit_time: datetime | None
    quantity: float
    side: OrderSide
    status: TradeStatus
    error: str | None = None
    error_code: str | None = None
    error_message: str | None = None

    @property
    def pnl(self) -> float | None:
        """Calculate profit/loss for the trade.

        Returns:
            PnL amount or None if trade is not closed
        """
        if self.exit_price is None or self.status != TradeStatus.CLOSED:
            return None

        if self.side == OrderSide.BUY:
            return (self.exit_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.exit_price) * self.quantity

    @property
    def pnl_percentage(self) -> float | None:
        """Calculate profit/loss percentage.

        Returns:
            PnL percentage or None if trade is not closed
        """
        pnl = self.pnl
        if pnl is None:
            return None
        return (pnl / (self.entry_price * self.quantity)) * 100


@dataclass
class BaseOrder:
    """Base order data structure for trading operations.

    Attributes:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        price: Order price (None for market orders)
        quantity: Order quantity in base asset
        side: Order side (BUY/SELL)
        type: Order type (MARKET, LIMIT, etc.)
        status: Current order status
        error: Error message if any
        error_code: Error code if any
        error_message: Detailed error message if any
    """

    symbol: str
    price: float | None
    quantity: float
    side: OrderSide
    type: OrderType
    status: OrderStatus
    error: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    order_id: str | None = None
    client_order_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate order data after initialization."""
        if self.quantity <= 0:
            raise ValueError("Order quantity must be positive")

        if self.type == OrderType.LIMIT and self.price is None:
            raise ValueError("Limit orders must have a price")

        if self.type == OrderType.MARKET and self.price is not None:
            raise ValueError("Market orders should not have a price")
