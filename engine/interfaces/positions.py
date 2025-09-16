"""Position management interfaces."""

from abc import ABC, abstractmethod
from decimal import Decimal

from ..models import PositionData, PositionParams


class IPnLCalculator(ABC):
    """Interface for PnL calculations."""

    @abstractmethod
    def calculate_unrealized_pnl(self, position: PositionData, current_price: Decimal) -> Decimal:
        """Calculate unrealized PnL for a position."""
        pass

    @abstractmethod
    def calculate_realized_pnl(self, position: PositionData, close_price: Decimal, close_quantity: Decimal) -> Decimal:
        """Calculate realized PnL for a position closure."""
        pass

    @abstractmethod
    def calculate_margin_used(self, position: PositionData) -> Decimal:
        """Calculate margin used by a position."""
        pass


class IPositionManager(ABC):
    """Interface for position management operations."""

    @abstractmethod
    def create_position(self, params: PositionParams) -> PositionData:
        """Create a new position."""
        pass

    @abstractmethod
    def update_position_price(self, position: PositionData, current_price: Decimal) -> None:
        """Update position with current market price."""
        pass

    @abstractmethod
    def add_to_position(self, position: PositionData, additional_size: Decimal, additional_price: Decimal) -> None:
        """Add to existing position."""
        pass

    @abstractmethod
    def close_position_partial(self, position: PositionData, close_size: Decimal, close_price: Decimal) -> Decimal:
        """Close part of a position and return realized PnL."""
        pass

    @abstractmethod
    def close_position_full(self, position: PositionData, close_price: Decimal) -> Decimal:
        """Close entire position and return realized PnL."""
        pass
