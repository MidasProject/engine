"""ID generation utilities for the trading engine."""

import uuid
from datetime import datetime


class IDGenerator:
    """Utility class for generating unique IDs."""

    def __init__(self):
        """Initialize the ID generator."""
        self._counters: dict[str, int] = {}

    def generate_uuid(self) -> str:
        """Generate a UUID-based ID."""
        return str(uuid.uuid4())

    def generate_sequential_id(self, prefix: str) -> str:
        """Generate a sequential ID with prefix."""
        if prefix not in self._counters:
            self._counters[prefix] = 0

        self._counters[prefix] += 1
        return f"{prefix}_{self._counters[prefix]}"

    def generate_timestamp_id(self, prefix: str) -> str:
        """Generate a timestamp-based ID."""
        timestamp = int(datetime.now().timestamp() * 1000)  # milliseconds
        return f"{prefix}_{timestamp}"

    def generate_order_id(self) -> str:
        """Generate an order ID."""
        return self.generate_sequential_id("order")

    def generate_trade_id(self) -> str:
        """Generate a trade ID."""
        return self.generate_sequential_id("trade")

    def generate_position_id(self) -> str:
        """Generate a position ID."""
        return self.generate_sequential_id("position")

    def generate_account_id(self) -> str:
        """Generate an account ID."""
        return self.generate_uuid()

    def reset_counter(self, prefix: str) -> None:
        """Reset counter for a specific prefix."""
        if prefix in self._counters:
            self._counters[prefix] = 0

    def reset_all_counters(self) -> None:
        """Reset all counters."""
        self._counters.clear()
