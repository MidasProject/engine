"""Account management interfaces."""

from abc import ABC, abstractmethod
from decimal import Decimal

from ..models import AccountData, PositionData


class IBalanceService(ABC):
    """Interface for balance management operations."""

    @abstractmethod
    def add_balance(self, account: AccountData, asset: str, amount: Decimal) -> None:
        """Add balance to account."""
        pass

    @abstractmethod
    def get_balance(self, account: AccountData, asset: str) -> Decimal:
        """Get free balance for an asset."""
        pass

    @abstractmethod
    def get_total_balance(self, account: AccountData, asset: str) -> Decimal:
        """Get total balance (free + locked) for an asset."""
        pass

    @abstractmethod
    def has_sufficient_balance(self, account: AccountData, asset: str, amount: Decimal) -> bool:
        """Check if account has sufficient balance."""
        pass

    @abstractmethod
    def lock_balance(self, account: AccountData, asset: str, amount: Decimal) -> None:
        """Lock balance for an order."""
        pass

    @abstractmethod
    def unlock_balance(self, account: AccountData, asset: str, amount: Decimal) -> None:
        """Unlock balance after order completion."""
        pass


class IAccountManager(ABC):
    """Interface for account management operations."""

    @abstractmethod
    def create_account(self, account_id: str, initial_balance: Decimal, currency: str) -> AccountData:
        """Create a new trading account."""
        pass

    @abstractmethod
    def get_account(self, account_id: str) -> AccountData | None:
        """Get account by ID."""
        pass

    @abstractmethod
    def add_position(self, account: AccountData, position: PositionData) -> None:
        """Add a position to the account."""
        pass

    @abstractmethod
    def get_position(self, account: AccountData, position_id: str) -> PositionData | None:
        """Get position by ID."""
        pass

    @abstractmethod
    def get_positions_by_symbol(self, account: AccountData, symbol: str) -> list[PositionData]:
        """Get all positions for a specific symbol."""
        pass

    @abstractmethod
    def get_total_equity(self, account: AccountData, base_currency: str = "USDT") -> Decimal:
        """Get total account equity including unrealized PnL."""
        pass
