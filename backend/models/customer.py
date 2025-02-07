from sqlalchemy import Column, Date, Integer, String, Identity, Unicode
from sqlalchemy.orm import relationship
from database import Base


class Customer(Base):
    __tablename__ = "CUSTOMER"
    id = Column(Integer, Identity(start=1, increment=1), primary_key=True, index=True)
    name = Column(Unicode(255), nullable=False)
    identite = Column(Unicode(255))
    telephone = Column(Unicode(20))
    date_naisse = Column(Date)

    deposits = relationship("Deposit", back_populates="customer")
    debts = relationship("Debt", back_populates="customer")
