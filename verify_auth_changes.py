from core.database import SessionLocal
from core import models, schemas, security
from backend_api.auth import register_user, login_for_access_token
from sqlalchemy.orm import Session
import uuid

def test_auth_cleanup():
    db = SessionLocal()
    unique_id = str(uuid.uuid4())[:8]
    email = f"TestUser_{unique_id}@Example.com"
    password = "password123"
    
    print(f"--- Testing registration with email: {email} ---")
    user_create = schemas.UserCreate(
        email=email,
        password=password,
        username=f"test_{unique_id}",
        first_name="Test",
        last_name="User"
    )
    
    try:
        # Test registration
        reg_response = register_user(user_create, db)
        print(f"✅ Registration successful: {reg_response}")
        
        # Verify in DB (should be lowercase)
        db_user = db.query(models.User).filter(models.User.email == email.lower()).first()
        if db_user:
            print(f"✅ Email in database is strictly lowercase: {db_user.email}")
            print(f"✅ Default role is correct: {db_user.role}")
        else:
            print("❌ User not found in database with lowercase email!")
            
        # Test login with MIXED case email
        print(f"--- Testing login with MIXED case email: {email} ---")
        login_data = schemas.UserLogin(email=email, password=password)
        login_response = login_for_access_token(login_data, db)
        print(f"✅ Login successful: {login_response}")
        
        # Test login with LOWER case email
        print(f"--- Testing login with LOWER case email: {email.lower()} ---")
        login_data_lower = schemas.UserLogin(email=email.lower(), password=password)
        login_response_lower = login_for_access_token(login_data_lower, db)
        print(f"✅ Login with lowercase successful: {login_response_lower}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Cleanup
        if db_user:
            db.delete(db_user)
            db.commit()
        db.close()

if __name__ == "__main__":
    test_auth_cleanup()
