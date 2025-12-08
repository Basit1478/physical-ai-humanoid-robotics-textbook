from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from models.database import SessionLocal
from models.schemas import UserCreate, User, Token, UserUpdate, Profile
from auth.better_auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    get_db
)
from models.database import User as UserModel, UserProfile

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
    """Register a new user with profile creation"""
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

    # Create default user profile
    user_profile = UserProfile(
        user_id=db_user.id,
        name=user.username,
        education_level="intermediate",
        field_of_study="general",
        background="general"
    )

    db.add(user_profile)
    db.commit()
    db.refresh(user_profile)

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
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Update user profile with comprehensive profile information"""
    # Update user information if provided
    if user_update.name:
        # Update or create user profile with name
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)

        profile.name = user_update.name

    # Update education level if provided
    if user_update.education_level:
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)

        profile.education_level = user_update.education_level

    # Update field of study if provided
    if user_update.field_of_study:
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)

        profile.field_of_study = user_update.field_of_study

    # Update background if provided
    if user_update.background:
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)

        profile.background = user_update.background

    db.commit()
    db.refresh(current_user)

    return current_user

@router.get("/auth/profile/details", response_model=Profile)
def get_detailed_profile(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db_session)):
    """Get detailed user profile information"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    if not profile:
        # Create a default profile if none exists
        profile = UserProfile(
            user_id=current_user.id,
            name=current_user.username,
            education_level="intermediate",
            field_of_study="general",
            background="general"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return profile

@router.put("/auth/profile/details", response_model=Profile)
def update_detailed_profile(
    profile_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Update detailed user profile information"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    if not profile:
        # Create profile if it doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Update profile fields
    if profile_update.name is not None:
        profile.name = profile_update.name

    if profile_update.education_level is not None:
        profile.education_level = profile_update.education_level

    if profile_update.field_of_study is not None:
        profile.field_of_study = profile_update.field_of_study

    if profile_update.background is not None:
        profile.background = profile_update.background

    db.commit()
    db.refresh(profile)

    return profile