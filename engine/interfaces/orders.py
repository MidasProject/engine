"""Order management interfaces."""

from abc import ABC, abstractmethod
from decimal import Decimal

from ..enums import OrderType
from ..models import AccountData, OrderData


class IOrderValidator(ABC):
    """Interface for order validation."""

    @abstractmethod
    def validate_order(self, order: OrderData, account: AccountData) -> tuple[bool, str]:
        """Validate an order.

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    @abstractmethod
    def validate_balance(self, order: OrderData, account: AccountData) -> bool:
        """Validate if account has sufficient balance for order."""
        pass

    @abstractmethod
    def validate_order_data(self, order: OrderData) -> tuple[bool, str]:
        """Validate order data integrity."""
        pass


class IOrderExecutor(ABC):
    """Interface for order execution."""

    @abstractmethod
    def can_execute(self, order: OrderData, current_price: Decimal) -> bool:
        """Check if order can be executed at current price."""
        pass

    @abstractmethod
    def execute_order(self, order: OrderData, current_price: Decimal, account: AccountData) -> bool:
        """Execute an order.

        Returns:
            True if order was executed successfully
        """
        pass


class IOrderManager(ABC):
    """Interface for order management operations."""

    @abstractmethod
    def create_order(self, symbol: str, side: str, quantity: Decimal, order_type: OrderType, **kwargs) -> OrderData:
        """Create a new order."""
        pass

    @abstractmethod
    def place_order(self, order: OrderData) -> None:
        """Place an order."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        pass

    @abstractmethod
    def get_pending_orders(self) -> list[OrderData]:
        """Get all pending orders."""
        pass

    @abstractmethod
    def process_orders(self, current_price: Decimal, account: AccountData) -> list[OrderData]:
        """Process all pending orders and return executed orders."""
        pass
