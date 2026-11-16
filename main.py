from src.order_processor import Order, process_order

if __name__ == "__main__":
    sample_order = Order(
        order_id="ORD-1001",
        customer="Alice",
        item="Keyboard",
        quantity=2,
        unit_price=59.99,
        email="alice@example.com",
    )
    result = process_order(sample_order)
    print(result)