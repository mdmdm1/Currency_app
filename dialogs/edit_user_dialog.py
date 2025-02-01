from PyQt5.QtWidgets import QLineEdit, QComboBox, QMessageBox
from database.database import SessionLocal
from database.models import User
from dialogs.base_dialog import BaseDialog
from utils.translation_manager import TranslationManager


class EditUserDialog(BaseDialog):
    def __init__(self, parent, user_id):
        super().__init__(TranslationManager.tr("Edit User"), parent)
        self.current_user_id = parent.user_id
        self.user_id = user_id

        self.load_user_data()

    def create_form_fields(self):
        """Create the form fields for editing user details."""
        self.username_input = QLineEdit()
        self.create_input_row(TranslationManager.tr("Username:"), self.username_input)

        self.role_combobox = QComboBox()
        self.role_combobox.addItems(
            [
                TranslationManager.tr("Admin"),
                TranslationManager.tr("User"),
                TranslationManager.tr("Visitor"),
            ]
        )
        self.create_input_row(TranslationManager.tr("Role:"), self.role_combobox)

    def on_submit(self):
        """Save the modified user details to the database."""
        new_username = self.username_input.text().strip()
        new_role = self.role_combobox.currentText()

        if not new_username:
            self.show_error(TranslationManager.tr("Username cannot be empty."))
            return

        session = SessionLocal()
        try:
            user = session.query(User).get(self.user_id)
            if not user:
                self.show_error(TranslationManager.tr("User not found."))
                self.reject()
                return

            user.username = new_username
            user.role = new_role
            session.commit()

            QMessageBox.information(
                self,
                TranslationManager.tr("Success"),
                TranslationManager.tr("User successfully updated."),
            )
            self.accept()

        except Exception as e:
            session.rollback()
            self.show_error(
                TranslationManager.tr("Error saving changes:") + f" {str(e)}"
            )

        finally:
            session.close()

    def load_user_data(self):
        """Load user data into the form fields."""
        session = SessionLocal()
        try:
            user = session.query(User).get(self.user_id)
            if not user:
                self.show_error(TranslationManager.tr("User not found."))
                self.reject()
                return

            self.username_input.setText(user.username)
            self.role_combobox.setCurrentText(user.role)

        except Exception as e:
            self.show_error(TranslationManager.tr("Error loading data:") + f" {str(e)}")
            self.reject()

        finally:
            session.close()
