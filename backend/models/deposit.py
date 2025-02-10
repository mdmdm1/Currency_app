from database_file import Base
from sqlalchemy import Column, Date, Float, ForeignKey, Identity, Integer, Unicode
from sqlalchemy.orm import relationship


class Deposit(Base):
    __tablename__ = "DEPOSITS"
    id = Column(Integer, Identity(start=1, increment=1), primary_key=True, index=True)
    person_name = Column(Unicode(255), nullable=False)
    amount = Column(Float, nullable=False)
    deposit_date = Column(Date, nullable=False)
    released_deposit = Column(Float)
    current_debt = Column(Float)
    customer_id = Column(Integer, ForeignKey("CUSTOMER.id"))

    customer = relationship("Customer", back_populates="deposits")
