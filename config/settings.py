"""Configuration settings for MidasEngine data fetching."""

# Standard library imports
import os
from pathlib import Path
from typing import Any, Final

# Third-party imports
from dotenv import load_dotenv

load_dotenv()

# API Configuration
BINANCE_BASE_URL: Final[str] = "https://fapi.binance.com/fapi/v1/klines"
REQUEST_TIMEOUT: Final[int] = 10

# Rate Limiting
API_LIMIT: Final[int] = 499  # Maximum number of klines per request
SLEEP_SECONDS: Final[float] = 0.25  # Delay between requests to respect rate limits  # 0.142857

# Retry Configuration
MAX_RETRIES: Final[int] = 5
RETRY_DELAY: Final[float] = 600

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

# Database Configuration
DB_CONFIG: Final[dict[str, Any]] = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# Database Batch Processing
DB_BATCH_SIZE: Final[int] = 1000
