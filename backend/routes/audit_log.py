from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database_file import get_db
from models.audit_log import AuditLog
from schemas.audit_log import AuditLogCreate, AuditLogResponse, AuditLogResponseWithUser

router = APIRouter(prefix="/audit_logs", tags=["Audit Logs"])


@router.post("/", response_model=AuditLogResponse)
def create_audit_log(auditlog: AuditLogCreate, db: Session = Depends(get_db)):
    new_audit_log = AuditLog(**auditlog.model_dump())
    db.add(new_audit_log)
    db.commit()
    db.refresh(new_audit_log)
    return new_audit_log


@router.get("/recent", response_model=list[AuditLogResponse])
def get_recent_logs(db: Session = Depends(get_db)):
    recent_logs = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())  # Order by latest
        .limit(5)  # Get the last 5 logs
        .all()
    )
    return recent_logs


@router.get("/by-user/{user_id}", response_model=list[AuditLogResponseWithUser])
def get_logs(user_id: int, db: Session = Depends(get_db)):
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return logs


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@router.get("/", response_model=list[AuditLogResponse])
def get_all_audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).all()
