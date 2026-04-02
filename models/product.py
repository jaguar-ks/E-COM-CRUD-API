from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .category import Category
    from .order_item import OrderItem



class ProductBase(SQLModel):
    """Shared product attributes used by create and table models."""

    name: str
    description: str | None = Field(default=None, description="Optional product description.")
    price: int = Field(gt=0, description="Unit price of the product.")
    stock_quantity: int = Field(gt=0, description="Available quantity in stock.")
    category_id: int | None = Field(
        default=None,
        foreign_key="category.id",
        description="Optional category ID this product belongs to.",
    )


class ProductCreate(ProductBase):
    """Request body for creating or updating a product."""

    pass


class Product(ProductBase, table=True):
    """Persistent product table model."""

    id: int | None = Field(default=None, primary_key=True, description="Product identifier.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the product was created.",
    )
    category: "Category" = Relationship(back_populates="products")
    order_items: List["OrderItem"] = Relationship(back_populates="product")

    @field_validator("name")
    @classmethod
    def check_name(cls, value: str):
        """Validate product name length before persisting."""
        if value == "" or len(value) < 3:
            raise ValueError("name not valid")
        return value