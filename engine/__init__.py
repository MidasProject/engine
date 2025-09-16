"""MidasEngine Trading Engine.

A comprehensive trading engine built with SOLID principles, featuring:
- Pure data models separated from business logic
- Interface-based design for extensibility
- Dependency injection for testability
- Factory pattern for object creation
- Comprehensive validation
"""

# Core enums
# Core engine components
from .backtest import BacktestEngine
from .enums import (
    FeeType,
    OrderSide,
    OrderStatus,
    OrderType,
    PositionSide,
    PositionStatus,
    TradeStatus,
)

# Factories
from .factories import (
    EngineComponentFactory,
    OrderFactory,
    TradeFactory,
)

# Interfaces
from .interfaces import (
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
    IStrategy,
    ITradeAnalyzer,
)

# Data models
from .models import (
    AccountData,
    BacktestMetrics,
    BacktestResultData,
    Balance,
    Candle,
    Fee,
    FeeConfig,
    LimitOrderData,
    OrderData,
    PositionData,
    StopLimitOrderData,
    StopMarketOrderData,
    StopOrderData,
    TakeProfitOrderData,
    TradeData,
)

# Services
from .services import (
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
from .strategy import Strategy

# Utils
from .utils import (
    IDGenerator,
    PriceUtils,
)

# Validators
from .validators import (
    OrderBusinessRuleValidator,
    OrderDataValidator,
    PositionBusinessRuleValidator,
    PositionDataValidator,
    TradeBusinessRuleValidator,
    TradeDataValidator,
)

__all__ = [
    "AccountData",
    "AccountManager",
    "BacktestAnalyzer",
    "BacktestEngine",
    "BacktestMetrics",
    "BacktestResultData",
    "Balance",
    "BalanceService",
    "Candle",
    "EngineComponentFactory",
    "Fee",
    "FeeCalculator",
    "FeeConfig",
    "FeeService",
    "FeeType",
    "IAccountManager",
    "IBacktestAnalyzer",
    "IBalanceService",
    "IDGenerator",
    "IFeeCalculator",
    "IFeeService",
    "IOrderExecutor",
    "IOrderManager",
    "IOrderValidator",
    "IPnLCalculator",
    "IPositionManager",
    "IStrategy",
    "ITradeAnalyzer",
    "LimitOrderData",
    "OrderBusinessRuleValidator",
    "OrderData",
    "OrderDataValidator",
    "OrderExecutor",
    "OrderFactory",
    "OrderManager",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "OrderValidator",
    "PnLCalculator",
    "PositionBusinessRuleValidator",
    "PositionData",
    "PositionDataValidator",
    "PositionManager",
    "PositionSide",
    "PositionStatus",
    "PriceUtils",
    "StopLimitOrderData",
    "StopMarketOrderData",
    "StopOrderData",
    "Strategy",
    "TakeProfitOrderData",
    "TradeAnalyzer",
    "TradeBusinessRuleValidator",
    "TradeData",
    "TradeDataValidator",
    "TradeFactory",
    "TradeStatus",
]
