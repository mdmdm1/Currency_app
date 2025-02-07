from unittest.mock import Base
from sqlalchemy import Column, Float, Identity, Integer, String


class TreasuryOperation(Base):
    __tablename__ = "TREASURY_OPERATIONS"
    treasury_operations_id = Column(
        Integer, Identity(start=1, increment=1), primary_key=True, index=True
    )
    name = Column(String(255), nullable=False)
    input = Column(Float)
    output = Column(Float)
    balance = Column(Float)
