from PyQt5.QtWidgets import (
    QLineEdit,
    QComboBox,
    QMessageBox,
)
from sqlalchemy.exc import IntegrityError
from dialogs.base_dialog import BaseDialog
from database.models import User
from database.database import SessionLocal
import re
import bcrypt

from utils.translation_manager import TranslationManager


class AddUserDialog(BaseDialog):
    def __init__(self, parent):
        super().__init__(TranslationManager.tr("Ajouter un nouvel utilisateur"), parent)
        self.current_user_id = parent.user_id

    def create_form_fields(self):
        # Initialize input fields
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(
            [
                TranslationManager.tr("admin"),
                TranslationManager.tr("utilisateur"),
                TranslationManager.tr("auditeur"),
            ]
        )
        self.is_active_input = QComboBox()
        self.is_active_input.addItems(
            [
                TranslationManager.tr("Actif"),
                TranslationManager.tr("Inactif"),
            ]
        )

        # Define fields with their labels
        fields = [
            (TranslationManager.tr("Nom d'utilisateur:"), self.username_input),
            (TranslationManager.tr("Mot de passe:"), self.password_input),
            (TranslationManager.tr("Rôle:"), self.role_dropdown),
            (TranslationManager.tr("Statut du compte:"), self.is_active_input),
        ]

        # Create rows for each field
        for label, widget in fields:
            self.create_input_row(label, widget)

    def on_submit(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_dropdown.currentText()
        is_active = self.is_active_input.currentText() == TranslationManager.tr("Actif")

        print(f"{TranslationManager.tr('Nom d\'utilisateur saisi')} : '{username}'")

        # Validate inputs
        if not username:
            self.show_error(TranslationManager.tr("Le nom d'utilisateur est requis."))
            return

        if not password:
            self.show_error(TranslationManager.tr("Le mot de passe est requis."))
            return

        if not re.match("^[a-zA-Z0-9_.-]+$", username):
            self.show_error(
                TranslationManager.tr(
                    "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, points, "
                    "underscores et tirets."
                )
            )
            return

        hashed_password = self.hash_password(password)

        try:
            self.save_user_to_db(username, hashed_password, role, is_active)
            QMessageBox.information(
                self,
                TranslationManager.tr("Succès"),
                TranslationManager.tr("Utilisateur créé avec succès!"),
            )
            self.accept()
        except IntegrityError:
            self.show_error(TranslationManager.tr("Le nom d'utilisateur existe déjà."))
        except Exception as e:
            self.show_error(
                TranslationManager.tr(
                    "Échec de la création de l'utilisateur : {str(e)}"
                )
            )

    def show_error(self, message):
        QMessageBox.critical(self, TranslationManager.tr("Erreur"), message)
