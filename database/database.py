from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL (replace with your Oracle connection details)
# DATABASE_URL = "oracle+cx_oracle://admin:2024@localhost:1521/?service_name=MANAGEMENT4"
DATABASE_URL = "oracle+cx_oracle://admin:2024@localhost:1521/?service_name=MANAGEMENT4&encoding=utf8&nencoding=utf8"
engine = create_engine(DATABASE_URL)
# SQLAlchemy engine, session, and base
# engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
