from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditLogBase(BaseModel):
    table_name: str
    operation: str
    record_id: int
    user_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    changes: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogResponse(AuditLogBase):
    id: int

    class Config:
        from_attributes = True


class AuditLogResponseWithUser(AuditLogBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
