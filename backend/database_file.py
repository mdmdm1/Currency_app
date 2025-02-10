from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Correct DATABASE_URL format for Oracle with service name
DATABASE_URL = "oracle+cx_oracle://admin:2024@localhost:1521/?service_name=MANAGEMENT4"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for SQLAlchemy models
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
