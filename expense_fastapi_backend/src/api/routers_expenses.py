from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.core.database import get_db
from src.models.models import Expense, User, Category
from src.schemas.schemas import ExpenseCreate, ExpenseOut

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[ExpenseOut],
    summary="List Expenses",
    description="List expenses for the current user with optional filters for date range and category.",
)
def list_expenses(
    start: Optional[datetime] = Query(None, description="Start datetime (inclusive)"),
    end: Optional[datetime] = Query(None, description="End datetime (inclusive)"),
    category_id: Optional[int] = Query(None, description="Filter by category id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return expenses belonging to the current user with optional filters."""
    query = db.query(Expense).filter(Expense.owner_id == current_user.id)
    if start:
        query = query.filter(Expense.spent_at >= start)
    if end:
        query = query.filter(Expense.spent_at <= end)
    if category_id is not None:
        query = query.filter(Expense.category_id == category_id)
    return query.order_by(Expense.spent_at.desc(), Expense.id.desc()).all()


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=ExpenseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create Expense",
    description="Create a new expense for the current user.",
)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an expense record owned by the current user."""
    if payload.category_id is not None:
        # Ensure category belongs to current user
        cat = db.query(Category).filter(
            Category.id == payload.category_id, Category.owner_id == current_user.id
        ).first()
        if not cat:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    exp = Expense(
        amount=payload.amount,
        currency=payload.currency,
        note=payload.note,
        spent_at=payload.spent_at,
        owner_id=current_user.id,
        category_id=payload.category_id,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


# PUBLIC_INTERFACE
@router.get(
    "/{expense_id}",
    response_model=ExpenseOut,
    summary="Get Expense",
    description="Get a single expense by id owned by the current user.",
)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single expense with ownership validation."""
    exp = db.query(Expense).filter(Expense.id == expense_id, Expense.owner_id == current_user.id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    return exp


# PUBLIC_INTERFACE
@router.put(
    "/{expense_id}",
    response_model=ExpenseOut,
    summary="Update Expense",
    description="Update an existing expense owned by the current user.",
)
def update_expense(
    expense_id: int,
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update fields on an existing expense, validating category ownership if provided."""
    exp = db.query(Expense).filter(Expense.id == expense_id, Expense.owner_id == current_user.id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    if payload.category_id is not None:
        cat = db.query(Category).filter(
            Category.id == payload.category_id, Category.owner_id == current_user.id
        ).first()
        if not cat:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    exp.amount = payload.amount
    exp.currency = payload.currency
    exp.note = payload.note
    exp.spent_at = payload.spent_at
    exp.category_id = payload.category_id
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


# PUBLIC_INTERFACE
@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Expense",
    description="Delete an expense owned by the current user.",
)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an owned expense."""
    exp = db.query(Expense).filter(Expense.id == expense_id, Expense.owner_id == current_user.id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(exp)
    db.commit()
    return None
