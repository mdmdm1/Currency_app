from pydantic import BaseModel
from typing import Optional
from datetime import date


class DebtBase(BaseModel):
    customer_id: int
    amount: float
    debt_date: date
    paid_debt: Optional[float] = None
    current_debt: Optional[float] = None
    created_by: Optional[int] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None


class DebtCreate(DebtBase):
    pass


class DebtResponse(DebtBase):
    id: int

    class Config:
        from_attributes = True


class DebtResponseWithCustomerId(DebtBase):
    id: int
    customer_id: int

    class Config:
        from_attributes = True


class DebtUpdate(BaseModel):
    amount: Optional[float] = None
    debt_date: Optional[date] = None
    paid_debt: Optional[float] = None
    current_debt: Optional[float] = None
    created_by: Optional[int] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
