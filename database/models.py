from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, BigInteger, func
from .db import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Admin(Base):
    __tablename__ = "admins"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    role = Column(String, default="admin")
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OTPCode(Base):
    __tablename__ = "otp_codes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    admin_id = Column(String, ForeignKey("admins.id"), nullable=False)
    email = Column(String, nullable=False)
    otp_code = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))