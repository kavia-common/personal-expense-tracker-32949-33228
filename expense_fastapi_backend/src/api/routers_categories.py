from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.core.database import get_db
from src.models.models import Category, User
from src.schemas.schemas import CategoryCreate, CategoryOut

router = APIRouter(prefix="/categories", tags=["Categories"])


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[CategoryOut],
    summary="List Categories",
    description="List categories owned by the current user. Optionally filter by name substring.",
)
def list_categories(
    q: Optional[str] = Query(None, description="Optional name substring filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all categories for the current user, optionally filtered by a substring."""
    query = db.query(Category).filter(Category.owner_id == current_user.id)
    if q:
        query = query.filter(Category.name.ilike(f"%{q}%"))
    return query.order_by(Category.name.asc()).all()


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create Category",
    description="Create a new category for the current user.",
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a category owned by the current user."""
    cat = Category(name=payload.name, description=payload.description, owner_id=current_user.id)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# PUBLIC_INTERFACE
@router.get(
    "/{category_id}",
    response_model=CategoryOut,
    summary="Get Category",
    description="Get a single category by id owned by the current user.",
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a category ensuring ownership."""
    cat = db.query(Category).filter(Category.id == category_id, Category.owner_id == current_user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


# PUBLIC_INTERFACE
@router.put(
    "/{category_id}",
    response_model=CategoryOut,
    summary="Update Category",
    description="Update name/description of an owned category.",
)
def update_category(
    category_id: int,
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a category fields if owned by the user."""
    cat = db.query(Category).filter(Category.id == category_id, Category.owner_id == current_user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.name = payload.name
    cat.description = payload.description
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# PUBLIC_INTERFACE
@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Category",
    description="Delete a category owned by the current user.",
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an owned category."""
    cat = db.query(Category).filter(Category.id == category_id, Category.owner_id == current_user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return None
