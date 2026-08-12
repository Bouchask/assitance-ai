import os
import sys
from werkzeug.security import generate_password_hash

# Ensure backend module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import engine, SessionLocal
from backend.models.base import Base
from backend.models.client import Client
from backend.models.service import Service
from backend.models.quote import Quote, QuoteItem
from backend.models.user import User
from backend.database.catalogue import seed_catalogue

def init_db():
    print("Creating all tables in the database...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Seed the catalogue
        print("Seeding product catalogue...")
        count = seed_catalogue(db)
        print(f"Catalogue seeded with {count} new services.")
        
        # Create default admin user if it doesn't exist
        print("Checking admin user...")
        admin_email = "admin@atlas.com"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        
        if not admin_user:
            hashed_pw = generate_password_hash("admin123")
            admin_user = User(
                email=admin_email,
                hashed_password=hashed_pw,
                role="ADMIN",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"Created default admin user: {admin_email} / admin123")
        else:
            print(f"Admin user {admin_email} already exists.")
            
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        db.rollback()
    finally:
        db.close()
        print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
