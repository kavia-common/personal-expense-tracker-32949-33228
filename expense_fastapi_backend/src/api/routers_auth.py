from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import hash_password, verify_password, create_access_token
from src.models.models import User
from src.schemas.schemas import UserCreate, UserOut
from src.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


# PUBLIC_INTERFACE
@router.post(
    "/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="User Signup",
    description="Create a new user account with email and password.",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Email already registered"},
    },
)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user, hashing the password and returning the created user."""
    existing = db.query(User).filter(User.email == str(payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=str(payload.email),
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate user using OAuth2 password flow and return an access token.",
    responses={
        200: {"description": "Authenticated"},
        400: {"description": "Incorrect email or password"},
    },
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 Password flow login.
    Note: OAuth2PasswordRequestForm uses 'username' field; we treat it as email.
    """
    email = form_data.username
    password = form_data.password
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token, token_type="bearer")


# PUBLIC_INTERFACE
@router.get(
    "/me",
    response_model=UserOut,
    summary="Current User",
    description="Return the currently authenticated user's profile.",
)
def me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's information."""
    return current_user
