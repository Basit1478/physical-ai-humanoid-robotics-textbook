from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import os
from datetime import datetime, timedelta
import uuid

app = FastAPI(title="Auth Service", version="1.0.0")

# User data storage (in production, use a proper database)
USERS_FILE = "users.json"

class SignupRequest(BaseModel):
    email: str
    password: str
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None

class SignupResponse(BaseModel):
    user_id: str
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None
    token: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    user_id: str
    token: str

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@app.post("/auth/signup", response_model=SignupResponse)
async def signup(request: SignupRequest):
    users = load_users()

    if request.email in users:
        raise HTTPException(status_code=400, detail="User already exists")

    user_id = str(uuid.uuid4())
    token = f"token_{uuid.uuid4()}"

    user_data = {
        "user_id": user_id,
        "email": request.email,
        "password": request.password,  # In production, hash the password
        "software_background": request.software_background,
        "hardware_background": request.hardware_background,
        "created_at": datetime.now().isoformat(),
        "token": token
    }

    users[request.email] = user_data
    save_users(users)

    return SignupResponse(
        user_id=user_id,
        software_background=request.software_background,
        hardware_background=request.hardware_background,
        token=token
    )

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    users = load_users()

    user = users.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return LoginResponse(
        user_id=user["user_id"],
        token=user["token"]
    )

@app.get("/")
async def root():
    return {"message": "Auth Service", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)