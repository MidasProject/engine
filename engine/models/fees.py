"""Fee data models for trading operations."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from ..enums import FeeType


@dataclass
class Fee:
    """Represents a trading fee data structure.

    This is a pure data model containing fee information without business logic.
    """

    fee_type: FeeType
    amount: Decimal
    currency: str
    timestamp: datetime
    order_id: str
    position_id: str | None = None


@dataclass
class FeeConfig:
    """Configuration for fee calculation.

    This is a pure data model containing fee rates and settings.
    """

    maker_fee_rate: Decimal = Decimal("0.0002")  # 0.02%
    taker_fee_rate: Decimal = Decimal("0.0004")  # 0.04%
    funding_fee_rate: Decimal = Decimal("0.0001")  # 0.01% per 8 hours
    commission_rate: Decimal = Decimal("0.001")  # 0.1%
