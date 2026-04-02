from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db import get_session
from models import Category, OrderItem, Product, ProductCreate

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    """Create a new product record."""
    try:
        if product.category_id is not None:
            category = session.get(Category, product.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Invalid category ID",
                )

        db_product = Product.model_validate(product)
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product name may already exist or invalid category",
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return db_product


@router.get("", response_model=list[Product], status_code=status.HTTP_200_OK)
async def get_products(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    """Return a paginated list of products."""
    try:
        if skip < 0 or limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="skip must be >= 0 and limit must be > 0",
            )
        return session.exec(select(Product).offset(skip).limit(limit)).all()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, session: Session = Depends(get_session)):
    """Return one product by its ID."""
    try:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int,
    product_data: ProductCreate,
    session: Session = Depends(get_session),
):
    """Update an existing product by ID."""
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    try:
        if product_data.category_id is not None:
            category = session.get(Category, product_data.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Invalid category ID",
                )

        update_data = product_data.model_dump()
        for key, value in update_data.items():
            setattr(db_product, key, value)

        session.add(db_product)
        session.commit()
        session.refresh(db_product)
        return db_product
    except HTTPException:
        session.rollback()
        raise
    except ValidationError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product update conflict")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, session: Session = Depends(get_session)):
    """Delete a product by ID."""
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    try:
        related_items = session.exec(
            select(OrderItem).where(OrderItem.product_id == product_id).limit(1)
        ).first()
        if related_items:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product cannot be deleted due to related records",
            )

        session.delete(db_product)
        session.commit()
    except HTTPException:
        raise
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product cannot be deleted due to related records",
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
