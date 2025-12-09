from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
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

class UserSignupRequest(BaseModel):
    username: str
    email: str
    password: str
    software_background: str
    hardware_background: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    software_background: str
    hardware_background: str
    token: str

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
    
    # Check if user already exists
    if request.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password
    hashed_password = hash_password(request.password)
    
    # Create user
    user_id = f"user_{len(users) + 1:04d}"
    users[request.username] = {
        "user_id": user_id,
        "email": request.email,
        "password": hashed_password,
        "software_background": request.software_background,
        "hardware_background": request.hardware_background,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Save users
    save_users(users)
    
    # Create JWT token
    token = create_jwt_token(user_id)
    
    return UserResponse(
        user_id=user_id,
        software_background=request.software_background,
        hardware_background=request.hardware_background,
        token=token
    )

@auth_router.post("/login")
async def login(request: UserLoginRequest):
    users = load_users()
    
    # Check if user exists
    if request.username not in users:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    user = users[request.username]
    hashed_password = hash_password(request.password)
    
    # Check password
    if user["password"] != hashed_password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Create JWT token
    token = create_jwt_token(user["user_id"])
    
    return {
        "user_id": user["user_id"],
        "token": token,
        "software_background": user["software_background"],
        "hardware_background": user["hardware_background"]
    }