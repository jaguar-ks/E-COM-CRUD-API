from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .customer import Customer
    from .order_item import OrderItem


class OrderStatus(str, Enum):
    """Allowed status values for an order."""

    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class OrderBase(SQLModel):
    """Shared order attributes used by create and table models."""

    customer_id: int = Field(foreign_key="customer.id", description="Customer ID who placed the order.")
    order_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the order was created.",
    )
    total_amount: int = Field(default=0, description="Computed total amount for all order items.")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Current order status.")


class OrderCreate(OrderBase):
    """Request body for creating or updating an order."""

    pass


class Order(OrderBase, table=True):
    """Persistent order table model."""

    __tablename__ = "orders"

    id: int | None = Field(default=None, primary_key=True, description="Order identifier.")
    customer: "Customer" = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")