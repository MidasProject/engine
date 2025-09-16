"""Parameter objects for position creation to reduce argument count."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PositionParams:
    """Parameters for creating a position."""

    symbol: str
    side: str
    size: Decimal
    entry_price: Decimal
    leverage: int
    position_id: str


@dataclass
class TradeParams:
    """Parameters for creating a trade."""

    symbol: str
    entry_order_type: str
    entry_side: str
    entry_quantity: Decimal
    entry_price: Decimal
    entry_order_id: str
    position_side: str
    leverage: int
    position_id: str


@dataclass
class StopLimitOrderParams:
    """Parameters for creating a stop limit order."""

    symbol: str
    side: str
    quantity: Decimal
    stop_price: Decimal
    limit_price: Decimal
    client_order_id: str | None = None
