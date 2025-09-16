"""Position data models for futures trading."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from ..enums import PositionSide, PositionStatus


@dataclass
class PositionData:
    """Core position data structure.

    This is a pure data model containing position information without business logic.
    """

    symbol: str
    side: PositionSide
    size: Decimal
    entry_price: Decimal
    current_price: Decimal
    leverage: int
    position_id: str
    entry_time: datetime
    status: PositionStatus = PositionStatus.OPEN
    unrealized_pnl: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")
