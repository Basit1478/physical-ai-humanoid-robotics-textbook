from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from .models import UserSignupRequest, UserSignupResponse, UserLoginRequest, UserLoginResponse, UserProfileResponse
import uuid
import json
import os
from datetime import datetime
import hashlib
import secrets

router = APIRouter()

# In-memory storage for users (in production, use a proper database)
users_db = {}
user_profiles_db = {}

def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{hashed}:{salt}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    stored_hash, salt = hashed_password.split(":")
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash == stored_hash

def generate_token() -> str:
    """Generate a random token"""
    return secrets.token_urlsafe(32)

@router.post("/signup", response_model=UserSignupResponse)
async def signup(user_data: UserSignupRequest):
    # Check if user already exists
    if user_data.email in users_db:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)

    users_db[user_data.email] = {
        "user_id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "full_name": user_data.full_name,
        "created_at": datetime.utcnow()
    }

    # Store user profile with background information
    user_profiles_db[user_id] = {
        "user_id": user_id,
        "software_background": user_data.software_background,
        "hardware_background": user_data.hardware_background,
        "created_at": datetime.utcnow()
    }

    # Generate token
    token = generate_token()

    # Store token with user (in production, use proper session management)
    users_db[user_data.email]["token"] = token

    return UserSignupResponse(
        user_id=user_id,
        software_background=user_data.software_background,
        hardware_background=user_data.hardware_background,
        token=token
    )

@router.post("/login", response_model=UserLoginResponse)
async def login(login_data: UserLoginRequest):
    # Check if user exists
    if login_data.email not in users_db:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user = users_db[login_data.email]

    # Verify password
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate new token
    token = generate_token()
    user["token"] = token

    return UserLoginResponse(
        user_id=user["user_id"],
        token=token
    )

@router.get("/me", response_model=UserProfileResponse)
async def get_user_profile(request: Request):
    # Extract token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ")[1]

    # Find user by token
    user = None
    for email, user_data in users_db.items():
        if user_data.get("token") == token:
            user = user_data
            break

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get user profile
    profile = user_profiles_db.get(user["user_id"], {})

    return UserProfileResponse(
        user_id=user["user_id"],
        email=user["email"],
        full_name=user["full_name"],
        software_background=profile.get("software_background"),
        hardware_background=profile.get("hardware_background"),
        created_at=user["created_at"]
    )

@router.post("/logout")
async def logout(request: Request):
    # Extract token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ")[1]

    # Find user by token and invalidate token
    for email, user_data in users_db.items():
        if user_data.get("token") == token:
            del user_data["token"]
            break

    return {"message": "Successfully logged out"}