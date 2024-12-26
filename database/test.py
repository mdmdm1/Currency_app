from sqlalchemy.orm import Session

from database.crud import create_deposit
from database.database import Base, engine, SessionLocal


# Initialize the database
# Base.metadata.create_all(bind=engine)


# Example usage
def main():
    db: Session = SessionLocal()
    try:
        create_deposit(db, "John Doe", 500.0, "2024-12-23")
    finally:
        db.close()


if __name__ == "__main__":
    main()
