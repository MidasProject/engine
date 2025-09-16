"""Factory for creating different order types."""

from datetime import datetime
from decimal import Decimal

from ..enums import OrderSide, OrderType
from ..models import (
    LimitOrderData,
    OrderData,
    StopLimitOrderData,
    StopLimitOrderParams,
    StopMarketOrderData,
    TakeProfitOrderData,
)


class OrderFactory:
    """Factory for creating different types of orders."""

    def __init__(self):
        """Initialize the order factory."""
        self._order_counter = 0

    def _generate_order_id(self) -> str:
        """Generate unique order ID."""
        self._order_counter += 1
        return f"order_{self._order_counter}"

    def create_market_order(
        self, symbol: str, side: OrderSide, quantity: Decimal, client_order_id: str | None = None
    ) -> OrderData:
        """Create a market order."""
        return OrderData(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_id=self._generate_order_id(),
            order_type=OrderType.MARKET,
            client_order_id=client_order_id,
            created_at=datetime.now(),
        )

    def create_limit_order(
        self, symbol: str, side: OrderSide, quantity: Decimal, price: Decimal, client_order_id: str | None = None
    ) -> LimitOrderData:
        """Create a limit order."""
        return LimitOrderData(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_id=self._generate_order_id(),
            price=price,
            client_order_id=client_order_id,
            created_at=datetime.now(),
        )

    def create_stop_market_order(
        self, symbol: str, side: OrderSide, quantity: Decimal, stop_price: Decimal, client_order_id: str | None = None
    ) -> StopMarketOrderData:
        """Create a stop market order."""
        return StopMarketOrderData(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_id=self._generate_order_id(),
            stop_price=stop_price,
            order_type=OrderType.STOP_MARKET,
            client_order_id=client_order_id,
            created_at=datetime.now(),
        )

    def create_stop_limit_order(self, params: StopLimitOrderParams) -> StopLimitOrderData:
        """Create a stop limit order."""
        return StopLimitOrderData(
            symbol=params.symbol,
            side=OrderSide.BUY if params.side.upper() == "BUY" else OrderSide.SELL,
            quantity=params.quantity,
            order_id=self._generate_order_id(),
            stop_price=params.stop_price,
            limit_price=params.limit_price,
            client_order_id=params.client_order_id,
            created_at=datetime.now(),
        )

    def create_take_profit_order(
        self, symbol: str, side: OrderSide, quantity: Decimal, target_price: Decimal, client_order_id: str | None = None
    ) -> TakeProfitOrderData:
        """Create a take profit order."""
        return TakeProfitOrderData(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_id=self._generate_order_id(),
            target_price=target_price,
            client_order_id=client_order_id,
            created_at=datetime.now(),
        )
