from database.models import User
from database.database import SessionLocal


def is_user_admin(user_id):
    session = SessionLocal()
    try:
        # Fetch the user by ID
        user = session.get(User, user_id)
        if not user:
            return False  # User not found

        # Check if the user role is 'admin'
        return hasattr(user, "role") and user.role == "admin"
    except Exception as e:
        print(f"Error while checking user admin status: {e}")
        return False  # Return False in case of an error
    finally:
        session.close()
