from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class TimestampMixin(BaseModel):
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="Full name")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Plain text password for signup")


class UserOut(UserBase, TimestampMixin):
    id: int = Field(..., description="User identifier")

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Optional description")


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase, TimestampMixin):
    id: int = Field(..., description="Category identifier")
    owner_id: int = Field(..., description="Owner user id")

    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    amount: Decimal = Field(..., description="Expense amount")
    currency: str = Field("USD", description="ISO currency code")
    note: Optional[str] = Field(None, description="Optional note")
    spent_at: datetime = Field(default_factory=datetime.utcnow, description="When the expense occurred")


class ExpenseCreate(ExpenseBase):
    category_id: Optional[int] = Field(None, description="Optional category id")


class ExpenseOut(ExpenseBase, TimestampMixin):
    id: int = Field(..., description="Expense identifier")
    owner_id: int = Field(..., description="Owner user id")
    category_id: Optional[int] = Field(None, description="Associated category id")

    class Config:
        from_attributes = True
