"""Order management service implementations."""

from datetime import datetime
from decimal import Decimal

from ..enums import OrderSide, OrderStatus, OrderType
from ..interfaces import IBalanceService, IOrderExecutor, IOrderManager, IOrderValidator
from ..models import (
    AccountData,
    LimitOrderData,
    OrderData,
    StopLimitOrderData,
    StopMarketOrderData,
    StopOrderData,
    TakeProfitOrderData,
)


class OrderValidator(IOrderValidator):
    """Service for order validation."""

    def __init__(self, balance_service: IBalanceService):
        """Initialize with balance service dependency."""
        self.balance_service = balance_service

    def validate_order(self, order: OrderData, account: AccountData) -> tuple[bool, str]:
        """Validate an order."""
        # Validate order data
        is_valid_data, data_error = self.validate_order_data(order)
        if not is_valid_data:
            return False, data_error

        # Validate balance
        if not self.validate_balance(order, account):
            return False, "Insufficient balance"

        return True, ""

    def validate_balance(self, order: OrderData, account: AccountData) -> bool:
        """Validate if account has sufficient balance for order."""
        # For buy orders, need base currency (usually USDT)
        if order.side == OrderSide.BUY:
            # For market orders, estimate using current quantity and a price
            # For limit orders, use the exact limit price
            if isinstance(order, LimitOrderData):
                required_amount = order.quantity * order.price
            else:
                # For market orders, we'll need the current price from the caller
                # For now, just check if we have any balance
                required_amount = order.quantity

            return self.balance_service.has_sufficient_balance(account, "USDT", required_amount)

        # For sell orders, need the asset being sold
        # This would require knowing the base asset of the trading pair
        # For simplicity, assume we have sufficient balance for sells
        return True

    def validate_order_data(self, order: OrderData) -> tuple[bool, str]:
        """Validate order data integrity."""
        if order.quantity <= 0:
            return False, "Order quantity must be positive"

        if isinstance(order, LimitOrderData) and order.price <= 0:
            return False, "Limit order price must be positive"

        if isinstance(order, StopOrderData) and order.stop_price <= 0:
            return False, "Stop price must be positive"

        if isinstance(order, StopLimitOrderData) and order.limit_price <= 0:
            return False, "Limit price must be positive"

        if isinstance(order, TakeProfitOrderData) and order.target_price <= 0:
            return False, "Target price must be positive"

        return True, ""


class OrderExecutor(IOrderExecutor):
    """Service for order execution."""

    def can_execute(self, order: OrderData, current_price: Decimal) -> bool:
        """Check if order can be executed at current price."""
        if order.order_type == OrderType.MARKET:
            return True

        if isinstance(order, LimitOrderData):
            return self._can_execute_limit_order(order, current_price)
        if isinstance(order, StopMarketOrderData):
            return self._can_execute_stop_market_order(order, current_price)
        if isinstance(order, StopLimitOrderData):
            return self._can_execute_stop_limit_order(order, current_price)
        if isinstance(order, TakeProfitOrderData):
            return self._can_execute_take_profit_order(order, current_price)

        return False

    def _can_execute_limit_order(self, order: LimitOrderData, current_price: Decimal) -> bool:
        """Check if limit order can execute."""
        if order.side == OrderSide.BUY:
            return current_price <= order.price
        return current_price >= order.price

    def _can_execute_stop_market_order(self, order: StopMarketOrderData, current_price: Decimal) -> bool:
        """Check if stop market order can execute."""
        if order.side == OrderSide.BUY:
            return current_price >= order.stop_price
        return current_price <= order.stop_price

    def _can_execute_stop_limit_order(self, order: StopLimitOrderData, current_price: Decimal) -> bool:
        """Check if stop limit order can execute."""
        if order.side == OrderSide.BUY:
            return current_price >= order.stop_price
        return current_price <= order.stop_price

    def _can_execute_take_profit_order(self, order: TakeProfitOrderData, current_price: Decimal) -> bool:
        """Check if take profit order can execute."""
        if order.side == OrderSide.BUY:
            return current_price >= order.target_price
        return current_price <= order.target_price

    def execute_order(self, order: OrderData, current_price: Decimal, account: AccountData) -> bool:
        """Execute an order."""
        if not self.can_execute(order, current_price):
            return False

        # Mark order as filled
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.now()

        return True


class OrderManager(IOrderManager):
    """Service for order management operations."""

    def __init__(self, validator: IOrderValidator, executor: IOrderExecutor):
        """Initialize with validator and executor dependencies."""
        self.validator = validator
        self.executor = executor
        self._pending_orders: list[OrderData] = []
        self._order_counter = 0

    def create_order(self, symbol: str, side: str, quantity: Decimal, order_type: OrderType, **kwargs) -> OrderData:
        """Create a new order."""
        order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL

        # Generate order ID
        self._order_counter += 1
        order_id = f"order_{self._order_counter}"

        if order_type == OrderType.MARKET:
            return OrderData(
                symbol=symbol,
                side=order_side,
                quantity=quantity,
                order_id=order_id,
                order_type=order_type,
                created_at=datetime.now(),
            )
        elif order_type == OrderType.LIMIT:
            return LimitOrderData(
                symbol=symbol,
                side=order_side,
                quantity=quantity,
                order_id=order_id,
                price=kwargs.get("price", Decimal("0")),
                created_at=datetime.now(),
            )
        elif order_type == OrderType.STOP_MARKET:
            return StopMarketOrderData(
                symbol=symbol,
                side=order_side,
                quantity=quantity,
                order_id=order_id,
                stop_price=kwargs.get("stop_price", Decimal("0")),
                created_at=datetime.now(),
            )
        elif order_type == OrderType.STOP_LIMIT:
            return StopLimitOrderData(
                symbol=symbol,
                side=order_side,
                quantity=quantity,
                order_id=order_id,
                stop_price=kwargs.get("stop_price", Decimal("0")),
                limit_price=kwargs.get("limit_price", Decimal("0")),
                created_at=datetime.now(),
            )
        elif order_type == OrderType.TAKE_PROFIT:
            return TakeProfitOrderData(
                symbol=symbol,
                side=order_side,
                quantity=quantity,
                order_id=order_id,
                target_price=kwargs.get("target_price", Decimal("0")),
                created_at=datetime.now(),
            )
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

    def place_order(self, order: OrderData) -> None:
        """Place an order."""
        self._pending_orders.append(order)

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        for order in self._pending_orders:
            if order.order_id == order_id and order.status == OrderStatus.NEW:
                order.status = OrderStatus.CANCELED
                return True
        return False

    def get_pending_orders(self) -> list[OrderData]:
        """Get all pending orders."""
        return [order for order in self._pending_orders if order.status == OrderStatus.NEW]

    def process_orders(self, current_price: Decimal, account: AccountData) -> list[OrderData]:
        """Process all pending orders and return executed orders."""
        executed_orders = []

        for order in self.get_pending_orders():
            if self.executor.execute_order(order, current_price, account):
                executed_orders.append(order)
                # Remove from pending orders
                if order in self._pending_orders:
                    self._pending_orders.remove(order)

        return executed_orders
