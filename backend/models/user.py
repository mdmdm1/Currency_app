from datetime import datetime, timezone
from unittest.mock import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "USERS"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Store hashed passwords
    is_active = Column(
        Boolean, default=True, nullable=False
    )  # Active or inactive account
    role = Column(
        String(50), nullable=False
    )  # e.g., 'admin', 'user', 'auditor' SUPERADMIN
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    # Relationship to AuditLog table
    audit_logs = relationship("AuditLog", back_populates="user")
