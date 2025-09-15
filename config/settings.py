"""Configuration settings for MidasEngine data fetching."""

from pathlib import Path
from typing import Final

# API Configuration
BINANCE_BASE_URL: Final[str] = "https://fapi.binance.com/fapi/v1/klines"
REQUEST_TIMEOUT: Final[int] = 10

# Rate Limiting
API_LIMIT: Final[int] = 499  # Maximum number of klines per request
SLEEP_SECONDS: Final[float] = 0.2  # Delay between requests to respect rate limits

# Retry Configuration
MAX_RETRIES: Final[int] = 5
RETRY_DELAY: Final[float] = 3.0

# File Configuration
DATA_DIR: Final[Path] = Path("raw_data")
CSV_ENCODING: Final[str] = "utf-8"

# Progress Display
PROGRESS_UPDATE_INTERVAL: Final[int] = 10  # Update progress every N loops

# Default Trading Pairs
DEFAULT_COINS: Final[list[str]] = [
    "BTCUSDT",
    "ETHUSDT",
    "XRPUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "DOGEUSDT",
    "TRXUSDT",
    "ADAUSDT",
    "HYPEUSDT",
    "LINKUSDT",
    "SUIUSDT",
    "AVAXUSDT",
    "XLMUSDT",
    "BCHUSDT",
    "HBARUSDT",
    "LEOUSDT",
    "LTCUSDT",
    "TONUSDT",
    "CROUSDT",
    "SHIBUSDT",
]

# CSV Headers for Binance Kline Data
KLINE_HEADERS: Final[list[str]] = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base",
    "taker_buy_quote",
    "ignore",
]
