"""Factory for creating trade objects."""

from datetime import datetime

from ..enums import TradeStatus
from ..models import TradeData, TradeFromOrderPositionParams, TradeParams


class TradeFactory:
    """Factory for creating trade objects."""

    def __init__(self):
        """Initialize the trade factory."""
        self._trade_counter = 0

    def _generate_trade_id(self) -> str:
        """Generate unique trade ID."""
        self._trade_counter += 1
        return f"trade_{self._trade_counter}"

    def create_trade_from_order_and_position(self, params: TradeFromOrderPositionParams) -> TradeData:
        """Create a trade from an order and position."""
        return TradeData(
            trade_id=self._generate_trade_id(),
            symbol=params.symbol,
            entry_order_type=params.order.order_type,
            entry_side=params.order.side,
            entry_quantity=params.order.quantity,
            entry_price=params.position.entry_price,
            entry_time=params.order.created_at or datetime.now(),
            entry_order_id=params.order.order_id,
            position_side=params.position.side,
            leverage=params.position.leverage,
            position_id=params.position.position_id,
            status=TradeStatus.OPEN,
            max_price=params.position.entry_price,
            min_price=params.position.entry_price,
        )

    def create_trade(self, params: TradeParams) -> TradeData:
        """Create a trade with detailed parameters."""
        return TradeData(
            trade_id=self._generate_trade_id(),
            symbol=params.symbol,
            entry_order_type=params.entry_order_type,
            entry_side=params.entry_side,
            entry_quantity=params.entry_quantity,
            entry_price=params.entry_price,
            entry_time=datetime.now(),
            entry_order_id=params.entry_order_id,
            position_side=params.position_side,
            leverage=params.leverage,
            position_id=params.position_id,
            status=TradeStatus.OPEN,
            max_price=params.entry_price,
            min_price=params.entry_price,
        )
