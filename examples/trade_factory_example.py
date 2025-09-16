"""Example demonstrating the TradeFactory with parameter classes.

This example shows how to use both methods of the TradeFactory:
1. create_trade_from_order_and_position (using TradeFromOrderPositionParams)
2. create_trade (using TradeParams)
"""

from datetime import datetime
from decimal import Decimal

from engine import (
    OrderData,
    OrderSide,
    OrderType,
    PositionData,
    PositionSide,
    PositionStatus,
    TradeFactory,
    TradeFromOrderPositionParams,
    TradeParams,
)


def main():
    """Demonstrate the TradeFactory parameter classes."""
    print("🏭 Trade Factory Parameter Classes Example")
    print("=" * 50)

    # Create trade factory
    factory = TradeFactory()

    # 1. Create sample order and position
    print("\n📋 Creating Sample Order and Position:")

    sample_order = OrderData(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        quantity=Decimal("0.01"),
        order_id="order_123",
        order_type=OrderType.MARKET,
        created_at=datetime.now(),
    )

    sample_position = PositionData(
        symbol="BTCUSDT",
        side=PositionSide.LONG,
        size=Decimal("0.01"),
        entry_price=Decimal("50000"),
        current_price=Decimal("50000"),
        leverage=1,
        position_id="position_123",
        entry_time=datetime.now(),
        status=PositionStatus.OPEN,
    )

    print(f"  Order: {sample_order.side.value} {sample_order.quantity} {sample_order.symbol}")
    print(f"  Position: {sample_position.side.value} {sample_position.size} at ${sample_position.entry_price}")

    # 2. Create trade using TradeFromOrderPositionParams
    print("\n🔗 Creating Trade from Order and Position:")

    order_position_params = TradeFromOrderPositionParams(order=sample_order, position=sample_position, symbol="BTCUSDT")

    trade1 = factory.create_trade_from_order_and_position(order_position_params)

    print(f"  Trade ID: {trade1.trade_id}")
    print(f"  Symbol: {trade1.symbol}")
    print(f"  Entry Side: {trade1.entry_side.value}")
    print(f"  Entry Price: ${trade1.entry_price}")
    print(f"  Quantity: {trade1.entry_quantity}")
    print(f"  Position Side: {trade1.position_side.value}")
    print(f"  Status: {trade1.status.value}")

    # 3. Create trade using TradeParams directly
    print("\n⚙️ Creating Trade with Direct Parameters:")

    direct_params = TradeParams(
        symbol="ETHUSDT",
        entry_order_type=OrderType.LIMIT,
        entry_side=OrderSide.SELL,
        entry_quantity=Decimal("0.5"),
        entry_price=Decimal("3000"),
        entry_order_id="order_456",
        position_side=PositionSide.SHORT,
        leverage=2,
        position_id="position_456",
    )

    trade2 = factory.create_trade(direct_params)

    print(f"  Trade ID: {trade2.trade_id}")
    print(f"  Symbol: {trade2.symbol}")
    print(f"  Entry Side: {trade2.entry_side.value}")
    print(f"  Entry Price: ${trade2.entry_price}")
    print(f"  Quantity: {trade2.entry_quantity}")
    print(f"  Position Side: {trade2.position_side.value}")
    print(f"  Leverage: {trade2.leverage}x")
    print(f"  Status: {trade2.status.value}")

    print("\n✅ Benefits of Parameter Classes in TradeFactory:")
    print("  - 🔗 TradeFromOrderPositionParams: Clean way to create trades from existing objects")
    print("  - ⚙️ TradeParams: Direct control over all trade parameters")
    print("  - 🎯 Consistent API across all factory methods")
    print("  - 🔒 Type safety with dataclass validation")
    print("  - 📖 Self-documenting parameter structures")
    print("  - 🧪 Easy to test with parameter objects")

    print("\n🎉 TradeFactory parameter classes example completed!")


if __name__ == "__main__":
    main()
