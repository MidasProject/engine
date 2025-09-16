"""Example demonstrating the new parameter classes for order creation.

This example shows how to use the parameter classes to create orders
with cleaner, more maintainable code.
"""

from decimal import Decimal

from engine import (
    LimitOrderParams,
    MarketOrderParams,
    OrderFactory,
    StopLimitOrderParams,
    StopMarketOrderParams,
    TakeProfitOrderParams,
)


def demonstrate_market_order(factory: OrderFactory) -> None:
    """Demonstrate market order creation."""
    print("\n📦 Creating Market Order:")
    market_params = MarketOrderParams(
        symbol="BTCUSDT", side="BUY", quantity=Decimal("0.01"), client_order_id="market_001"
    )
    market_order = factory.create_market_order(market_params)
    print(f"  Order ID: {market_order.order_id}")
    print(f"  Type: {market_order.order_type.value}")
    print(f"  Side: {market_order.side.value}")
    print(f"  Quantity: {market_order.quantity}")


def demonstrate_limit_order(factory: OrderFactory) -> None:
    """Demonstrate limit order creation."""
    print("\n📋 Creating Limit Order:")
    limit_params = LimitOrderParams(
        symbol="BTCUSDT", side="SELL", quantity=Decimal("0.01"), price=Decimal("52000"), client_order_id="limit_001"
    )
    limit_order = factory.create_limit_order(limit_params)
    print(f"  Order ID: {limit_order.order_id}")
    print(f"  Type: {limit_order.order_type.value}")
    print(f"  Side: {limit_order.side.value}")
    print(f"  Quantity: {limit_order.quantity}")
    print(f"  Price: ${limit_order.price}")


def demonstrate_stop_orders(factory: OrderFactory) -> None:
    """Demonstrate stop order creation."""
    # Stop Market Order
    print("\n🛑 Creating Stop Market Order:")
    stop_market_params = StopMarketOrderParams(
        symbol="BTCUSDT",
        side="SELL",
        quantity=Decimal("0.01"),
        stop_price=Decimal("48000"),
        client_order_id="stop_market_001",
    )
    stop_market_order = factory.create_stop_market_order(stop_market_params)
    print(f"  Order ID: {stop_market_order.order_id}")
    print(f"  Type: {stop_market_order.order_type.value}")
    print(f"  Side: {stop_market_order.side.value}")
    print(f"  Quantity: {stop_market_order.quantity}")
    print(f"  Stop Price: ${stop_market_order.stop_price}")

    # Stop Limit Order
    print("\n🎯 Creating Stop Limit Order:")
    stop_limit_params = StopLimitOrderParams(
        symbol="BTCUSDT",
        side="SELL",
        quantity=Decimal("0.01"),
        stop_price=Decimal("48000"),
        limit_price=Decimal("47500"),
        client_order_id="stop_limit_001",
    )
    stop_limit_order = factory.create_stop_limit_order(stop_limit_params)
    print(f"  Order ID: {stop_limit_order.order_id}")
    print(f"  Type: {stop_limit_order.order_type.value}")
    print(f"  Side: {stop_limit_order.side.value}")
    print(f"  Quantity: {stop_limit_order.quantity}")
    print(f"  Stop Price: ${stop_limit_order.stop_price}")
    print(f"  Limit Price: ${stop_limit_order.limit_price}")


def demonstrate_take_profit_order(factory: OrderFactory) -> None:
    """Demonstrate take profit order creation."""
    print("\n💰 Creating Take Profit Order:")
    take_profit_params = TakeProfitOrderParams(
        symbol="BTCUSDT",
        side="SELL",
        quantity=Decimal("0.01"),
        target_price=Decimal("55000"),
        client_order_id="take_profit_001",
    )
    take_profit_order = factory.create_take_profit_order(take_profit_params)
    print(f"  Order ID: {take_profit_order.order_id}")
    print(f"  Type: {take_profit_order.order_type.value}")
    print(f"  Side: {take_profit_order.side.value}")
    print(f"  Quantity: {take_profit_order.quantity}")
    print(f"  Target Price: ${take_profit_order.target_price}")


def print_benefits() -> None:
    """Print the benefits of using parameter classes."""
    print("\n✅ Benefits of Parameter Classes:")
    print("  - ✨ Cleaner method signatures (no long argument lists)")
    print("  - 🔒 Type safety with dataclass validation")
    print("  - 📖 Self-documenting code with named parameters")
    print("  - 🔧 Easy to extend with new parameters")
    print("  - 🧪 Easier to test with mock parameter objects")
    print("  - 🎯 Follows SOLID principles (Single Responsibility)")


def main():
    """Demonstrate the new parameter classes."""
    print("🏭 Order Factory Parameter Classes Example")
    print("=" * 50)

    # Create order factory
    factory = OrderFactory()

    # Demonstrate different order types
    demonstrate_market_order(factory)
    demonstrate_limit_order(factory)
    demonstrate_stop_orders(factory)
    demonstrate_take_profit_order(factory)

    print_benefits()
    print("\n🎉 Parameter classes example completed!")


if __name__ == "__main__":
    main()
