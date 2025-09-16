"""Abstract interfaces and protocols for the trading engine.

This module contains abstract base classes and protocols that define
contracts for various trading engine components.
"""

from .account import IAccountManager, IBalanceService
from .analysis import IBacktestAnalyzer, ITradeAnalyzer
from .fees import IFeeCalculator, IFeeService
from .orders import IOrderExecutor, IOrderManager, IOrderValidator
from .positions import IPnLCalculator, IPositionManager
from .strategy import IStrategy

__all__ = [
    "IAccountManager",
    "IBacktestAnalyzer",
    "IBalanceService",
    "IFeeCalculator",
    "IFeeService",
    "IOrderExecutor",
    "IOrderManager",
    "IOrderValidator",
    "IPnLCalculator",
    "IPositionManager",
    "IStrategy",
    "ITradeAnalyzer",
]
