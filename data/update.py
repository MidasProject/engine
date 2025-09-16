"""Database Update Module for MidasEngine.

This module handles incremental updates to keep the database current
with new market data from Binance Futures API.
"""

import logging
import time
from typing import Any

import psycopg2
import requests
from psycopg2.extras import execute_values

from config.settings import (
    API_LIMIT,
    BINANCE_BASE_URL,
    DB_BATCH_SIZE,
    DB_CONFIG,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    RETRY_DELAY,
    SLEEP_SECONDS,
)
from data.db_initialize import (
    INTERVAL_MINUTES,
    SUPPORTED_INTERVALS,
    get_table_name,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


class DatabaseUpdater:
    """Handles incremental database updates with new market data."""

    def __init__(self) -> None:
        """Initialize the database updater."""
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Establish database connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected to PostgreSQL database")
            return True
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def disconnect(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Database connection closed")

    def get_latest_timestamp(self, symbol: str, interval: str) -> int | None:
        """Get the latest timestamp for a symbol and interval.

        Args:
            symbol: Trading pair symbol
            interval: Time interval

        Returns:
            Latest timestamp in milliseconds, or None if no data
        """
        table_name = get_table_name(symbol, interval)
        query = f"SELECT MAX(open_time) as latest FROM {table_name}"

        try:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0] if result and result[0] else None
        except psycopg2.Error as e:
            logger.error(f"Failed to get latest timestamp for {symbol} {interval}: {e}")
            return None

    def fetch_new_data(self, symbol: str, interval: str, start_time: int) -> list[list[Any]]:
        """Fetch new data from Binance API.

        Args:
            symbol: Trading pair symbol
            interval: Time interval
            start_time: Start timestamp in milliseconds

        Returns:
            List of new kline data
        """
        logger.info(f"Fetching new {interval} data for {symbol} from {start_time}")

        all_data = []
        end_time = int(time.time() * 1000)  # Current time in milliseconds

        while start_time < end_time:
            # Calculate batch end time
            batch_end_time = min(start_time + (API_LIMIT * INTERVAL_MINUTES[interval] * 60 * 1000), end_time)

            # Fetch data batch
            data = self._fetch_klines_batch(symbol, interval, batch_end_time)

            if not data:
                logger.warning(f"No more data available for {symbol} {interval}")
                break

            # Filter out data we already have
            new_data = [row for row in data if int(row[0]) > start_time]

            if not new_data:
                logger.info(f"No new data in this batch for {symbol} {interval}")
                break

            all_data.extend(new_data)
            logger.info(f"Fetched {len(new_data)} new records for {symbol} {interval}")

            # Update start time for next batch
            start_time = int(data[0][0]) + 1

            # Rate limiting
            time.sleep(SLEEP_SECONDS)

        logger.info(f"Total new data fetched for {symbol} {interval}: {len(all_data)} records")
        return all_data

    def _fetch_klines_batch(self, symbol: str, interval: str, end_time: int) -> list[list[Any]]:
        """Fetch a batch of klines from Binance API.

        Args:
            symbol: Trading pair symbol
            interval: Time interval
            end_time: End time in milliseconds

        Returns:
            List of kline data or empty list if failed
        """
        params = {"symbol": symbol, "interval": interval, "limit": API_LIMIT, "endTime": end_time}

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(BINANCE_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                data = response.json()
                logger.debug(f"Successfully fetched {len(data)} klines for {symbol} {interval}")
                return data

            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt}/{MAX_RETRIES} failed for {symbol} {interval}: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)

        logger.error(f"Failed to fetch data for {symbol} {interval} after {MAX_RETRIES} attempts")
        return []

    def aggregate_to_interval(self, data_1m: list[list[Any]], target_interval: str) -> list[list[Any]]:
        """Aggregate 1-minute data to target interval.

        Args:
            data_1m: List of 1-minute kline data
            target_interval: Target interval (e.g., '5m', '1h', '1D')

        Returns:
            Aggregated data for target interval
        """
        if target_interval == "1m":
            return data_1m

        target_minutes = INTERVAL_MINUTES[target_interval]
        aggregated_data = []

        # Group data by target interval
        current_group = []
        current_open_time = None

        for row in data_1m:
            open_time = int(row[0])  # open_time in milliseconds
            # close_time = int(row[6])  # close_time in milliseconds

            # Calculate the start of the target interval
            interval_start = self._get_interval_start(open_time, target_minutes)

            if current_open_time is None or interval_start != current_open_time:
                # Save previous group if exists
                if current_group:
                    aggregated_data.append(self._aggregate_group(current_group))

                # Start new group
                current_group = [row]
                current_open_time = interval_start
            else:
                # Add to current group
                current_group.append(row)

        # Don't forget the last group
        if current_group:
            aggregated_data.append(self._aggregate_group(current_group))

        return aggregated_data

    def _get_interval_start(self, timestamp_ms: int, interval_minutes: int) -> int:
        """Get the start timestamp of the interval containing the given timestamp.

        Args:
            timestamp_ms: Timestamp in milliseconds
            interval_minutes: Interval in minutes

        Returns:
            Start timestamp of the interval in milliseconds
        """
        # Convert to seconds and get the interval start
        timestamp_sec = timestamp_ms // 1000
        interval_sec = interval_minutes * 60

        # Calculate the start of the interval
        interval_start_sec = (timestamp_sec // interval_sec) * interval_sec

        return interval_start_sec * 1000

    def _aggregate_group(self, group: list[list[Any]]) -> list[Any]:
        """Aggregate a group of 1-minute candles into a single candle.

        Args:
            group: List of 1-minute candle data

        Returns:
            Aggregated candle data
        """
        if not group:
            return []

        # Sort by open_time to ensure correct order
        group.sort(key=lambda x: int(x[0]))

        # First candle
        first_candle = group[0]
        # Last candle
        last_candle = group[-1]

        # Open time and close time
        open_time = int(first_candle[0])
        close_time = int(last_candle[6])

        # OHLC
        open_price = float(first_candle[1])
        close_price = float(last_candle[4])

        # High and low
        high_price = max(float(candle[2]) for candle in group)
        low_price = min(float(candle[3]) for candle in group)

        # Volume and other metrics (sum them up)
        volume = sum(float(candle[5]) for candle in group)
        quote_asset_volume = sum(float(candle[7]) for candle in group)
        number_of_trades = sum(int(candle[8]) for candle in group)
        taker_buy_base = sum(float(candle[9]) for candle in group)
        taker_buy_quote = sum(float(candle[10]) for candle in group)
        ignore_field = sum(float(candle[11]) for candle in group)

        return [
            open_time,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            close_time,
            quote_asset_volume,
            number_of_trades,
            taker_buy_base,
            taker_buy_quote,
            ignore_field,
        ]

    def insert_new_data(self, symbol: str, interval: str, data: list[list[Any]]) -> bool:
        """Insert new data into the appropriate table.

        Args:
            symbol: Trading pair symbol
            interval: Time interval
            data: Kline data to insert

        Returns:
            True if successful, False otherwise
        """
        if not data:
            return True

        table_name = get_table_name(symbol, interval)

        insert_sql = f"""
        INSERT INTO {table_name} (
            open_time, open, high, low, close, volume,
            close_time, quote_asset_volume, number_of_trades, taker_buy_base,
            taker_buy_quote, ignore_field
        ) VALUES %s
        ON CONFLICT (open_time) DO NOTHING
        """

        try:
            # Process in batches
            batch_size = DB_BATCH_SIZE
            for i in range(0, len(data), batch_size):
                batch = data[i : i + batch_size]
                execute_values(self.cursor, insert_sql, batch, template=None, page_size=batch_size)

            self.connection.commit()
            logger.info(f"Successfully inserted {len(data)} records into {table_name}")
            return True

        except psycopg2.Error as e:
            logger.error(f"Failed to insert data into {table_name}: {e}")
            self.connection.rollback()
            return False

    def update_symbol(self, symbol: str) -> bool:
        """Update all intervals for a specific symbol.

        Args:
            symbol: Trading pair symbol

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Updating {symbol}...")

        # Get latest 1m timestamp
        latest_1m = self.get_latest_timestamp(symbol, "1m")
        if latest_1m is None:
            logger.warning(f"No existing data found for {symbol}, skipping update")
            return True

        # Fetch new 1m data
        new_1m_data = self.fetch_new_data(symbol, "1m", latest_1m + 1)
        if not new_1m_data:
            logger.info(f"No new data available for {symbol}")
            return True

        # Process each interval
        success = True
        for interval in SUPPORTED_INTERVALS:
            logger.info(f"Processing {symbol} {interval}...")

            # Aggregate data to target interval
            aggregated_data = self.aggregate_to_interval(new_1m_data, interval)

            if aggregated_data:
                # Insert new data
                if not self.insert_new_data(symbol, interval, aggregated_data):
                    success = False
                    logger.error(f"Failed to update {symbol} {interval}")
                else:
                    logger.info(f"Updated {symbol} {interval}: {len(aggregated_data)} records")
            else:
                logger.warning(f"No aggregated data for {symbol} {interval}")

        return success

    def update_all_symbols(self) -> bool:
        """Update all symbols in the database.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting database update for all symbols")

        if not self.connect():
            return False

        try:
            # Get all symbols from database
            symbols = self._get_all_symbols()
            if not symbols:
                logger.warning("No symbols found in database")
                return True

            logger.info(f"Found {len(symbols)} symbols to update: {symbols}")

            # Update each symbol
            successful = 0
            failed = 0

            for symbol in symbols:
                if self.update_symbol(symbol):
                    successful += 1
                else:
                    failed += 1

            # Summary
            logger.info(f"Update completed: {successful} symbols successful, {failed} failed")

            return failed == 0

        finally:
            self.disconnect()

    def _get_all_symbols(self) -> list[str]:
        """Get all symbols from the database.

        Returns:
            List of symbols
        """
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name LIKE '%_1m'
        ORDER BY table_name
        """
        results = self.execute_query(query)
        if results:
            symbols = []
            for row in results:
                table_name = row["table_name"]
                symbol = table_name.replace("_1m", "").upper()
                symbols.append(symbol)
            return symbols
        return []

    def execute_query(self, query: str, params: tuple | None = None) -> list[dict] | None:
        """Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Query results as list of dictionaries or None
        """
        if not self.connection:
            logger.error("No database connection available")
            return None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row, strict=False)) for row in results]

        except psycopg2.Error as e:
            logger.error(f"Query execution failed: {e}")
            return None


def main() -> None:
    """Main function to update the database."""
    updater = DatabaseUpdater()
    success = updater.update_all_symbols()

    if success:
        print("\n" + "=" * 60)
        print("DATABASE UPDATE SUCCESSFUL")
        print("=" * 60)
        print("✅ All symbols updated with latest data")
        print("✅ Database is now current with market data")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("DATABASE UPDATE FAILED")
        print("=" * 60)
        print("❌ Some symbols failed to update")
        print("❌ Check logs for error details")
        print("=" * 60)


if __name__ == "__main__":
    main()
