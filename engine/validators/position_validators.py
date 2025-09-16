"""Position validation rules and validators."""

from decimal import Decimal

from ..enums import PositionStatus
from ..models import PositionData


class PositionDataValidator:
    """Validator for position data integrity."""

    @staticmethod
    def validate_position_data(position: PositionData) -> tuple[bool, str]:
        """Validate basic position data."""
        if not position.symbol:
            return False, "Symbol is required"

        if not position.position_id:
            return False, "Position ID is required"

        if position.entry_price <= 0:
            return False, "Entry price must be positive"

        if position.current_price <= 0:
            return False, "Current price must be positive"

        if position.leverage <= 0:
            return False, "Leverage must be positive"

        return True, ""

    @staticmethod
    def validate_position_size(position: PositionData) -> tuple[bool, str]:
        """Validate position size is reasonable."""
        if position.size == 0 and position.status == PositionStatus.OPEN:
            return False, "Open position cannot have zero size"

        return True, ""


class PositionBusinessRuleValidator:
    """Validator for position business rules."""

    @staticmethod
    def validate_leverage_limits(position: PositionData, max_leverage: int = 100) -> tuple[bool, str]:
        """Validate position leverage is within limits."""
        if position.leverage > max_leverage:
            return False, f"Leverage {position.leverage} exceeds maximum {max_leverage}"

        return True, ""

    @staticmethod
    def validate_position_value_limits(position: PositionData, max_position_value: Decimal) -> tuple[bool, str]:
        """Validate position value is within limits."""
        position_value = abs(position.size) * position.current_price

        if position_value > max_position_value:
            return False, f"Position value {position_value} exceeds maximum {max_position_value}"

        return True, ""

    @staticmethod
    def validate_margin_requirements(position: PositionData, available_margin: Decimal) -> tuple[bool, str]:
        """Validate position meets margin requirements."""
        required_margin = (abs(position.size) * position.current_price) / position.leverage

        if required_margin > available_margin:
            return False, f"Required margin {required_margin} exceeds available margin {available_margin}"

        return True, ""
