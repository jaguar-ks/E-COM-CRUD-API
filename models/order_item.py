from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .order import Order
    from .product import Product


class OrderItemBase(SQLModel):
    """Shared order-item attributes used by create and table models."""

    order_id: int = Field(foreign_key="orders.id", description="Parent order identifier.")
    product_id: int = Field(foreign_key="product.id", unique=True, description="Referenced product identifier.")
    quantity: int = Field(ge=1, description="Quantity of product ordered.")
    price: int = Field(description="Unit price captured at order time.")


class OrderItemCreate(OrderItemBase):
    """Request body for creating or updating an order item."""

    pass


class OrderItem(OrderItemBase, table=True):
    """Persistent order-item table model."""

    id: int | None = Field(default=None, primary_key=True, description="Order item identifier.")
    order: "Order" = Relationship(back_populates="order_items")
    product: "Product" = Relationship(back_populates="order_items")