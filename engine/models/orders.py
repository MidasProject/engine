"""Order data models for trading operations."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from ..enums import OrderSide, OrderStatus, OrderType


@dataclass
class OrderData:
    """Base order data structure.

    This is a pure data model containing core order information without business logic.
    """

    symbol: str
    side: OrderSide
    quantity: Decimal
    order_id: str
    order_type: OrderType
    client_order_id: str | None = None
    status: OrderStatus = OrderStatus.NEW
    created_at: datetime | None = None
    filled_at: datetime | None = None
    error_message: str | None = None


@dataclass
class LimitOrderData(OrderData):
    """Limit order specific data."""

    price: Decimal = Decimal("0")
    order_type: OrderType = OrderType.LIMIT


@dataclass
class StopOrderData(OrderData):
    """Stop order specific data."""

    stop_price: Decimal = Decimal("0")


@dataclass
class StopLimitOrderData(StopOrderData):
    """Stop limit order specific data."""

    limit_price: Decimal = Decimal("0")
    order_type: OrderType = OrderType.STOP_LIMIT


@dataclass
class StopMarketOrderData(StopOrderData):
    """Stop market order specific data."""

    order_type: OrderType = OrderType.STOP_MARKET


@dataclass
class TakeProfitOrderData(OrderData):
    """Take profit order specific data."""

    target_price: Decimal = Decimal("0")
    order_type: OrderType = OrderType.TAKE_PROFIT
