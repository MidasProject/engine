"""
Database utility functions for MidasEngine.

This module provides common database operations and utilities
for working with the PostgreSQL database with 15 tables per symbol.
"""

import logging
from datetime import datetime
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from config.settings import DB_CONFIG
from data.db_initialize import SUPPORTED_INTERVALS, get_table_name

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and common operations."""

    def __init__(self, db_config: dict[str, Any] | None = None) -> None:
        """Initialize database manager.

        Args:
            db_config: Database configuration (uses default if None)
        """
        self.db_config = db_config or DB_CONFIG
        self.connection = None

    def connect(self) -> bool:
        """Establish database connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("Successfully connected to PostgreSQL database")
            return True
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def execute_query(self, query: str, params: tuple | None = None, fetch: bool = True) -> list[dict] | None:
        """Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results

        Returns:
            Query results as list of dictionaries or None
        """
        if not self.connection:
            logger.error("No database connection available")
            return None

        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)

                if fetch:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                else:
                    self.connection.commit()
                    return None

        except psycopg2.Error as e:
            logger.error(f"Query execution failed: {e}")
            self.connection.rollback()
            return None

    def get_symbols(self) -> list[str]:
        """Get all unique symbols from the database.

        Returns:
            List of unique symbols
        """
        # Get symbols by checking which tables exist
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name LIKE '%_1m'
        ORDER BY table_name
        """
        results = self.execute_query(query)
        if results:
            # Extract symbol from table name (e.g., 'btcusdt_1m' -> 'BTCUSDT')
            symbols = []
            for row in results:
                table_name = row["table_name"]
                symbol = table_name.replace("_1m", "").upper()
                symbols.append(symbol)
            return symbols
        return []

    def get_intervals(self) -> list[str]:
        """Get all supported intervals.

        Returns:
            List of supported intervals
        """
        return SUPPORTED_INTERVALS.copy()

    def get_data_count(self, symbol: str | None = None, interval: str | None = None) -> int:
        """Get total number of records in the database.

        Args:
            symbol: Filter by specific symbol
            interval: Filter by specific interval

        Returns:
            Number of records
        """
        if symbol and interval:
            # Count records in specific table
            table_name = get_table_name(symbol, interval)
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            results = self.execute_query(query)
            return results[0]["count"] if results else 0
        elif symbol:
            # Count records across all intervals for symbol
            total_count = 0
            for interval_name in SUPPORTED_INTERVALS:
                table_name = get_table_name(symbol, interval_name)
                query = f"SELECT COUNT(*) as count FROM {table_name}"
                results = self.execute_query(query)
                if results:
                    total_count += results[0]["count"]
            return total_count
        else:
            # Count all records across all tables
            total_count = 0
            symbols = self.get_symbols()
            for symbol_name in symbols:
                for interval_name in SUPPORTED_INTERVALS:
                    table_name = get_table_name(symbol_name, interval_name)
                    query = f"SELECT COUNT(*) as count FROM {table_name}"
                    results = self.execute_query(query)
                    if results:
                        total_count += results[0]["count"]
            return total_count

    def get_latest_data(self, symbol: str, interval: str, limit: int = 100) -> list[dict]:
        """Get latest kline data for a symbol and interval.

        Args:
            symbol: Trading pair symbol
            interval: Time interval
            limit: Maximum number of records to return

        Returns:
            List of kline data records
        """
        table_name = get_table_name(symbol, interval)
        query = f"""
        SELECT * FROM {table_name}
        ORDER BY open_time DESC
        LIMIT %s
        """
        return self.execute_query(query, (limit,)) or []

    def get_data_range(self, symbol: str, interval: str, start_time: int, end_time: int) -> list[dict]:
        """Get kline data for a specific time range.

        Args:
            symbol: Trading pair symbol
            interval: Time interval
            start_time: Start timestamp (milliseconds)
            end_time: End timestamp (milliseconds)

        Returns:
            List of kline data records
        """
        table_name = get_table_name(symbol, interval)
        query = f"""
        SELECT * FROM {table_name}
        WHERE open_time >= %s AND open_time <= %s
        ORDER BY open_time ASC
        """
        return self.execute_query(query, (start_time, end_time)) or []

    def get_database_stats(self) -> dict[str, Any]:
        """Get database statistics.

        Returns:
            Dictionary with database statistics
        """
        stats = {}

        # Get all symbols
        symbols = self.get_symbols()
        stats["symbol_count"] = len(symbols)
        stats["interval_count"] = len(SUPPORTED_INTERVALS)

        # Total records
        stats["total_records"] = self.get_data_count()

        # Records by symbol
        stats["by_symbol"] = {}
        for symbol in symbols:
            count = self.get_data_count(symbol=symbol)
            stats["by_symbol"][symbol] = count

        # Records by interval
        stats["by_interval"] = {}
        for interval in SUPPORTED_INTERVALS:
            count = 0
            for symbol in symbols:
                count += self.get_data_count(symbol=symbol, interval=interval)
            stats["by_interval"][interval] = count

        # Date range (get from 1m tables)
        earliest = None
        latest = None
        for symbol in symbols:
            table_name = get_table_name(symbol, "1m")
            query = f"""
            SELECT
                MIN(open_time) as earliest,
                MAX(open_time) as latest
            FROM {table_name}
            """
            results = self.execute_query(query)
            if results and results[0]["earliest"]:
                if earliest is None or results[0]["earliest"] < earliest:
                    earliest = results[0]["earliest"]
                if latest is None or results[0]["latest"] > latest:
                    latest = results[0]["latest"]

        stats["earliest"] = earliest
        stats["latest"] = latest

        return stats


def main() -> None:
    """Test database connection and display statistics."""
    db_manager = DatabaseManager()

    if not db_manager.connect():
        print("❌ Failed to connect to database")
        return

    try:
        stats = db_manager.get_database_stats()

        print("\n" + "=" * 50)
        print("DATABASE STATISTICS")
        print("=" * 50)
        print(f"Total Records: {stats.get('total_records', 0):,}")
        print(f"Unique Symbols: {stats.get('symbol_count', 0)}")
        print(f"Unique Intervals: {stats.get('interval_count', 0)}")

        if stats.get("earliest") and stats.get("latest"):
            earliest = datetime.fromtimestamp(stats["earliest"] / 1000)
            latest = datetime.fromtimestamp(stats["latest"] / 1000)
            print(f"Date Range: {earliest} to {latest}")

        print("\nRecords by Symbol:")
        for symbol, count in list(stats.get("by_symbol", {}).items())[:10]:
            print(f"  {symbol}: {count:,}")

        print("\nRecords by Interval:")
        for interval, count in stats.get("by_interval", {}).items():
            print(f"  {interval}: {count:,}")

    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    main()
