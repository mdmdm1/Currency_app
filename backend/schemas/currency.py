from pydantic import BaseModel
from typing import Optional


class CurrencyBase(BaseModel):
    name: str
    code: str
    input: float
    output: float
    balance: float
    rate: float = 1.0


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyResponse(CurrencyBase):
    id: int

    class Config:
        from_attributes = True
