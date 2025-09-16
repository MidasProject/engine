"""Account and balance data models."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class Balance:
    """Represents balance for a specific asset.

    This is a pure data model containing balance information.
    """

    asset: str
    free: Decimal
    locked: Decimal

    @property
    def total(self) -> Decimal:
        """Get total balance (free + locked)."""
        return self.free + self.locked


@dataclass
class AccountData:
    """Core account data structure.

    This is a pure data model containing account information without business logic.
    """

    account_id: str
    balances: dict[str, Balance] = field(default_factory=dict)
    total_fees_paid: Decimal = Decimal("0")
    total_pnl: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.now)
