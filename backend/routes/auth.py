from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from models.database import SessionLocal
from models.schemas import UserCreate, User, Token
from auth.better_auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    get_db
)
from models.database import User as UserModel

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/auth/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db_session)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(UserModel).filter(
        (UserModel.username == user.username) | (UserModel.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    """Login endpoint that returns a JWT token"""
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/profile", response_model=User)
def get_profile(current_user: UserModel = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("/auth/profile", response_model=User)
def update_profile(
    user_update: dict,  # Using a dict for flexibility
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Update user profile"""
    for field, value in user_update.items():
        if hasattr(current_user, field) and field in ["name", "email"]:  # Only allow specific fields to be updated
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user