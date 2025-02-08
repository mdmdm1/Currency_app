from pydantic import BaseModel
from typing import Optional
from datetime import date


class CustomerBase(BaseModel):
    name: str
    identite: Optional[str] = None
    telephone: Optional[str] = None
    date_naisse: Optional[date] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int

    class Config:
        from_attributes = True
