import json
from PyQt5.QtWidgets import QLineEdit, QComboBox, QMessageBox
import requests
from dialogs.base_dialog import BaseDialog
from utils.translation_manager import TranslationManager
from config import API_BASE_URL


class EditUserDialog(BaseDialog):
    def __init__(self, parent, user_id):
        super().__init__(TranslationManager.tr("Modifier l'utilisateur"), parent)
        self.current_user_id = parent.user_id
        self.user_id = user_id
        self.api_base_url = API_BASE_URL

        self.load_user_data()

    def create_form_fields(self):
        """Create the form fields for editing user details."""
        self.username_input = QLineEdit()
        self.create_input_row(
            TranslationManager.tr("Nom d'utilisateur:"), self.username_input
        )

        self.role_combobox = QComboBox()
        self.role_combobox.addItems(
            [
                TranslationManager.tr("admin"),
                TranslationManager.tr("sous admin"),
                TranslationManager.tr("employer"),
            ]
        )
        self.create_input_row(TranslationManager.tr("Rôle:"), self.role_combobox)

        self.status_combobox = QComboBox()
        self.status_combobox.addItems(
            [
                TranslationManager.tr("Actif"),
                TranslationManager.tr("Inactif"),
            ]
        )
        self.create_input_row(
            TranslationManager.tr("Statut du compte:"), self.status_combobox
        )

    def on_submit(self):
        """Save the modified user details to the database."""
        new_username = self.username_input.text().strip()
        new_role = self.role_combobox.currentText()
        new_is_active = self.status_combobox.currentText() == TranslationManager.tr(
            "Actif"
        )

        if not new_username:
            self.show_error(
                TranslationManager.tr("Le nom d'utilisateur ne pas être vide.")
            )
            return

        try:
            old_data = {
                TranslationManager.tr("username"): self.user["username"],
                TranslationManager.tr("role"): self.user["role"],
                TranslationManager.tr("is_active"): self.user["is_active"],
            }
            updated_data = {
                "username": new_username,
                "role": new_role,
                "is_active": new_is_active,
            }
            response = requests.put(
                f"{self.api_base_url}/users/{self.user_id}", json=updated_data
            )

            response.raise_for_status()
            user = response.json()

            audit_response = requests.post(
                f"{self.api_base_url}/audit_logs/",
                json={
                    "table_name": TranslationManager.tr("Utilisateurs"),
                    "operation": TranslationManager.tr("MISE A JOUR"),
                    "record_id": user["id"],
                    "user_id": self.current_user_id,
                    "changes": json.dumps(
                        {
                            "old": old_data,
                            "new": {
                                TranslationManager.tr("username"): user["username"],
                                TranslationManager.tr("role"): user["role"],
                                TranslationManager.tr("is_active"): user["is_active"],
                            },
                        }
                    ),
                },
            )
            audit_response.raise_for_status()

            QMessageBox.information(
                self,
                TranslationManager.tr("Succès"),
                TranslationManager.tr(
                    "Les modifications ont été enregistrées avec succès."
                ),
            )
            self.accept()

        except requests.exceptions.RequestException as e:

            self.show_error(
                TranslationManager.tr("Erreur dans le sauvegarde les modifications:")
                + f" {str(e)}"
            )

    def load_user_data(self):
        """Load user data into the form fields."""
        try:
            response = requests.get(f"{self.api_base_url}/users/{self.user_id}")
            response.raise_for_status()

            if response.status_code == 404:
                self.show_error(TranslationManager.tr("Utilisateur introuvable."))
                self.reject()
                return
            self.user = response.json()

            self.username_input.setText(self.user["username"])
            self.role_combobox.setCurrentText(self.user["role"])
            if self.user["is_active"] == True:
                status = TranslationManager.tr("Actif")
            else:
                status = TranslationManager.tr("Inactif")
            self.status_combobox.setCurrentText(status)

        except requests.exceptions.RequestException as e:
            self.show_error(
                TranslationManager.tr("Erreur de chargement de données:") + f" {str(e)}"
            )
            self.reject()
