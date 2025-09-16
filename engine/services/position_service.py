"""Position management service implementations."""

from datetime import datetime
from decimal import Decimal

from ..enums import PositionSide, PositionStatus
from ..interfaces import IPnLCalculator, IPositionManager
from ..models import PositionData, PositionParams


class PnLCalculator(IPnLCalculator):
    """Service for PnL calculations."""

    def calculate_unrealized_pnl(self, position: PositionData, current_price: Decimal) -> Decimal:
        """Calculate unrealized PnL for a position."""
        if position.side == PositionSide.LONG:
            return (current_price - position.entry_price) * position.size
        else:  # SHORT
            return (position.entry_price - current_price) * position.size

    def calculate_realized_pnl(self, position: PositionData, close_price: Decimal, close_quantity: Decimal) -> Decimal:
        """Calculate realized PnL for a position closure."""
        if position.side == PositionSide.LONG:
            return (close_price - position.entry_price) * abs(close_quantity)
        else:  # SHORT
            return (position.entry_price - close_price) * abs(close_quantity)

    def calculate_margin_used(self, position: PositionData) -> Decimal:
        """Calculate margin used by a position."""
        position_value = abs(position.size) * position.current_price
        return position_value / position.leverage


class PositionManager(IPositionManager):
    """Service for position management operations."""

    def __init__(self, pnl_calculator: IPnLCalculator):
        """Initialize with PnL calculator dependency."""
        self.pnl_calculator = pnl_calculator

    def create_position(self, params: PositionParams) -> PositionData:
        """Create a new position."""
        position_side = PositionSide.LONG if params.side == "LONG" else PositionSide.SHORT

        position = PositionData(
            symbol=params.symbol,
            side=position_side,
            size=params.size,
            entry_price=params.entry_price,
            current_price=params.entry_price,
            leverage=params.leverage,
            position_id=params.position_id,
            entry_time=datetime.now(),
            status=PositionStatus.OPEN,
        )

        # Calculate initial unrealized PnL (should be 0)
        position.unrealized_pnl = self.pnl_calculator.calculate_unrealized_pnl(position, params.entry_price)

        return position

    def update_position_price(self, position: PositionData, current_price: Decimal) -> None:
        """Update position with current market price."""
        position.current_price = current_price
        position.unrealized_pnl = self.pnl_calculator.calculate_unrealized_pnl(position, current_price)

    def add_to_position(self, position: PositionData, additional_size: Decimal, additional_price: Decimal) -> None:
        """Add to existing position."""
        if position.status != PositionStatus.OPEN:
            raise ValueError("Cannot add to closed position")

        # Validate direction
        if position.side == PositionSide.LONG and additional_size < 0:
            raise ValueError("Cannot add negative size to long position")
        if position.side == PositionSide.SHORT and additional_size > 0:
            raise ValueError("Cannot add positive size to short position")

        # Calculate new average entry price
        total_value = (position.entry_price * position.size) + (additional_price * abs(additional_size))
        position.size += additional_size
        position.entry_price = total_value / position.size

        # Update unrealized PnL
        position.unrealized_pnl = self.pnl_calculator.calculate_unrealized_pnl(position, position.current_price)

    def close_position_partial(self, position: PositionData, close_size: Decimal, close_price: Decimal) -> Decimal:
        """Close part of a position and return realized PnL."""
        if position.status != PositionStatus.OPEN:
            raise ValueError("Cannot close closed position")

        if abs(close_size) > abs(position.size):
            raise ValueError("Cannot close more than current position size")

        # Calculate realized PnL for the closed portion
        realized_pnl = self.pnl_calculator.calculate_realized_pnl(position, close_price, close_size)

        # Update position size
        position.size -= close_size
        position.realized_pnl += realized_pnl

        # If position is fully closed, mark as closed
        if position.size == 0:
            position.status = PositionStatus.CLOSED

        # Update unrealized PnL for remaining position
        position.unrealized_pnl = self.pnl_calculator.calculate_unrealized_pnl(position, position.current_price)

        return realized_pnl

    def close_position_full(self, position: PositionData, close_price: Decimal) -> Decimal:
        """Close entire position and return realized PnL."""
        if position.status != PositionStatus.OPEN:
            raise ValueError("Cannot close closed position")

        # Calculate realized PnL for the entire position
        realized_pnl = self.pnl_calculator.calculate_unrealized_pnl(position, close_price)

        # Update position
        position.realized_pnl = realized_pnl
        position.size = Decimal("0")
        position.status = PositionStatus.CLOSED
        position.unrealized_pnl = Decimal("0")

        return realized_pnl
