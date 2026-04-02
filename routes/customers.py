from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db import get_session
from models import Customer, CustomerCreate

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerCreate, session: Session = Depends(get_session)):
    """Create a new customer record."""
    try:
        db_customer = Customer.model_validate(customer)
        session.add(db_customer)
        session.commit()
        session.refresh(db_customer)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Customer email already exists")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return db_customer


@router.get("", response_model=list[Customer], status_code=status.HTTP_200_OK)
async def get_customers(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    """Return a paginated list of customers."""
    try:
        if skip < 0 or limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="skip must be >= 0 and limit must be > 0",
            )
        return session.exec(select(Customer).offset(skip).limit(limit)).all()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{customer_id}", response_model=Customer, status_code=status.HTTP_200_OK)
async def get_customer(customer_id: int, session: Session = Depends(get_session)):
    """Return one customer by ID."""
    try:
        customer = session.get(Customer, customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return customer
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{customer_id}", response_model=Customer, status_code=status.HTTP_200_OK)
async def update_customer(
    customer_id: int,
    customer_data: CustomerCreate,
    session: Session = Depends(get_session),
):
    """Update an existing customer by ID."""
    db_customer = session.get(Customer, customer_id)
    if not db_customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    try:
        update_data = customer_data.model_dump()
        for key, value in update_data.items():
            setattr(db_customer, key, value)

        session.add(db_customer)
        session.commit()
        session.refresh(db_customer)
        return db_customer
    except ValidationError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Customer update conflict")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: int, session: Session = Depends(get_session)):
    """Delete a customer by ID."""
    db_customer = session.get(Customer, customer_id)
    if not db_customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    try:
        session.delete(db_customer)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer cannot be deleted due to related records",
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
