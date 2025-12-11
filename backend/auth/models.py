from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserSignupRequest(BaseModel):
    email: str
    password: str
    full_name: str
    software_background: str
    hardware_background: str

class UserSignupResponse(BaseModel):
    user_id: str
    software_background: str
    hardware_background: str
    token: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserLoginResponse(BaseModel):
    user_id: str
    token: str

class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None
    created_at: datetime