from pydantic import BaseModel
from typing import Optional
from datetime import date


class DepositBase(BaseModel):
    person_name: str
    amount: float
    deposit_date: date
    released_deposit: Optional[float] = None
    current_debt: Optional[float] = None
    customer_id: Optional[int] = None


class DepositCreate(DepositBase):
    pass


class DepositResponseWithCustomerId(DepositBase):
    id: int
    customer_id: int

    class Config:
        from_attributes = True


class DepositResponse(DepositBase):
    id: int

    class Config:
        from_attributes = True


class DepositUpdate(BaseModel):
    person_name: str = None
    amount: float = None
    deposit_date: date = None
    released_deposit: Optional[float] = None
    current_debt: Optional[float] = None
