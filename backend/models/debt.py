from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Identity,
    Integer,
    Float,
    ForeignKey,
    Date,
)
from sqlalchemy.orm import relationship
from database_file import Base
import sqlalchemy as sa


class Debt(Base):
    __tablename__ = "DEBTS"
    id = Column(Integer, Identity(start=1, increment=1), primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("CUSTOMER.id"), nullable=False)
    amount = Column(Float, nullable=False)
    debt_date = Column(Date, nullable=False)
    paid_debt = Column(Float)
    current_debt = Column(Float)
    created_by = Column(Integer)
    created_at = Column(Date, server_default=sa.func.now())
    updated_at = Column(Date, server_default=sa.func.now(), onupdate=sa.func.now())
    updated_at = Column(Date)

    customer = relationship("Customer", back_populates="debts")
