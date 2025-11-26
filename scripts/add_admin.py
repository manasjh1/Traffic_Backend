import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import SessionLocal
from database.models import Admin

def add_admin():
    email = input("Enter admin email: ").strip()
    if not email:
        print("Email required!")
        return
        
    full_name = input("Enter full name (optional): ").strip() or None
    
    db = SessionLocal()
    try:
        # Check if exists
        existing = db.query(Admin).filter(Admin.email == email).first()
        if existing:
            print(f"Admin {email} already exists!")
            return
            
        # Create admin
        admin = Admin(
            email=email,
            full_name=full_name,
            role="admin",
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        print(f"Admin {email} created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_admin()