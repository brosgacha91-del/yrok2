from __future__ import annotations

from math import isfinite
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field, model_validator


class Order(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )

    order_id: str = Field(min_length=1)
    customer: str = Field(min_length=1)
    item: str = Field(min_length=1)
    quantity: int = Field(gt=0, strict=True)
    unit_price: float = Field(gt=0)
    email: EmailStr
    status: Literal["pending", "processing", "shipped", "delivered", "cancelled"] = "pending"

    @model_validator(mode="before")
    @classmethod
    def validate_serialized_total(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "total" not in data:
            return data
        data = data.copy()
        total = data.pop("total")
        quantity = data.get("quantity")
        unit_price = data.get("unit_price")
        valid_quantity = isinstance(quantity, int) and not isinstance(quantity, bool)
        valid_price = isinstance(unit_price, (int, float)) and not isinstance(unit_price, bool)
        if valid_quantity and valid_price:
            if (
                isinstance(total, bool)
                or not isinstance(total, (int, float))
                or not isfinite(total)
                or total != quantity * unit_price
            ):
                raise ValueError("total must equal quantity * unit_price")
        return data

    @computed_field
    @property
    def total(self) -> float:
        return self.quantity * self.unit_price


def calculate_total(order: Order) -> float:
    return order.total


def process_order(order: Order) -> dict[str, object]:
    return order.model_dump(mode="json")
