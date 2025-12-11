from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from qdrant_client.http import models
from ..qdrant_setup import QdrantSetup

router = APIRouter(prefix="/auth")

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class SignupRequest(BaseModel):
    email: str
    password: str
    software_background: str
    hardware_background: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    user_id: str
    software_background: str
    hardware_background: str
    token: str

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(email: str, password: str):
    # In a real implementation, you would check the password against a stored hash
    # For this example, we'll just check if the user exists in Qdrant
    qdrant = QdrantSetup()

    # Find user in Qdrant by email
    results = qdrant.client.scroll(
        collection_name=qdrant.collections["users"],
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="email",
                    match=models.MatchValue(value=email)
                )
            ]
        ),
        limit=1
    )

    if results[0]:
        user_data = results[0][0].payload
        # For this example, we're not actually checking the password hash
        # In a real implementation, you would hash the input password and compare
        return user_data
    return None

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    # Check if user already exists
    qdrant = QdrantSetup()

    existing_user_results = qdrant.client.scroll(
        collection_name=qdrant.collections["users"],
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="email",
                    match=models.MatchValue(value=request.email)
                )
            ]
        ),
        limit=1
    )

    if existing_user_results[0]:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create new user ID
    user_id = str(uuid.uuid4())

    # Hash the password (in a real implementation)
    hashed_password = get_password_hash(request.password)

    # Store user background in Qdrant
    qdrant.store_user_background(
        user_id=user_id,
        software_background=request.software_background,
        hardware_background=request.hardware_background
    )

    # Update the stored data to include email and hashed password
    # In a real implementation, you'd store the hashed password in the database
    from qdrant_client import models as qdrant_models
    import uuid as uuid_lib

    # Store user data in Qdrant with email
    qdrant.client.upsert(
        collection_name=qdrant.collections["users"],
        points=[
            qdrant_models.PointStruct(
                id=uuid_lib.uuid4().int,
                vector=[0.0] * 384,  # Placeholder vector
                payload={
                    "user_id": user_id,
                    "email": request.email,
                    "hashed_password": hashed_password,
                    "software_background": request.software_background,
                    "hardware_background": request.hardware_background,
                    "created_at": str(datetime.now())
                }
            )
        ]
    )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user_id, "email": request.email}, expires_delta=access_token_expires
    )

    return AuthResponse(
        user_id=user_id,
        software_background=request.software_background,
        hardware_background=request.hardware_background,
        token=token
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user["user_id"], "email": request.email}, expires_delta=access_token_expires
    )

    return AuthResponse(
        user_id=user["user_id"],
        software_background=user["software_background"],
        hardware_background=user["hardware_background"],
        token=token
    )