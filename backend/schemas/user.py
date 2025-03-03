from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    username: str
    password: str
    is_active: bool = True
    role: str  # e.g., 'admin', 'user', 'auditor', 'SUPERADMIN'


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = True
    role: Optional[str] = "user"  # e.g., 'admin', 'user', 'auditor', 'SUPERADMIN'
