"""Account management service implementations."""

from datetime import datetime
from decimal import Decimal

from ..interfaces import IAccountManager, IBalanceService
from ..models import AccountData, Balance, PositionData


class BalanceService(IBalanceService):
    """Service for balance management operations."""

    def add_balance(self, account: AccountData, asset: str, amount: Decimal) -> None:
        """Add balance to account."""
        if asset not in account.balances:
            account.balances[asset] = Balance(asset=asset, free=amount, locked=Decimal("0"))
        else:
            account.balances[asset].free += amount

    def get_balance(self, account: AccountData, asset: str) -> Decimal:
        """Get free balance for an asset."""
        if asset not in account.balances:
            return Decimal("0")
        return account.balances[asset].free

    def get_total_balance(self, account: AccountData, asset: str) -> Decimal:
        """Get total balance (free + locked) for an asset."""
        if asset not in account.balances:
            return Decimal("0")
        return account.balances[asset].total

    def has_sufficient_balance(self, account: AccountData, asset: str, amount: Decimal) -> bool:
        """Check if account has sufficient balance."""
        return self.get_balance(account, asset) >= amount

    def lock_balance(self, account: AccountData, asset: str, amount: Decimal) -> None:
        """Lock balance for an order."""
        if asset not in account.balances:
            raise ValueError(f"No balance for asset {asset}")

        balance = account.balances[asset]
        if balance.free < amount:
            raise ValueError("Insufficient free balance to lock")

        balance.free -= amount
        balance.locked += amount

    def unlock_balance(self, account: AccountData, asset: str, amount: Decimal) -> None:
        """Unlock balance after order completion."""
        if asset not in account.balances:
            raise ValueError(f"No balance for asset {asset}")

        balance = account.balances[asset]
        if balance.locked < amount:
            raise ValueError("Insufficient locked balance to unlock")

        balance.locked -= amount
        balance.free += amount


class AccountManager(IAccountManager):
    """Service for account management operations."""

    def __init__(self, balance_service: IBalanceService):
        """Initialize with balance service dependency."""
        self.balance_service = balance_service
        self._accounts: dict[str, AccountData] = {}
        self._positions: dict[str, dict[str, PositionData]] = {}  # account_id -> position_id -> position

    def create_account(self, account_id: str, initial_balance: Decimal, currency: str) -> AccountData:
        """Create a new trading account."""
        account = AccountData(account_id=account_id, created_at=datetime.now())
        self.balance_service.add_balance(account, currency, initial_balance)
        self._accounts[account_id] = account
        self._positions[account_id] = {}
        return account

    def get_account(self, account_id: str) -> AccountData | None:
        """Get account by ID."""
        return self._accounts.get(account_id)

    def add_position(self, account: AccountData, position: PositionData) -> None:
        """Add a position to the account."""
        if account.account_id not in self._positions:
            self._positions[account.account_id] = {}
        self._positions[account.account_id][position.position_id] = position

    def get_position(self, account: AccountData, position_id: str) -> PositionData | None:
        """Get position by ID."""
        account_positions = self._positions.get(account.account_id, {})
        return account_positions.get(position_id)

    def get_positions_by_symbol(self, account: AccountData, symbol: str) -> list[PositionData]:
        """Get all positions for a specific symbol."""
        account_positions = self._positions.get(account.account_id, {})
        return [pos for pos in account_positions.values() if pos.symbol == symbol]

    def get_total_equity(self, account: AccountData, base_currency: str = "USDT") -> Decimal:
        """Get total account equity including unrealized PnL."""
        total_balance = self.balance_service.get_total_balance(account, base_currency)

        # Add unrealized PnL from all open positions
        account_positions = self._positions.get(account.account_id, {})
        unrealized_pnl = sum(pos.unrealized_pnl for pos in account_positions.values() if pos.status.value == "OPEN")

        return total_balance + unrealized_pnl
