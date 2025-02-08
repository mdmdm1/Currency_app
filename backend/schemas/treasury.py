from pydantic import BaseModel
from typing import Optional
from datetime import date


class TreasuryOperationBase(BaseModel):
    name: str
    input: Optional[float] = None
    output: Optional[float] = None
    balance: Optional[float] = None


class TreasuryOperationCreate(TreasuryOperationBase):
    pass


class TreasuryOperationResponse(TreasuryOperationBase):
    treasury_operations_id: int

    class Config:
        from_attributes = True
