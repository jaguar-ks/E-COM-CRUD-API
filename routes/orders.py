from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db import get_session
from models import Order, OrderCreate, OrderItem

router = APIRouter(prefix="/orders", tags=["orders"])


def recalculate_order_total(order_id: int, session: Session) -> None:
    """Recompute and persist an order total from its order items."""
    order = session.get(Order, order_id)
    if not order:
        return
    order_items = session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()
    order.total_amount = sum(item.quantity * item.price for item in order_items)
    session.add(order)


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, session: Session = Depends(get_session)):
    """Create a new order record."""
    try:
        db_order = Order.model_validate(order)
        session.add(db_order)
        session.commit()
        session.refresh(db_order)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invalid customer ID or order constraint violation",
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return db_order


@router.get("", response_model=list[Order], status_code=status.HTTP_200_OK)
async def get_orders(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    """Return a paginated list of orders."""
    try:
        if skip < 0 or limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="skip must be >= 0 and limit must be > 0",
            )
        return session.exec(select(Order).offset(skip).limit(limit)).all()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{order_id}", response_model=Order, status_code=status.HTTP_200_OK)
async def get_order(order_id: int, session: Session = Depends(get_session)):
    """Return one order by ID."""
    try:
        order = session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{order_id}", response_model=Order, status_code=status.HTTP_200_OK)
async def update_order(
    order_id: int,
    order_data: OrderCreate,
    session: Session = Depends(get_session),
):
    """Update order metadata and keep total amount computed from items."""
    db_order = session.get(Order, order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    try:
        db_order.customer_id = order_data.customer_id
        db_order.order_date = order_data.order_date
        db_order.status = order_data.status
        recalculate_order_total(order_id, session)

        session.add(db_order)
        session.commit()
        session.refresh(db_order)
        return db_order
    except ValidationError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order update conflict")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, session: Session = Depends(get_session)):
    """Delete an order by ID."""
    db_order = session.get(Order, order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    try:
        session.delete(db_order)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order cannot be deleted due to related records",
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
