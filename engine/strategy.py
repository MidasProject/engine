"""Strategy base class extracted from backtest.py for better organization."""

from abc import abstractmethod

from .interfaces import IStrategy
from .models import AccountData, Candle, OrderData, PositionData


class Strategy(IStrategy):
    """Abstract base class for trading strategies.

    This class implements the IStrategy interface and provides
    a concrete base for strategy implementations.
    """

    def __init__(self, name: str, parameters: dict | None = None):
        """Initialize the strategy.

        Args:
            name: Name of the strategy
            parameters: Strategy parameters dictionary
        """
        self._name = name
        self._parameters = parameters or {}

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

    def get_strategy_name(self) -> str:
        """Get the name of the strategy."""
        return self._name

    def get_strategy_parameters(self) -> dict:
        """Get strategy parameters for reporting."""
        return self._parameters.copy()

    def set_parameter(self, key: str, value) -> None:
        """Set a strategy parameter."""
        self._parameters[key] = value

    def get_parameter(self, key: str, default=None):
        """Get a strategy parameter."""
        return self._parameters.get(key, default)
