from database.database import SessionLocal
from database.models import AuditLog
from datetime import datetime


def log_user_action(user_id, action, details=""):
    """
    Logs user actions to the AuditLog table.

    Args:
        user_id (int): The ID of the user performing the action.
        action (str): A short description of the action performed.
        details (str, optional): Additional details about the action. Defaults to "".
    """
    session = SessionLocal()
    try:
        audit_log = AuditLog(
            user_id=user_id, action=action, details=details, timestamp=datetime.now()
        )
        session.add(audit_log)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error logging action: {e}")
    finally:
        session.close()
