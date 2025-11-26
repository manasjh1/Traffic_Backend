from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Authentication Schemas
class LoginRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginResponse(BaseModel):
    message: str
    status: str = "success"

class UserInfo(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str = "admin"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserInfo

# Admin Schemas
class AdminCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "admin"

class AdminResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

# Error Schemas
class ErrorResponse(BaseModel):
    detail: str
    type: str = "error"
    code: Optional[str] = None