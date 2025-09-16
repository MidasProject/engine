"""Strategy interface for trading strategies."""

from abc import ABC, abstractmethod

from ..models import AccountData, Candle, OrderData, PositionData


class IStrategy(ABC):
    """Enhanced interface for trading strategies."""

    @abstractmethod
    def on_candle(self, candle: Candle, account: AccountData) -> list[OrderData]:
        """Process a new candle and return orders to place.

        Args:
            candle: Current candle data
            account: Current account state

        Returns:
            List of orders to place
        """
        pass

    @abstractmethod
    def on_order_filled(self, order: OrderData, account: AccountData) -> None:
        """Handle when an order is filled.

        Args:
            order: The filled order
            account: Current account state
        """
        pass

    @abstractmethod
    def on_position_opened(self, position: PositionData, account: AccountData) -> None:
        """Handle when a position is opened.

        Args:
            position: The opened position
            account: Current account state
        """
        pass

    @abstractmethod
    def on_position_closed(self, position: PositionData, account: AccountData) -> None:
        """Handle when a position is closed.

        Args:
            position: The closed position
            account: Current account state
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of the strategy."""
        pass

    @abstractmethod
    def get_strategy_parameters(self) -> dict:
        """Get strategy parameters for reporting."""
        pass
