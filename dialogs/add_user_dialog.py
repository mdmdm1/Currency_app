from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QComboBox,
    QFrame,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from dialogs.base_dialog import BaseDialog
from database.models import User
from database.database import SessionLocal
import re


class AddUserDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Ajouter un nouvel utilisateur", parent)

    def create_form_fields(self):
        # Initialize input fields
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(["admin", "utilisateur", "auditeur"])
        self.is_active_input = QComboBox()
        self.is_active_input.addItems(["Actif", "Inactif"])

        # Define fields with their labels
        fields = [
            ("Nom d'utilisateur:", self.username_input),
            ("Mot de passe:", self.password_input),
            ("Rôle:", self.role_dropdown),
            ("Statut du compte:", self.is_active_input),
        ]

        # Create rows for each field
        for label, widget in fields:
            self.create_input_row(label, widget)

    def on_submit(self):
        """Handle form submission."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_dropdown.currentText()
        is_active = self.is_active_input.currentText() == "Actif"

        print(f"Nom d'utilisateur saisi : '{username}'")

        # Validate inputs
        if not username:
            self.show_error("Le nom d'utilisateur est requis.")
            return

        if not password:
            self.show_error("Le mot de passe est requis.")
            return

        if not re.match("^[a-zA-Z0-9_.-]+$", username):
            self.show_error(
                "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, points, "
                "underscores et tirets."
            )
            return

        # Hash the password
        hashed_password = self.hash_password(password)

        try:
            # Save user to database
            self.save_user_to_db(username, hashed_password, role, is_active)
            QMessageBox.information(self, "Succès", "Utilisateur créé avec succès!")
            self.accept()
        except IntegrityError:
            self.show_error("Le nom d'utilisateur existe déjà.")
        except Exception as e:
            self.show_error(f"Échec de la création de l'utilisateur : {str(e)}")

    def hash_password(self, password):
        """Hash the password for secure storage."""
        import hashlib

        return hashlib.sha256(password.encode()).hexdigest()

    def save_user_to_db(self, username, hashed_password, role, is_active):

        with SessionLocal() as session:
            user = User(
                username=username,
                password=hashed_password,
                role=role,
                is_active=is_active,
            )
            session.add(user)
            session.commit()

    def show_error(self, message):
        """Display an error message."""
        QMessageBox.critical(self, "Erreur", message)
