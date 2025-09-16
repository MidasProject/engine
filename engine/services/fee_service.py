"""Fee calculation service implementations."""

from datetime import datetime
from decimal import Decimal

from ..enums import FeeType, OrderType
from ..interfaces import IFeeCalculator, IFeeService
from ..models import Fee, FeeConfig


class FeeCalculator(IFeeCalculator):
    """Service for fee calculations."""

    def __init__(self, config: FeeConfig):
        """Initialize with fee configuration."""
        self.config = config

    def calculate_order_fee(
        self, order_type: OrderType, quantity: Decimal, price: Decimal, currency: str = "USDT"
    ) -> Fee:
        """Calculate fee for an order execution."""
        if order_type == OrderType.MARKET:
            fee_rate = self.config.taker_fee_rate
            fee_type = FeeType.TAKER
        else:
            fee_rate = self.config.maker_fee_rate
            fee_type = FeeType.MAKER

        fee_amount = quantity * price * fee_rate

        return Fee(
            fee_type=fee_type,
            amount=fee_amount,
            currency=currency,
            timestamp=datetime.now(),
            order_id="",  # Will be set by caller
        )

    def calculate_funding_fee(self, position_value: Decimal, currency: str = "USDT") -> Fee:
        """Calculate funding fee for a position."""
        fee_amount = position_value * self.config.funding_fee_rate

        return Fee(
            fee_type=FeeType.FUNDING,
            amount=fee_amount,
            currency=currency,
            timestamp=datetime.now(),
            order_id="",  # Will be set by caller
        )

    def calculate_commission_fee(self, amount: Decimal, currency: str = "USDT") -> Fee:
        """Calculate commission fee."""
        fee_amount = amount * self.config.commission_rate

        return Fee(
            fee_type=FeeType.COMMISSION,
            amount=fee_amount,
            currency=currency,
            timestamp=datetime.now(),
            order_id="",  # Will be set by caller
        )


class FeeService(IFeeService):
    """Service for fee management operations."""

    def __init__(self, initial_config: FeeConfig | None = None):
        """Initialize with optional fee configuration."""
        self._config = initial_config or FeeConfig()
        self._account_fees: dict[str, list[Fee]] = {}

    def get_fee_config(self) -> FeeConfig:
        """Get current fee configuration."""
        return self._config

    def update_fee_config(self, config: FeeConfig) -> None:
        """Update fee configuration."""
        self._config = config

    def apply_fee_to_account(self, fee: Fee, account_id: str) -> None:
        """Apply a fee to an account."""
        if account_id not in self._account_fees:
            self._account_fees[account_id] = []

        self._account_fees[account_id].append(fee)

    def get_account_fees(self, account_id: str) -> list[Fee]:
        """Get all fees for an account."""
        return self._account_fees.get(account_id, [])

    def get_total_fees_paid(self, account_id: str) -> Decimal:
        """Get total fees paid by an account."""
        account_fees = self.get_account_fees(account_id)
        return sum(fee.amount for fee in account_fees)
