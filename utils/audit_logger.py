from sqlalchemy.orm import Session
import json

from database.models import AuditLog


def log_audit_entry(
    db_session: Session,
    table_name: str,
    operation: str,
    record_id: int,
    user_id: int,
    changes: dict = None,
):
    """Log an entry in the audit log."""
    audit_entry = AuditLog(
        table_name=table_name,
        operation=operation,
        record_id=record_id,
        user_id=user_id,
        changes=json.dumps(changes) if changes else None,
    )
    db_session.add(audit_entry)
    db_session.commit()
