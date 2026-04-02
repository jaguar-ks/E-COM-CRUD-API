from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .order import Order


class CustomerBase(SQLModel):
    """Shared customer attributes used by create and table models."""

    first_name: str
    last_name: str
    email: EmailStr = Field(unique=True, description="Unique customer email address.")
    phone: str | None = Field(default=None, description="Optional customer phone number.")


class CustomerCreate(CustomerBase):
    """Request body for creating or updating a customer."""

    pass


class Customer(CustomerBase, table=True):
    """Persistent customer table model."""

    id: int | None = Field(default=None, primary_key=True, description="Customer identifier.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the customer was created.",
    )
    orders: List["Order"] = Relationship(back_populates="customer")