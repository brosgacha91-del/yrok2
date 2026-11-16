import pytest
from pydantic import ValidationError

from src.order_processor import Order, calculate_total, process_order


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        ({"order_id": " "}, "order_id"),
        ({"customer": ""}, "customer"),
        ({"item": " "}, "item"),
        ({"quantity": 0}, "quantity"),
        ({"quantity": True}, "quantity"),
        ({"unit_price": 0}, "unit_price"),
        ({"unit_price": float("inf")}, "unit_price"),
        ({"email": "not-an-email"}, "email"),
        ({"status": "returned"}, "status"),
        ({"unknown": "value"}, "unknown"),
    ],
)
def test_order_rejects_invalid_data(overrides: dict[str, object], field: str) -> None:
    data: dict[str, object] = {
        "order_id": "A-101",
        "customer": "Alice",
        "item": "Widget",
        "quantity": 2,
        "unit_price": 25.5,
        "email": "alice@example.com",
    }
    data.update(overrides)

    with pytest.raises(ValidationError) as error:
        Order.model_validate(data)

    assert field in {error["loc"][0] for error in error.value.errors()}


def test_calculate_total() -> None:
    order = Order(
        order_id="A-101",
        customer="Alice",
        item="Widget",
        quantity=2,
        unit_price=25.5,
        email="alice@example.com",
    )

    assert calculate_total(order) == 51.0


@pytest.mark.parametrize("status", ["pending", "processing", "shipped", "delivered", "cancelled"])
def test_order_accepts_allowed_statuses(status: str) -> None:
    order = Order(
        order_id="A-101",
        customer="Alice",
        item="Widget",
        quantity=2,
        unit_price=25.5,
        email="alice@example.com",
        status=status,
    )

    assert order.status == status


def test_process_order_dumps_validated_model() -> None:
    order = Order(
        order_id="A-101",
        customer="Alice",
        item="Widget",
        quantity=2,
        unit_price=25.5,
        email="alice@example.com",
    )

    assert process_order(order) == {
        "order_id": "A-101",
        "customer": "Alice",
        "item": "Widget",
        "quantity": 2,
        "unit_price": 25.5,
        "email": "alice@example.com",
        "status": "pending",
        "total": 51.0,
    }
    assert Order.model_validate(process_order(order)) == order


def test_order_rejects_mismatched_serialized_total() -> None:
    data: dict[str, object] = {
        "order_id": "A-101",
        "customer": "Alice",
        "item": "Widget",
        "quantity": 2,
        "unit_price": 25.5,
        "email": "alice@example.com",
        "total": 1.0,
    }

    with pytest.raises(ValidationError, match="total must equal"):
        Order.model_validate(data)
