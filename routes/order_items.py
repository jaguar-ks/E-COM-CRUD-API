from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db import get_session
from models import Order, OrderItem, OrderItemCreate, Product

router = APIRouter(prefix="/order-items", tags=["order-items"])


def recalculate_order_total(order_id: int, session: Session) -> None:
    """Recompute and persist an order total from its current order items."""
    order = session.get(Order, order_id)
    if not order:
        return
    order_items = session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()
    order.total_amount = sum(item.quantity * item.price for item in order_items)
    session.add(order)


@router.post("", response_model=OrderItem, status_code=status.HTTP_201_CREATED)
async def create_order_item(order_item: OrderItemCreate, session: Session = Depends(get_session)):
    """Create an order item, decrease stock, and recalculate order total."""
    try:
        order = session.get(Order, order_item.order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        product = session.get(Product, order_item.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        if product.stock_quantity < order_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insufficient stock. Available: {product.stock_quantity}, Requested: {order_item.quantity}",
            )

        product.stock_quantity -= order_item.quantity
        session.add(product)

        db_order_item = OrderItem.model_validate(order_item)
        session.add(db_order_item)
        session.flush()

        recalculate_order_total(order.id, session)

        session.commit()
        session.refresh(db_order_item)
    except HTTPException:
        raise
    except ValidationError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid order ID or product ID")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return db_order_item


@router.get("", response_model=list[OrderItem], status_code=status.HTTP_200_OK)
async def get_order_items(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    """Return a paginated list of order items."""
    try:
        if skip < 0 or limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="skip must be >= 0 and limit must be > 0",
            )
        return session.exec(select(OrderItem).offset(skip).limit(limit)).all()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{order_item_id}", response_model=OrderItem, status_code=status.HTTP_200_OK)
async def get_order_item(order_item_id: int, session: Session = Depends(get_session)):
    """Return one order item by ID."""
    try:
        order_item = session.get(OrderItem, order_item_id)
        if not order_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
        return order_item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{order_item_id}", response_model=OrderItem, status_code=status.HTTP_200_OK)
async def update_order_item(
    order_item_id: int,
    order_item_data: OrderItemCreate,
    session: Session = Depends(get_session),
):
    """Update an order item while reconciling stock and affected order totals."""
    db_order_item = session.get(OrderItem, order_item_id)
    if not db_order_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")

    try:
        old_order_id = db_order_item.order_id

        new_order = session.get(Order, order_item_data.order_id)
        if not new_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        old_product = session.get(Product, db_order_item.product_id)
        if not old_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Existing product not found")

        old_product.stock_quantity += db_order_item.quantity
        session.add(old_product)

        new_product = session.get(Product, order_item_data.product_id)
        if not new_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        if new_product.stock_quantity < order_item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insufficient stock. Available: {new_product.stock_quantity}, Requested: {order_item_data.quantity}",
            )

        new_product.stock_quantity -= order_item_data.quantity
        session.add(new_product)

        db_order_item.order_id = order_item_data.order_id
        db_order_item.product_id = order_item_data.product_id
        db_order_item.quantity = order_item_data.quantity
        db_order_item.price = order_item_data.price
        session.add(db_order_item)

        recalculate_order_total(old_order_id, session)
        if old_order_id != order_item_data.order_id:
            recalculate_order_total(order_item_data.order_id, session)

        session.commit()
        session.refresh(db_order_item)
        return db_order_item
    except HTTPException:
        session.rollback()
        raise
    except ValidationError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order item update conflict")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{order_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(order_item_id: int, session: Session = Depends(get_session)):
    """Delete an order item, restore stock, and recalculate order total."""
    db_order_item = session.get(OrderItem, order_item_id)
    if not db_order_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")

    try:
        product = session.get(Product, db_order_item.product_id)
        if product:
            product.stock_quantity += db_order_item.quantity
            session.add(product)

        order_id = db_order_item.order_id
        session.delete(db_order_item)
        session.flush()
        recalculate_order_total(order_id, session)

        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order item delete conflict")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
