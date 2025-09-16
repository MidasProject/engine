"""Candle data models for market data representation."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Candle:
    """Candlestick data structure matching database schema.

    This class represents a single candlestick/kline data point with all fields
    from the database table schema. This is a pure data model with minimal logic.
    """

    id: int | None = None
    open_time: int = 0
    open: Decimal = Decimal("0")
    high: Decimal = Decimal("0")
    low: Decimal = Decimal("0")
    close: Decimal = Decimal("0")
    volume: Decimal = Decimal("0")
    close_time: int = 0
    quote_asset_volume: Decimal = Decimal("0")
    number_of_trades: int = 0
    taker_buy_base: Decimal = Decimal("0")
    taker_buy_quote: Decimal = Decimal("0")
    ignore_field: Decimal = Decimal("0")
    created_at: datetime | None = None

    @classmethod
    def from_binance_data(cls, data: list) -> "Candle":
        """Create Candle from Binance API data format.

        Args:
            data: List containing kline data from Binance API

        Returns:
            Candle instance
        """
        return cls(
            open_time=int(data[0]),
            open=Decimal(str(data[1])),
            high=Decimal(str(data[2])),
            low=Decimal(str(data[3])),
            close=Decimal(str(data[4])),
            volume=Decimal(str(data[5])),
            close_time=int(data[6]),
            quote_asset_volume=Decimal(str(data[7])),
            number_of_trades=int(data[8]),
            taker_buy_base=Decimal(str(data[9])),
            taker_buy_quote=Decimal(str(data[10])),
            ignore_field=Decimal(str(data[11])),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            "id": self.id,
            "open_time": self.open_time,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "close_time": self.close_time,
            "quote_asset_volume": self.quote_asset_volume,
            "number_of_trades": self.number_of_trades,
            "taker_buy_base": self.taker_buy_base,
            "taker_buy_quote": self.taker_buy_quote,
            "ignore_field": self.ignore_field,
            "created_at": self.created_at,
        }
