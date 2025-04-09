from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from routes import (
    customer,
    deposit,
    debt,
    employee,
    treasury,
    currency,
    audit_log,
    user,
    auth,
)
import bcrypt
from database_file import SessionLocal, engine, Base
from models.user import User
from sqlalchemy import select

app = FastAPI(title="Currency Bank API", version="1.0")

# Include all routers
app.include_router(customer.router)
app.include_router(deposit.router)
app.include_router(debt.router)
app.include_router(employee.router)
app.include_router(treasury.router)
app.include_router(currency.router)
app.include_router(audit_log.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.on_event("startup")
async def startup_event():
    """
    Create tables and setup admin user if they don't exist
    This runs when the application starts
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create admin user if it doesn't exist
    create_admin_user()


def create_admin_user():
    """Create admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_exists = db.execute(
            select(User).where(User.username == "admin")
        ).scalar_one_or_none()

        if not admin_exists:
            # Generate a hash for the default password
            password = "admin123"  # Default password
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            # Create the admin user
            admin_user = User(
                username="admin",
                password=hashed_password.decode("utf-8"),
                is_active=True,
                role="admin",
            )

            db.add(admin_user)
            db.commit()
            print("Admin user created successfully")
        else:
            print("Admin user already exists")
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
    finally:
        db.close()


# Run with: uvicorn main:app --reload
