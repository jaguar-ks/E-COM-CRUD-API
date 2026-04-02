from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db import get_session
from models import Category, CategoryCreate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    """Create a new category record."""
    try:
        db_category = Category.model_validate(category)
        session.add(db_category)
        session.commit()
        session.refresh(db_category)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return db_category


@router.get("", response_model=list[Category], status_code=status.HTTP_200_OK)
async def get_categories(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    """Return a paginated list of categories."""
    try:
        if skip < 0 or limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="skip must be >= 0 and limit must be > 0",
            )
        return session.exec(select(Category).offset(skip).limit(limit)).all()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{category_id}", response_model=Category, status_code=status.HTTP_200_OK)
async def get_category(category_id: int, session: Session = Depends(get_session)):
    """Return one category by its ID."""
    try:
        category = session.get(Category, category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{category_id}", response_model=Category, status_code=status.HTTP_200_OK)
async def update_category(
    category_id: int,
    category_data: CategoryCreate,
    session: Session = Depends(get_session),
):
    """Update an existing category by ID."""
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    try:
        update_data = category_data.model_dump()
        for key, value in update_data.items():
            setattr(db_category, key, value)

        session.add(db_category)
        session.commit()
        session.refresh(db_category)
        return db_category
    except ValidationError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category update conflict")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, session: Session = Depends(get_session)):
    """Delete a category by ID."""
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    try:
        session.delete(db_category)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category cannot be deleted due to related records",
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
