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
