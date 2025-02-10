from datetime import datetime, timezone
from database_file import Base
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship


class AuditLog(Base):
    __tablename__ = "AUDIT_LOGS"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False)  # e.g., 'CURRENCIES', 'DEBTS'
    operation = Column(String(50), nullable=False)  # 'INSERT', 'UPDATE', 'DELETE'
    record_id = Column(Integer, nullable=False)  # ID of the affected record
    user_id = Column(
        Integer, ForeignKey("USERS.id"), nullable=True
    )  # Who performed the action
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    changes = Column(
        Text, nullable=True
    )  # Optional: Store details of changes (e.g., JSON)

    # Relationship to the User table
    user = relationship("User", back_populates="audit_logs")
