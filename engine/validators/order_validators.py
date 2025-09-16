"""Order validation rules and validators."""

from decimal import Decimal

from ..enums import OrderSide
from ..models import LimitOrderData, OrderData, StopLimitOrderData, StopOrderData, TakeProfitOrderData


class OrderDataValidator:
    """Validator for order data integrity."""

    @staticmethod
    def validate_basic_order_data(order: OrderData) -> tuple[bool, str]:
        """Validate basic order data."""
        if not order.symbol:
            return False, "Symbol is required"

        if order.quantity <= 0:
            return False, "Order quantity must be positive"

        if not order.order_id:
            return False, "Order ID is required"

        return True, ""

    @staticmethod
    def validate_limit_order_data(order: LimitOrderData) -> tuple[bool, str]:
        """Validate limit order specific data."""
        is_valid, error = OrderDataValidator.validate_basic_order_data(order)
        if not is_valid:
            return is_valid, error

        if order.price <= 0:
            return False, "Limit order price must be positive"

        return True, ""

    @staticmethod
    def validate_stop_order_data(order: StopOrderData) -> tuple[bool, str]:
        """Validate stop order specific data."""
        is_valid, error = OrderDataValidator.validate_basic_order_data(order)
        if not is_valid:
            return is_valid, error

        if order.stop_price <= 0:
            return False, "Stop price must be positive"

        return True, ""

    @staticmethod
    def validate_stop_limit_order_data(order: StopLimitOrderData) -> tuple[bool, str]:
        """Validate stop limit order specific data."""
        is_valid, error = OrderDataValidator.validate_stop_order_data(order)
        if not is_valid:
            return is_valid, error

        if order.limit_price <= 0:
            return False, "Limit price must be positive"

        return True, ""

    @staticmethod
    def validate_take_profit_order_data(order: TakeProfitOrderData) -> tuple[bool, str]:
        """Validate take profit order specific data."""
        is_valid, error = OrderDataValidator.validate_basic_order_data(order)
        if not is_valid:
            return is_valid, error

        if order.target_price <= 0:
            return False, "Target price must be positive"

        return True, ""


class OrderBusinessRuleValidator:
    """Validator for order business rules."""

    @staticmethod
    def validate_price_reasonableness(
        order: OrderData, current_price: Decimal, tolerance_percent: Decimal = Decimal("10")
    ) -> tuple[bool, str]:
        """Validate that order prices are reasonable compared to current market price."""
        if current_price <= 0:
            return False, "Current price must be positive"

        tolerance = current_price * (tolerance_percent / 100)

        if isinstance(order, LimitOrderData):
            if order.side == OrderSide.BUY:
                # Buy limit orders should be at or below market price
                if order.price > current_price + tolerance:
                    return False, f"Buy limit price {order.price} is too far above market price {current_price}"
            # Sell limit orders should be at or above market price
            elif order.price < current_price - tolerance:
                return False, f"Sell limit price {order.price} is too far below market price {current_price}"

        return True, ""

    @staticmethod
    def validate_order_size_limits(order: OrderData, min_quantity: Decimal, max_quantity: Decimal) -> tuple[bool, str]:
        """Validate order quantity is within allowed limits."""
        if order.quantity < min_quantity:
            return False, f"Order quantity {order.quantity} is below minimum {min_quantity}"

        if order.quantity > max_quantity:
            return False, f"Order quantity {order.quantity} is above maximum {max_quantity}"

        return True, ""
