"""Fee calculation interfaces."""

from abc import ABC, abstractmethod
from decimal import Decimal

from ..enums import OrderType
from ..models import Fee, FeeConfig


class IFeeCalculator(ABC):
    """Interface for fee calculations."""

    @abstractmethod
    def calculate_order_fee(
        self, order_type: OrderType, quantity: Decimal, price: Decimal, currency: str = "USDT"
    ) -> Fee:
        """Calculate fee for an order execution."""
        pass

    @abstractmethod
    def calculate_funding_fee(self, position_value: Decimal, currency: str = "USDT") -> Fee:
        """Calculate funding fee for a position."""
        pass

    @abstractmethod
    def calculate_commission_fee(self, amount: Decimal, currency: str = "USDT") -> Fee:
        """Calculate commission fee."""
        pass


class IFeeService(ABC):
    """Interface for fee management operations."""

    @abstractmethod
    def get_fee_config(self) -> FeeConfig:
        """Get current fee configuration."""
        pass

    @abstractmethod
    def update_fee_config(self, config: FeeConfig) -> None:
        """Update fee configuration."""
        pass

    @abstractmethod
    def apply_fee_to_account(self, fee: Fee, account_id: str) -> None:
        """Apply a fee to an account."""
        pass
