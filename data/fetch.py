"""Binance Futures Kline Data Fetcher.

This module fetches historical kline (candlestick) data from Binance Futures API
and saves it to CSV files for further analysis.
"""

# Standard library imports
import csv
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Third-party imports
import requests
from tqdm import tqdm

# Local imports
from config.settings import (
    API_LIMIT,
    BINANCE_BASE_URL,
    CSV_ENCODING,
    DATA_DIR,
    DEFAULT_COINS,
    KLINE_HEADERS,
    MAX_RETRIES,
    PROGRESS_UPDATE_INTERVAL,
    REQUEST_TIMEOUT,
    RETRY_DELAY,
    SLEEP_SECONDS,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


class BinanceDataFetcher:
    """Handles fetching and saving Binance Futures kline data."""

    def __init__(self) -> None:
        """Initialize the data fetcher."""
        self._ensure_data_directory()

    def _ensure_data_directory(self) -> None:
        """Create data directory if it doesn't exist."""
        DATA_DIR.mkdir(exist_ok=True)
        logger.info(f"Data directory ensured: {DATA_DIR}")

    @staticmethod
    def _ms_to_datetime_str(timestamp_ms: int) -> str:
        """Convert milliseconds timestamp to readable datetime string.

        Args:
            timestamp_ms: Timestamp in milliseconds

        Returns:
            Formatted datetime string in UTC
        """
        dt = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=UTC)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _fetch_klines(
        self,
        symbol: str,
        interval: str,
        end_time: int,
        max_retries: int = MAX_RETRIES,
        retry_delay: float = RETRY_DELAY,
    ) -> list[list[Any]]:
        """Fetch klines data from Binance API with retry logic.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Time interval (e.g., '1m', '5m', '1h')
            end_time: End time in milliseconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            List of kline data or empty list if failed
        """
        params = {"symbol": symbol, "interval": interval, "limit": API_LIMIT, "endTime": end_time}

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(BINANCE_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                data = response.json()
                logger.debug(f"Successfully fetched {len(data)} klines for {symbol}")
                return data

            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt}/{max_retries} failed for {symbol}: {e}")
                if attempt < max_retries:
                    time.sleep(retry_delay)

        logger.error(f"Failed to fetch data for {symbol} after {max_retries} attempts")
        return []

    def _create_csv_writer(self, file_path: Path) -> tuple[Any, Any]:
        """Create CSV file and writer with headers.

        Args:
            file_path: Path to the CSV file

        Returns:
            Tuple of (file_handle, csv_writer)
        """
        file_handle = open(file_path, mode="w", newline="", encoding=CSV_ENCODING)
        writer = csv.writer(file_handle)
        writer.writerow(KLINE_HEADERS)
        return file_handle, writer

    def _update_progress(self, pbar: tqdm, symbol: str, end_time: int, loop_count: int) -> None:
        """Update progress bar description periodically.

        Args:
            pbar: Progress bar instance
            symbol: Trading pair symbol
            end_time: Current end time being processed
            loop_count: Current loop iteration count
        """
        if loop_count % PROGRESS_UPDATE_INTERVAL == 0:
            readable_time = self._ms_to_datetime_str(end_time)
            pbar.set_description(f"{symbol} — Back to: {readable_time}")

    def fetch_historical_data(self, symbol: str, interval: str) -> bool:
        """Fetch complete historical data for a symbol and interval.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Time interval (e.g., '1m', '5m', '1h')

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting data fetch for {symbol} with interval {interval}")

        output_path = DATA_DIR / f"{symbol.lower()}_{interval}.csv"

        try:
            file_handle, writer = self._create_csv_writer(output_path)
            try:
                end_time = int(time.time() * 1000)
                loop_count = 0

                with tqdm(desc=f"{symbol} — Fetching...", dynamic_ncols=True, unit="klines") as pbar:
                    while True:
                        # Fetch data batch
                        data = self._fetch_klines(symbol, interval, end_time)

                        if not data:
                            logger.info(f"No more data available for {symbol}")
                            break

                        # Write data (newest first)
                        writer.writerows(data[::-1])
                        file_handle.flush()

                        # Update for next iteration
                        end_time = data[0][0] - 1  # Go backward in time
                        loop_count += 1

                        # Update progress display
                        self._update_progress(pbar, symbol, end_time, loop_count)
                        pbar.update(len(data))

                        # Rate limiting
                        time.sleep(SLEEP_SECONDS)

                logger.info(f"Successfully saved {symbol} data to {output_path}")
                return True
            finally:
                file_handle.close()

        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            return False

    def fetch_multiple_symbols(self, symbols: list[str], interval: str = "1m") -> dict[str, bool]:
        """Fetch data for multiple symbols.

        Args:
            symbols: List of trading pair symbols
            interval: Time interval for all symbols

        Returns:
            Dictionary mapping symbol to success status
        """
        logger.info(f"Starting batch fetch for {len(symbols)} symbols")
        results = {}

        for i, symbol in enumerate(symbols, 1):
            logger.info(f"Processing {symbol} ({i}/{len(symbols)})")
            results[symbol] = self.fetch_historical_data(symbol, interval)
            time.sleep(SLEEP_SECONDS)

        # Summary
        successful = sum(results.values())
        failed = len(symbols) - successful
        logger.info(f"Batch fetch completed: {successful} successful, {failed} failed")

        return results


def main(symbols: list[str] | None = None, interval: str = "1m") -> None:
    """Main function to fetch historical data.

    Args:
        symbols: List of symbols to fetch (defaults to DEFAULT_COINS)
        interval: Time interval for data fetching
    """
    if symbols is None:
        symbols = DEFAULT_COINS

    fetcher = BinanceDataFetcher()
    results = fetcher.fetch_multiple_symbols(symbols, interval)

    # Print final summary
    print("\n" + "=" * 50)
    print("FETCH SUMMARY")
    print("=" * 50)

    for symbol, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{symbol:12} | {status}")


if __name__ == "__main__":
    main()
