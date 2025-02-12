from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database_file import get_db
from models.audit_log import AuditLog
from schemas.audit_log import AuditLogCreate, AuditLogResponse

router = APIRouter(prefix="/audit_logs", tags=["Audit Logs"])


@router.post("/", response_model=AuditLogResponse)
def create_audit_log(auditlog: AuditLogCreate, db: Session = Depends(get_db)):
    new_audit_log = AuditLog(**auditlog.model_dump())
    db.add(new_audit_log)
    db.commit()
    db.refresh(new_audit_log)
    return new_audit_log


@router.get("/", response_model=list[AuditLogResponse])
def get_all_audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).all()
