from unittest.mock import Base
from sqlalchemy import Column, Float, Identity, Integer, String


class Currency(Base):
    __tablename__ = "CURRENCIES"
    id = Column(Integer, Identity(start=1, increment=1), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(3), nullable=False, unique=True)
    input = Column(Float)
    output = Column(Float)
    balance = Column(Float)
    rate = Column(Float, nullable=False, default=1.0)
