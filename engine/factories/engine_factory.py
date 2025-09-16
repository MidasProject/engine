"""Factory for creating engine components with proper dependency injection."""

from ..interfaces import (
    IAccountManager,
    IBacktestAnalyzer,
    IBalanceService,
    IFeeCalculator,
    IFeeService,
    IOrderExecutor,
    IOrderManager,
    IOrderValidator,
    IPnLCalculator,
    IPositionManager,
    ITradeAnalyzer,
)
from ..models import FeeConfig
from ..services import (
    AccountManager,
    BacktestAnalyzer,
    BalanceService,
    FeeCalculator,
    FeeService,
    OrderExecutor,
    OrderManager,
    OrderValidator,
    PnLCalculator,
    PositionManager,
    TradeAnalyzer,
)
from .order_factory import OrderFactory
from .trade_factory import TradeFactory


class EngineComponentFactory:
    """Factory for creating engine components with proper dependency injection."""

    def __init__(self, fee_config: FeeConfig | None = None):
        """Initialize the factory with optional fee configuration."""
        self._fee_config = fee_config or FeeConfig()
        self._components = {}

    def create_balance_service(self) -> IBalanceService:
        """Create a balance service."""
        if "balance_service" not in self._components:
            self._components["balance_service"] = BalanceService()
        return self._components["balance_service"]

    def create_account_manager(self) -> IAccountManager:
        """Create an account manager with dependencies."""
        if "account_manager" not in self._components:
            balance_service = self.create_balance_service()
            self._components["account_manager"] = AccountManager(balance_service)
        return self._components["account_manager"]

    def create_pnl_calculator(self) -> IPnLCalculator:
        """Create a PnL calculator."""
        if "pnl_calculator" not in self._components:
            self._components["pnl_calculator"] = PnLCalculator()
        return self._components["pnl_calculator"]

    def create_position_manager(self) -> IPositionManager:
        """Create a position manager with dependencies."""
        if "position_manager" not in self._components:
            pnl_calculator = self.create_pnl_calculator()
            self._components["position_manager"] = PositionManager(pnl_calculator)
        return self._components["position_manager"]

    def create_fee_calculator(self) -> IFeeCalculator:
        """Create a fee calculator."""
        if "fee_calculator" not in self._components:
            self._components["fee_calculator"] = FeeCalculator(self._fee_config)
        return self._components["fee_calculator"]

    def create_fee_service(self) -> IFeeService:
        """Create a fee service."""
        if "fee_service" not in self._components:
            self._components["fee_service"] = FeeService(self._fee_config)
        return self._components["fee_service"]

    def create_order_validator(self) -> IOrderValidator:
        """Create an order validator with dependencies."""
        if "order_validator" not in self._components:
            balance_service = self.create_balance_service()
            self._components["order_validator"] = OrderValidator(balance_service)
        return self._components["order_validator"]

    def create_order_executor(self) -> IOrderExecutor:
        """Create an order executor."""
        if "order_executor" not in self._components:
            self._components["order_executor"] = OrderExecutor()
        return self._components["order_executor"]

    def create_order_manager(self) -> IOrderManager:
        """Create an order manager with dependencies."""
        if "order_manager" not in self._components:
            validator = self.create_order_validator()
            executor = self.create_order_executor()
            self._components["order_manager"] = OrderManager(validator, executor)
        return self._components["order_manager"]

    def create_trade_analyzer(self) -> ITradeAnalyzer:
        """Create a trade analyzer."""
        if "trade_analyzer" not in self._components:
            self._components["trade_analyzer"] = TradeAnalyzer()
        return self._components["trade_analyzer"]

    def create_backtest_analyzer(self) -> IBacktestAnalyzer:
        """Create a backtest analyzer with dependencies."""
        if "backtest_analyzer" not in self._components:
            trade_analyzer = self.create_trade_analyzer()
            self._components["backtest_analyzer"] = BacktestAnalyzer(trade_analyzer)
        return self._components["backtest_analyzer"]

    def create_order_factory(self) -> OrderFactory:
        """Create an order factory."""
        if "order_factory" not in self._components:
            self._components["order_factory"] = OrderFactory()
        return self._components["order_factory"]

    def create_trade_factory(self) -> TradeFactory:
        """Create a trade factory."""
        if "trade_factory" not in self._components:
            self._components["trade_factory"] = TradeFactory()
        return self._components["trade_factory"]

    def create_full_engine_components(self) -> dict:
        """Create all engine components with proper dependencies."""
        return {
            "balance_service": self.create_balance_service(),
            "account_manager": self.create_account_manager(),
            "pnl_calculator": self.create_pnl_calculator(),
            "position_manager": self.create_position_manager(),
            "fee_calculator": self.create_fee_calculator(),
            "fee_service": self.create_fee_service(),
            "order_validator": self.create_order_validator(),
            "order_executor": self.create_order_executor(),
            "order_manager": self.create_order_manager(),
            "trade_analyzer": self.create_trade_analyzer(),
            "backtest_analyzer": self.create_backtest_analyzer(),
            "order_factory": self.create_order_factory(),
            "trade_factory": self.create_trade_factory(),
        }
