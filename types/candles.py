"""Data classes for candlestick/kline data structures."""

# Standard library imports
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseCandle:
    """Base candlestick data structure for OHLCV data.

    Attributes:
        open: Opening price
        high: Highest price in the period
        low: Lowest price in the period
        close: Closing price
        volume: Trading volume in base asset
        timestamp: Timestamp of the candle
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        interval: Time interval (e.g., '1m', '5m', '1h')
    """

    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime
    symbol: str
    interval: str

    def __post_init__(self) -> None:
        """Validate candle data after initialization."""
        if self.high < max(self.open, self.close):
            raise ValueError("High price cannot be lower than open or close")
        if self.low > min(self.open, self.close):
            raise ValueError("Low price cannot be higher than open or close")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")


@dataclass
class BinanceKline:
    """Binance-specific kline data structure matching API response format.

    This matches the exact format returned by Binance Futures API for klines.
    """

    open_time: int  # Kline open time (timestamp in ms)
    open_price: str  # Open price (string to preserve precision)
    high_price: str  # High price
    low_price: str  # Low price
    close_price: str  # Close price
    volume: str  # Volume
    close_time: int  # Kline close time (timestamp in ms)
    quote_asset_volume: str  # Quote asset volume
    number_of_trades: int  # Number of trades
    taker_buy_base_volume: str  # Taker buy base asset volume
    taker_buy_quote_volume: str  # Taker buy quote asset volume
    ignore: str  # Unused field

    def to_base_candle(self, symbol: str, interval: str) -> BaseCandle:
        """Convert to BaseCandle format.

        Args:
            symbol: Trading pair symbol
            interval: Time interval

        Returns:
            BaseCandle instance
        """
        return BaseCandle(
            open=float(self.open_price),
            high=float(self.high_price),
            low=float(self.low_price),
            close=float(self.close_price),
            volume=float(self.volume),
            timestamp=datetime.fromtimestamp(self.open_time / 1000.0),
            symbol=symbol,
            interval=interval,
        )
