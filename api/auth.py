from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
import os
from database.db import get_db
from database.models import Admin

router = APIRouter()

# 1. SECURITY CONFIGURATION
# We use Argon2 because it is newer and doesn't crash like bcrypt
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Secret key for signing JWT tokens (keep this safe!)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# 2. DATA MODELS
class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str | None = None
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# 3. REGISTER API (Creates the user)
@router.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    if db.query(Admin).filter(Admin.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password using Argon2
    hashed_password = pwd_context.hash(req.password)
    
    new_admin = Admin(
        email=req.email,
        full_name=req.full_name,
        password_hash=hashed_password,
        role="admin"
    )
    
    db.add(new_admin)
    db.commit()
    return {"message": "Admin registered successfully. You can now login."}

# In Traffic_Backend/api/auth.py

@router.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    print(f"\n--- LOGIN ATTEMPT ---")
    print(f"1. Received email: '{req.email}'")
    print(f"2. Received password: '{req.password}'")

    # Find the user
    admin = db.query(Admin).filter(Admin.email == req.email).first()
    
    if not admin:
        print("3. RESULT: User NOT found in database.")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    print(f"3. User found: {admin.email}")
    print(f"4. Stored Hash in DB: {admin.password_hash[:15]}...") # Print first 15 chars
    
    # Verify password
    is_valid = pwd_context.verify(req.password, admin.password_hash)
    print(f"5. Password Verification Result: {is_valid}")

    if not is_valid:
        print("6. RESULT: Password verification FAILED.")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    print("6. RESULT: Success!")
    
    # Create JWT Token payload
    token_data = {
        "sub": admin.id,
        "email": admin.email,
        "role": admin.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": admin.email,
            "full_name": admin.full_name
        }
    }