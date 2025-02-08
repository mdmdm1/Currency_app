from pydantic import BaseModel
from typing import Optional
from datetime import date


class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    carte_ident: Optional[str] = None
    telephone: Optional[str] = None
    date_naiss: Optional[date] = None
    password: str
    permission_role: Optional[str] = "user"


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    employee_id: int

    class Config:
        from_attributes = True
