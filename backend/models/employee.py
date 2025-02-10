from database_file import Base

from sqlalchemy import Column, Date, Identity, Integer, String


class Employee(Base):
    __tablename__ = "EMPLOYEE"
    employee_id = Column(
        Integer, Identity(start=1, increment=1), primary_key=True, index=True
    )
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    carte_ident = Column(String(255))
    telephone = Column(String(20))
    date_naiss = Column(Date)
    password = Column(String(255), nullable=False)
    permission_role = Column(String(50), default="user")
