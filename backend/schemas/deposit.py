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


class DepositResponse(DepositBase):
    id: int

    class Config:
        from_attributes = True
