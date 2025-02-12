from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Identity,
    Integer,
    String,
    Float,
    ForeignKey,
    Date,
    Text,
    Unicode,
)
from sqlalchemy.orm import relationship
from database.database import Base
import sqlalchemy as sa


class Customer(Base):
    __tablename__ = "CUSTOMER"
    id = Column(Integer, Identity(start=1, increment=1), primary_key=True, index=True)
    name = Column(Unicode(255), nullable=False)
    identite = Column(Unicode(255))
    telephone = Column(Unicode(20))
    date_naisse = Column(Date)

    deposits = relationship("Deposit", back_populates="customer")
    debts = relationship("Debt", back_populates="customer")


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


class TreasuryOperation(Base):
    __tablename__ = "TREASURY_OPERATIONS"
    treasury_operations_id = Column(
        Integer, Identity(start=1, increment=1), primary_key=True, index=True
    )
    name = Column(String(255), nullable=False)
    input = Column(Float)
    output = Column(Float)
    balance = Column(Float)


class Currency(Base):
    __tablename__ = "CURRENCIES"
    id = Column(Integer, Identity(start=1, increment=1), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(3), nullable=False, unique=True)
    input = Column(Float)
    output = Column(Float)
    balance = Column(Float)
    rate = Column(Float, nullable=False, default=1.0)


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
