from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import random
import string
import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from database.supabase_client import supabase_select, supabase_insert, supabase_update
from utils.email_sender import send_otp_email

router = APIRouter()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "unsafe_secret_key")
ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@router.post("/auth/login")
def login(request: LoginRequest):
    # 1. Check if admin exists
    admins = supabase_select("admins", filters={"email": f"eq.{request.email}"})
    
    if not admins:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    admin_id = admins[0]['id']

    # 2. Generate OTP
    otp = generate_otp()

    # 3. Send Email
    if not send_otp_email(request.email, otp):
        raise HTTPException(status_code=500, detail="Failed to send email")

    # 4. Save to DB
    data = {
        "admin_id": admin_id,
        "email": request.email,
        "otp_code": otp
    }
    
    result = supabase_insert("otp_codes", data)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Database error")

    return {"message": "OTP sent successfully"}

@router.post("/auth/verify")
def verify(request: VerifyOTPRequest):
    # 1. Get latest OTP
    # Note: supabase_select defaults to ordering by created_at desc
    records = supabase_select("otp_codes", filters={"email": f"eq.{request.email}"}, limit=1)
    
    if not records:
        raise HTTPException(status_code=400, detail="No OTP found")
    
    record = records[0]

    # 2. Check Code
    if record['otp_code'] != request.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    # 3. Check Expiry (5 minutes)
    # Supabase returns ISO format like "2023-11-26T10:00:00+00:00"
    # We replace Z with +00:00 to ensure compatibility with fromisoformat if strictly ISO 8601
    created_at_str = record['created_at'].replace('Z', '+00:00')
    otp_time = datetime.fromisoformat(created_at_str)
    
    if datetime.now(timezone.utc) - otp_time > timedelta(minutes=5):
        raise HTTPException(status_code=401, detail="OTP expired")

    # 4. Get Admin Details
    admins = supabase_select("admins", filters={"id": f"eq.{record['admin_id']}"})
    if not admins:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    admin = admins[0]

    # 5. Update Last Login
    supabase_update("admins", admin['id'], {"last_login": datetime.now(timezone.utc).isoformat()})

    # 6. Generate JWT
    expiration = datetime.now(timezone.utc) + timedelta(hours=24)
    token_data = {
        "sub": admin['id'],
        "email": admin['email'],
        "role": admin.get('role', 'admin'),
        "exp": expiration
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": admin['email'],
            "role": admin.get('role')
        }
    }