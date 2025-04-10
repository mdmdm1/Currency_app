# schemas/currency.py
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


class CurrencyUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    input: Optional[float] = None
    output: Optional[float] = None
    balance: Optional[float] = None
    rate: Optional[float] = None


class CurrencyConversionRequest(BaseModel):
    source_currency: str
    target_currency: str
    amount: float
    converted_amount: float
    user_id: int
