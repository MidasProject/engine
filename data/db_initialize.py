"""PostgreSQL Database Initialization for MidasEngine.

This module initializes a PostgreSQL database and ingests all CSV files
from the raw_data directory into the database. Creates 15 separate tables
per symbol for optimal chart rendering performance.
"""

import csv
import logging
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import execute_values

from config.settings import DATA_DIR, DB_BATCH_SIZE, DB_CONFIG, KLINE_HEADERS

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

# Supported intervals for chart rendering
SUPPORTED_INTERVALS = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1D", "3D", "1W", "1M"]

# Interval to minutes mapping for aggregation
INTERVAL_MINUTES = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "2h": 120,
    "4h": 240,
    "6h": 360,
    "8h": 480,
    "12h": 720,
    "1D": 1440,
    "3D": 4320,
    "1W": 10080,
    "1M": 43200,  # Approximate
}


class DatabaseInitializer:
    """Handles PostgreSQL database initialization and CSV data ingestion."""

    def __init__(self, db_config: dict[str, Any]) -> None:
        """Initialize the database initializer.

        Args:
            db_config: Database connection configuration
        """
        self.db_config = db_config
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Establish database connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(**self.db_config)
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

    def create_tables_for_symbol(self, symbol: str) -> bool:
        """Create 15 tables for a specific symbol (one per interval).

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            True if successful, False otherwise
        """
        symbol_lower = symbol.lower()

        # Base table schema for each interval
        table_schema = """
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            open_time BIGINT NOT NULL,
            open DECIMAL(20, 8) NOT NULL,
            high DECIMAL(20, 8) NOT NULL,
            low DECIMAL(20, 8) NOT NULL,
            close DECIMAL(20, 8) NOT NULL,
            volume DECIMAL(20, 8) NOT NULL,
            close_time BIGINT NOT NULL,
            quote_asset_volume DECIMAL(20, 8) NOT NULL,
            number_of_trades INTEGER NOT NULL,
            taker_buy_base DECIMAL(20, 8) NOT NULL,
            taker_buy_quote DECIMAL(20, 8) NOT NULL,
            ignore_field DECIMAL(20, 8) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(open_time)
        );
        """

        # Index creation SQL for each table
        index_sqls = [
            "CREATE INDEX IF NOT EXISTS idx_{table_name}_open_time ON {table_name}(open_time);",
            "CREATE INDEX IF NOT EXISTS idx_{table_name}_close_time ON {table_name}(close_time);",
            "CREATE INDEX IF NOT EXISTS idx_{table_name}_time_range ON {table_name}(open_time, close_time);",
        ]

        try:
            # Create table for each interval
            for interval in SUPPORTED_INTERVALS:
                table_name = f"{symbol_lower}_{interval}"
                create_sql = table_schema.format(table_name=table_name)
                self.cursor.execute(create_sql)

                # Create indexes for this table
                for index_sql in index_sqls:
                    formatted_index_sql = index_sql.format(table_name=table_name)
                    self.cursor.execute(formatted_index_sql)

            self.connection.commit()
            logger.info(f"Created 15 tables for {symbol}")
            return True

        except psycopg2.Error as e:
            logger.error(f"Failed to create tables for {symbol}: {e}")
            self.connection.rollback()
            return False

    def create_all_tables(self, symbols: list[str]) -> bool:
        """Create tables for all symbols.

        Args:
            symbols: List of trading pair symbols

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Creating tables for {len(symbols)} symbols...")

        for symbol in symbols:
            if not self.create_tables_for_symbol(symbol):
                return False

        logger.info(f"Successfully created {len(symbols) * len(SUPPORTED_INTERVALS)} tables")
        return True

    def get_csv_files(self) -> list[Path]:
        """Get all CSV files from the raw_data directory.

        Returns:
            List of CSV file paths
        """
        raw_data_dir = DATA_DIR / "raw_data"
        if not raw_data_dir.exists():
            logger.error(f"Raw data directory not found: {raw_data_dir}")
            return []

        csv_files = list(raw_data_dir.glob("*.csv"))
        logger.info(f"Found {len(csv_files)} CSV files to process")
        return csv_files

    def extract_symbol_interval(self, filename: str) -> tuple[str, str]:
        """Extract symbol and interval from filename.

        Args:
            filename: CSV filename (e.g., 'btcusdt_1m.csv')

        Returns:
            Tuple of (symbol, interval)
        """
        # Remove .csv extension and split by underscore
        name_parts = filename.replace(".csv", "").split("_")
        MIN_PARTS_FOR_SYMBOL_INTERVAL = 2
        if len(name_parts) >= MIN_PARTS_FOR_SYMBOL_INTERVAL:
            symbol = name_parts[0].upper()
            interval = name_parts[1]
            return symbol, interval
        else:
            logger.warning(f"Could not parse symbol and interval from filename: {filename}")
            return filename.upper().replace(".csv", ""), "1m"

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

    def process_csv_file(self, csv_file: Path) -> bool:
        """Process a single CSV file and insert data into all interval tables.

        Args:
            csv_file: Path to the CSV file

        Returns:
            True if successful, False otherwise
        """
        symbol, interval = self.extract_symbol_interval(csv_file.name)
        logger.info(f"Processing {csv_file.name} -> Symbol: {symbol}, Source Interval: {interval}")

        # Only process 1m data for aggregation
        if interval != "1m":
            logger.warning(f"Skipping {csv_file.name} - only 1m data is processed for aggregation")
            return True

        try:
            # Read 1m data from CSV
            data_1m = []
            with open(csv_file, encoding="utf-8") as file:
                # Skip header row
                next(file)

                for row in csv.reader(file):
                    if len(row) == len(KLINE_HEADERS):
                        # Convert string values to appropriate types
                        processed_row = [
                            int(row[0]),  # open_time
                            float(row[1]),  # open
                            float(row[2]),  # high
                            float(row[3]),  # low
                            float(row[4]),  # close
                            float(row[5]),  # volume
                            int(row[6]),  # close_time
                            float(row[7]),  # quote_asset_volume
                            int(row[8]),  # number_of_trades
                            float(row[9]),  # taker_buy_base
                            float(row[10]),  # taker_buy_quote
                            float(row[11]),  # ignore_field
                        ]
                        data_1m.append(processed_row)

            if not data_1m:
                logger.warning(f"No data found in {csv_file.name}")
                return True

            logger.info(f"Loaded {len(data_1m)} 1m records for {symbol}")

            # Process each interval
            total_inserted = 0
            for target_interval in SUPPORTED_INTERVALS:
                logger.info(f"Aggregating {symbol} data to {target_interval} interval...")

                # Aggregate data to target interval
                aggregated_data = self.aggregate_to_interval(data_1m, target_interval)

                if not aggregated_data:
                    logger.warning(f"No aggregated data for {symbol} {target_interval}")
                    continue

                # Insert into appropriate table
                success = self._insert_interval_data(symbol, target_interval, aggregated_data)
                if success:
                    total_inserted += len(aggregated_data)
                    logger.info(f"Inserted {len(aggregated_data)} {target_interval} records for {symbol}")
                else:
                    logger.error(f"Failed to insert {target_interval} data for {symbol}")
                    return False

            logger.info(f"Successfully processed {symbol}: {total_inserted} total records across all intervals")
            return True

        except Exception as e:
            logger.error(f"Failed to process {csv_file.name}: {e}")
            self.connection.rollback()
            return False

    def _insert_interval_data(self, symbol: str, interval: str, data: list[list[Any]]) -> bool:
        """Insert data into specific interval table.

        Args:
            symbol: Trading pair symbol
            interval: Time interval
            data: Kline data to insert

        Returns:
            True if successful, False otherwise
        """
        table_name = f"{symbol.lower()}_{interval}"

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
            return True

        except psycopg2.Error as e:
            logger.error(f"Failed to insert data into {table_name}: {e}")
            self.connection.rollback()
            return False

    def initialize_database(self) -> bool:
        """Initialize database and ingest all CSV files.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting database initialization with 15 tables per symbol")

        # Connect to database
        if not self.connect():
            return False

        try:
            # Get all CSV files to determine symbols
            csv_files = self.get_csv_files()
            if not csv_files:
                logger.warning("No CSV files found to process")
                return True

            # Extract unique symbols from CSV files
            symbols = set()
            for csv_file in csv_files:
                symbol, _ = self.extract_symbol_interval(csv_file.name)
                symbols.add(symbol)

            symbols = list(symbols)
            logger.info(f"Found {len(symbols)} unique symbols: {symbols}")

            # Create tables for all symbols
            if not self.create_all_tables(symbols):
                return False

            # Process each CSV file
            successful_files = 0
            failed_files = 0

            for csv_file in csv_files:
                if self.process_csv_file(csv_file):
                    successful_files += 1
                else:
                    failed_files += 1

            # Summary
            logger.info(
                f"Database initialization completed: {successful_files} files processed successfully, {failed_files} failed"
            )

            # Get final statistics
            self._print_database_stats(symbols)

            return failed_files == 0

        finally:
            self.disconnect()

    def _print_database_stats(self, symbols: list[str]) -> None:
        """Print database statistics for all tables.

        Args:
            symbols: List of symbols to check
        """
        logger.info("=" * 60)
        logger.info("DATABASE STATISTICS")
        logger.info("=" * 60)

        total_tables = 0
        total_rows = 0

        for symbol in symbols:
            symbol_lower = symbol.lower()
            logger.info(f"\n{symbol} Tables:")

            for interval in SUPPORTED_INTERVALS:
                table_name = f"{symbol_lower}_{interval}"
                try:
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = self.cursor.fetchone()[0]
                    total_tables += 1
                    total_rows += row_count
                    logger.info(f"  {interval:4}: {row_count:>8,} records")
                except psycopg2.Error as e:
                    logger.warning(f"  {interval:4}: Error - {e}")

        logger.info(f"\nTotal: {total_tables} tables, {total_rows:,} records")
        logger.info("=" * 60)


def get_table_name(symbol: str, interval: str) -> str:
    """Get the table name for a symbol and interval.

    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        interval: Time interval (e.g., '1m', '5m', '1h')

    Returns:
        Table name (e.g., 'btcusdt_1m')
    """
    return f"{symbol.lower()}_{interval}"


def main() -> None:
    """Main function to initialize the database."""
    # Use database configuration from settings
    # You can override these values by modifying config/settings.py
    # or by using environment variables
    initializer = DatabaseInitializer(DB_CONFIG)
    success = initializer.initialize_database()

    if success:
        print("\n" + "=" * 60)
        print("DATABASE INITIALIZATION SUCCESSFUL")
        print("=" * 60)
        print("✅ All CSV files have been ingested into PostgreSQL")
        print("✅ 15 tables per symbol created for optimal performance")
        print("✅ All intervals aggregated from 1m data")
        print("✅ Ready for ultra-fast chart rendering!")
        print("\nTable naming convention: {symbol}_{interval}")
        print("Example: btcusdt_1m, btcusdt_5m, btcusdt_1h, etc.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("DATABASE INITIALIZATION FAILED")
        print("=" * 60)
        print("❌ Please check the logs for error details")
        print("=" * 60)


if __name__ == "__main__":
    main()
