from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .product import Product


class CategoryBase(SQLModel):
    """Shared category attributes used by create and table models."""

    name: str = Field(unique=True, description="Unique category name.")
    description: str | None = Field(default=None, description="Optional category description.")


class CategoryCreate(CategoryBase):
    """Request body for creating or updating a category."""

    pass


class Category(CategoryBase, table=True):
    """Persistent category table model."""

    id: int | None = Field(default=None, primary_key=True, description="Category identifier.")
    products: List["Product"] = Relationship(back_populates="category")