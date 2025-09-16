"""Trading enumerations for the engine.

This module contains all enum definitions used throughout the trading engine.
All trading-related enums are consolidated here for better organization.
"""

from enum import Enum


class OrderSide(Enum):
    """Order side enumeration."""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """Order type enumeration."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"
    STOP_LIMIT = "STOP_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"


class OrderStatus(Enum):
    """Order status enumeration."""

    NEW = "NEW"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class PositionSide(Enum):
    """Position side enumeration for futures trading."""

    LONG = "LONG"
    SHORT = "SHORT"


class PositionStatus(Enum):
    """Position status enumeration."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    LIQUIDATED = "LIQUIDATED"


class FeeType(Enum):
    """Fee type enumeration."""

    MAKER = "MAKER"
    TAKER = "TAKER"
    FUNDING = "FUNDING"
    COMMISSION = "COMMISSION"


class TradeStatus(Enum):
    """Trade status enumeration."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
