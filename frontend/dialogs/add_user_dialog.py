import json
from PyQt5.QtWidgets import (
    QLineEdit,
    QComboBox,
    QMessageBox,
    QWidget,
    QPushButton,
    QHBoxLayout,
)
import requests
from sqlalchemy.exc import IntegrityError
from PyQt5.QtCore import Qt
from dialogs.base_dialog import BaseDialog
from database.models import User
from database.database import SessionLocal
import re
import bcrypt

from utils.translation_manager import TranslationManager
from config import API_BASE_URL


class AddUserDialog(BaseDialog):
    def __init__(self, parent):
        super().__init__(TranslationManager.tr("Ajouter un nouvel utilisateur"), parent)
        self.current_user_id = parent.user_id
        self.api_base_url = API_BASE_URL

    def create_form_fields(self):

        for i in reversed(range(self.form_layout.count())):
            self.form_layout.itemAt(i).widget().deleteLater()

        # Initialize input fields
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(
            [
                TranslationManager.tr("admin"),
                TranslationManager.tr("sous admin"),
                TranslationManager.tr("employer"),
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
        self.fields = [
            (TranslationManager.tr("Nom d'utilisateur:"), self.username_input),
            (TranslationManager.tr("Mot de passe:"), self.password_input),
            (TranslationManager.tr("Role:"), self.role_dropdown),
            (TranslationManager.tr("Statut du compte:"), self.is_active_input),
        ]

        # Create rows for each field
        for label, widget in self.fields:
            self.create_input_row(label, widget)

    def create_buttons(self):
        self.buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(self.buttons_widget)
        buttons_layout.setSpacing(15)

        self.cancel_button = QPushButton(TranslationManager.tr("Annuler"))
        self.submit_button = QPushButton(TranslationManager.tr("Effectuer"))

        self.submit_button.setMinimumHeight(45)
        self.submit_button.setMinimumWidth(120)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setStyleSheet(self._get_primary_button_style())

        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setStyleSheet(self._get_secondary_button_style())

        self.submit_button.clicked.connect(self.on_submit)
        self.cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.submit_button)

    def on_submit(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_dropdown.currentText()
        is_active = self.is_active_input.currentText() == TranslationManager.tr("Actif")

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

        if self.user_exists(username):
            self.show_error(TranslationManager.tr("Le nom d'utilisateur existe déjà."))
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
        except requests.exceptions.RequestException as e:

            self.show_error(
                TranslationManager.tr(
                    f"Échec de la création de l'utilisateur : {str(e)}"
                )
            )

    def user_exists(self, username):
        try:
            response = requests.get(f"{self.api_base_url}/users/exists/{username}")
            if response.status_code == 400:
                return True  # User exists
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error checking user existence: {e}")
            return False

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def save_user_to_db(self, username, hashed_password, role, is_active):

        try:
            new_user_response = requests.post(
                f"{self.api_base_url}/users/",
                json={
                    "username": username,
                    "password": hashed_password,
                    "role": role,
                    "is_active": is_active,
                },
            )
            new_user_response.raise_for_status()
            user = new_user_response.json()

            # Log audit entry for new debt
            audit_response = requests.post(
                f"{self.api_base_url}/audit_logs/",
                json={
                    "table_name": TranslationManager.tr("Utilisateurs"),
                    "operation": TranslationManager.tr("INSERTION"),
                    "record_id": user["id"],
                    "user_id": self.current_user_id,
                    "changes": json.dumps(
                        {
                            TranslationManager.tr("username"): user["username"],
                            TranslationManager.tr("role"): user["role"],
                        }
                    ),
                },
            )
            audit_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.show_error(
                TranslationManager.tr(
                    f"Erreur lors de la création de l'utilisateur : {str(e)}"
                )
            )
            self.reject()

    def show_error(self, message):
        QMessageBox.critical(self, TranslationManager.tr("Erreur"), message)

    def retranslate_ui(self):

        print("Retranslating AddUserDialog UI")
        self.setWindowTitle(TranslationManager.tr("Ajouter un nouvel utilisateur"))
        # Remove existing widgets from form layout
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Recreate form fields
        self.cancel_button = QPushButton(TranslationManager.tr("Annuler"))
        self.submit_button = QPushButton(TranslationManager.tr("Effectuer"))

        self.create_form_fields()
        self.create_buttons()

        # Set layout direction
        main_window = self._find_main_window()
        if main_window and main_window.translation_manager.current_language == "ar":
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

        self.adjustSize()
