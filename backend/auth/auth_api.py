from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import jwt
import json
import os
from datetime import datetime, timedelta
import hashlib

auth_router = APIRouter()

# Secret for JWT encoding/decoding
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# File to store user data
USERS_FILE = "users.json"

class UserBackground(BaseModel):
    software_experience: str
    programming_languages: List[str]
    robotics_experience: str
    hardware_experience: str
    ai_ml_knowledge: str
    goals: str

class UserSignupRequest(BaseModel):
    email: str
    password: str
    full_name: str
    background: UserBackground

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    token: str
    profile: dict

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def create_jwt_token(user_id: str) -> str:
    """Create JWT token for user"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@auth_router.post("/signup", response_model=UserResponse)
async def signup(request: UserSignupRequest):
    users = load_users()

    # Check if user already exists by email
    for user_data in users.values():
        if user_data["email"] == request.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    # Hash password
    hashed_password = hash_password(request.password)

    # Create user
    user_id = f"user_{len(users) + 1:04d}"
    users[user_id] = {
        "user_id": user_id,
        "email": request.email,
        "full_name": request.full_name,
        "password": hashed_password,
        "background": request.background.dict(),
        "created_at": datetime.utcnow().isoformat()
    }

    # Save users
    save_users(users)

    # Create JWT token
    token = create_jwt_token(user_id)

    return UserResponse(
        user_id=user_id,
        token=token,
        profile={
            "email": request.email,
            "full_name": request.full_name,
            "background": request.background.dict()
        }
    )

@auth_router.post("/login")
async def login(request: UserLoginRequest):
    users = load_users()

    # Find user by email
    user = None
    user_id = None
    for uid, user_data in users.items():
        if user_data["email"] == request.email:
            user = user_data
            user_id = uid
            break

    if user is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    hashed_password = hash_password(request.password)

    # Check password
    if user["password"] != hashed_password:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create JWT token
    token = create_jwt_token(user["user_id"])

    return {
        "user_id": user["user_id"],
        "token": token,
        "profile": {
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "background": user.get("background", {})
        }
    }