import sys
import os
from dotenv import load_dotenv
from sqlalchemy import text

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
load_dotenv(os.path.join(project_root, '.env'))

from database.db import SessionLocal, engine, Base
from database.models import Admin

def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def add_admin():
    if not test_connection():
        return
    
    Base.metadata.create_all(bind=engine)
    
    email = input("Admin email: ").strip()
    if not email:
        print("Email required")
        return
        
    full_name = input("Full name (optional): ").strip() or None
    
    db = SessionLocal()
    try:
        existing = db.query(Admin).filter(Admin.email == email).first()
        if existing:
            print(f"Admin {email} already exists")
            return
            
        admin = Admin(
            email=email,
            full_name=full_name,
            role="admin",
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        
        print(f"Admin {email} created successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_admin()