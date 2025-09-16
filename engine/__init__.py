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
    LimitOrderParams,
    MarketOrderParams,
    OrderData,
    PositionData,
    PositionParams,
    StopLimitOrderData,
    StopLimitOrderParams,
    StopMarketOrderData,
    StopMarketOrderParams,
    StopOrderData,
    TakeProfitOrderData,
    TakeProfitOrderParams,
    TradeData,
    TradeFromOrderPositionParams,
    TradeParams,
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
    BollingerBands,
    IDGenerator,
    IndicatorUtils,
    MovingAverages,
    PriceIndicators,
    PriceUtils,
    SupportResistance,
    TrendIndicators,
    VolumeIndicators,
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
    "BollingerBands",
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
    "IndicatorUtils",
    "LimitOrderData",
    "LimitOrderParams",
    "MarketOrderParams",
    "MovingAverages",
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
    "PositionParams",
    "PositionSide",
    "PositionStatus",
    "PriceIndicators",
    "PriceUtils",
    "StopLimitOrderData",
    "StopLimitOrderParams",
    "StopMarketOrderData",
    "StopMarketOrderParams",
    "StopOrderData",
    "Strategy",
    "SupportResistance",
    "TakeProfitOrderData",
    "TakeProfitOrderParams",
    "TradeAnalyzer",
    "TradeBusinessRuleValidator",
    "TradeData",
    "TradeDataValidator",
    "TradeFactory",
    "TradeFromOrderPositionParams",
    "TradeParams",
    "TradeStatus",
    "TrendIndicators",
    "VolumeIndicators",
]
