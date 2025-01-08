from PyQt5.QtWidgets import QLineEdit, QComboBox, QMessageBox
from database.database import SessionLocal
from database.models import User
from dialogs.base_dialog import BaseDialog


class EditUserDialog(BaseDialog):
    def __init__(self, user_id, parent=None):
        super().__init__("Modifier l'utilisateur", parent)
        self.user_id = user_id
        # self.username_input = None
        # self.role_combobox = None
        self.load_user_data()

    def create_form_fields(self):
        """Create the form fields for editing user details."""
        self.username_input = QLineEdit()
        self.create_input_row("Nom d'utilisateur:", self.username_input)

        self.role_combobox = QComboBox()
        self.role_combobox.addItems(
            ["Admin", "Utilisateur", "Visiteur"]
        )  # Example roles
        self.create_input_row("Rôle:", self.role_combobox)

    def on_submit(self):
        """Save the modified user details to the database."""
        new_username = self.username_input.text().strip()
        new_role = self.role_combobox.currentText()

        if not new_username:
            self.show_error("Le nom d'utilisateur ne peut pas être vide.")
            return

        session = SessionLocal()
        try:
            user = session.query(User).get(self.user_id)
            if not user:
                self.show_error("Utilisateur introuvable.")
                self.reject()
                return

            user.username = new_username
            user.role = new_role
            session.commit()

            QMessageBox.information(self, "Succès", "Utilisateur modifié avec succès.")
            self.accept()

        except Exception as e:
            session.rollback()
            self.show_error(f"Erreur lors de la sauvegarde: {str(e)}")

        finally:
            session.close()

    def load_user_data(self):
        """Load user data into the form fields."""
        session = SessionLocal()
        try:
            user = session.query(User).get(self.user_id)
            if not user:
                self.show_error("Utilisateur introuvable.")
                self.reject()
                return

            self.username_input.setText(user.username)
            self.role_combobox.setCurrentText(user.role)

        except Exception as e:
            self.show_error(f"Erreur lors du chargement: {str(e)}")
            self.reject()

        finally:
            session.close()
