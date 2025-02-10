from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database_file import get_db
from models.audit_log import AuditLog
from schemas.audit_log import AuditLogResponse

router = APIRouter(prefix="/audit_logs", tags=["Audit Logs"])


@router.get("/", response_model=list[AuditLogResponse])
def get_all_audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).all()
