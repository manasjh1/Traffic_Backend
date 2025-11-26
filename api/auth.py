from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import random
import string
import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from database.db import get_db
from database.models import Admin, OTPCode
from utils.email_sender import send_otp_email

router = APIRouter()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Security
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Check if admin exists and is active
    admin = db.query(Admin).filter(
        Admin.email == request.email,
        Admin.is_active == True
    ).first()
    
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Generate OTP
    otp = generate_otp()
    
    # Save OTP with 5 minute expiry
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    otp_record = OTPCode(
        admin_id=admin.id,
        email=request.email,
        otp_code=otp,
        expires_at=expires_at
    )
    
    db.add(otp_record)
    db.commit()
    
    # Send OTP email
    if not send_otp_email(request.email, otp):
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to send email")
    
    return {"message": "OTP sent successfully"}

@router.post("/auth/verify")
def verify(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    # Get latest OTP
    otp_record = db.query(OTPCode).filter(
        OTPCode.email == request.email
    ).order_by(OTPCode.created_at.desc()).first()
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="No OTP found")
    
    # Check OTP code
    if otp_record.otp_code != request.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")
    
    # Check expiry
    if datetime.now(timezone.utc) > otp_record.expires_at:
        raise HTTPException(status_code=401, detail="OTP expired")
    
    # Get admin
    admin = db.query(Admin).filter(Admin.id == otp_record.admin_id).first()
    
    # Update last login
    admin.last_login = datetime.now(timezone.utc)
    db.commit()
    
    # Delete used OTP
    db.delete(otp_record)
    db.commit()
    
    # Create JWT token
    token_data = {
        "sub": admin.id,
        "email": admin.email,
        "role": admin.role
    }
    
    token = create_access_token(token_data)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": admin.email,
            "role": admin.role,
            "full_name": admin.full_name
        }
    }

@router.get("/auth/me")
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id = payload.get("sub")
        
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        return {
            "id": admin.id,
            "email": admin.email,
            "full_name": admin.full_name,
            "role": admin.role
        }
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")