"""Trade validation rules and validators."""

from decimal import Decimal

from ..enums import TradeStatus
from ..models import TradeData


class TradeDataValidator:
    """Validator for trade data integrity."""

    @staticmethod
    def validate_trade_data(trade: TradeData) -> tuple[bool, str]:
        """Validate basic trade data."""
        # Check required string fields
        required_fields = [
            (trade.trade_id, "Trade ID is required"),
            (trade.symbol, "Symbol is required"),
            (trade.entry_order_id, "Entry order ID is required"),
            (trade.position_id, "Position ID is required"),
        ]

        for field_value, error_msg in required_fields:
            if not field_value:
                return False, error_msg

        # Check positive numeric fields
        positive_fields = [
            (trade.entry_price, "Entry price must be positive"),
            (trade.entry_quantity, "Entry quantity must be positive"),
            (trade.leverage, "Leverage must be positive"),
        ]

        for field_value, error_msg in positive_fields:
            if field_value <= 0:
                return False, error_msg

        return True, ""

    @staticmethod
    def validate_closed_trade_data(trade: TradeData) -> tuple[bool, str]:
        """Validate closed trade specific data."""
        is_valid, error = TradeDataValidator.validate_trade_data(trade)
        if not is_valid:
            return is_valid, error

        if trade.status == TradeStatus.CLOSED:
            if trade.exit_price is None:
                return False, "Closed trade must have exit price"

            if trade.exit_time is None:
                return False, "Closed trade must have exit time"

            if trade.exit_order_id is None:
                return False, "Closed trade must have exit order ID"

            if trade.exit_price <= 0:
                return False, "Exit price must be positive"

        return True, ""


class TradeBusinessRuleValidator:
    """Validator for trade business rules."""

    @staticmethod
    def validate_trade_duration(trade: TradeData, min_duration_minutes: float = 0.1) -> tuple[bool, str]:
        """Validate trade duration is reasonable."""
        if trade.status == TradeStatus.CLOSED and trade.exit_time and trade.entry_time:
            duration_minutes = (trade.exit_time - trade.entry_time).total_seconds() / 60.0

            if duration_minutes < min_duration_minutes:
                return False, f"Trade duration {duration_minutes:.2f} minutes is too short"

        return True, ""

    @staticmethod
    def validate_pnl_calculation(trade: TradeData) -> tuple[bool, str]:
        """Validate PnL calculation is consistent."""
        if trade.status == TradeStatus.CLOSED and trade.exit_price:
            # Calculate expected PnL
            if trade.position_side.value == "LONG":
                expected_pnl = (trade.exit_price - trade.entry_price) * trade.entry_quantity
            else:  # SHORT
                expected_pnl = (trade.entry_price - trade.exit_price) * trade.entry_quantity

            # Allow for small rounding differences
            tolerance = Decimal("0.01")
            pnl_difference = abs(trade.realized_pnl - expected_pnl)

            if pnl_difference > tolerance:
                return False, f"PnL calculation inconsistent: expected {expected_pnl}, got {trade.realized_pnl}"

        return True, ""

    @staticmethod
    def validate_fee_reasonableness(trade: TradeData, max_fee_percent: Decimal = Decimal("1.0")) -> tuple[bool, str]:
        """Validate fees are reasonable compared to trade value."""
        trade_value = trade.entry_price * trade.entry_quantity
        max_fee = trade_value * (max_fee_percent / 100)

        if trade.total_fees > max_fee:
            return False, f"Total fees {trade.total_fees} exceed maximum {max_fee} ({max_fee_percent}% of trade value)"

        return True, ""
