import json
from PyQt5.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QDialog,
    QTableWidgetItem,
    QMessageBox,
)
from PyQt5.QtCore import Qt
import requests
from dialogs.add_user_dialog import AddUserDialog
from dialogs.edit_user_dialog import EditUserDialog
from dialogs.user_history_dialog import UserHistoryDialog
from pages.base_page import BasePage
from utils.translation_manager import TranslationManager
from config import API_BASE_URL


class UserManagementPage(BasePage):
    def __init__(self, parent):
        super().__init__(
            parent, title=TranslationManager.tr("Gestion des utilisateurs")
        )
        self.user_id = parent.user_id
        self.api_base_url = API_BASE_URL
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI for user management."""
        # Set up table headers
        headers = [
            TranslationManager.tr("ID"),
            TranslationManager.tr("Nom d'utilisateur"),
            TranslationManager.tr("Rôle"),
            # TranslationManager.tr("Dernière connexion"),
            TranslationManager.tr("Actions"),
        ]
        self.setup_table_headers(headers)

        # Add a button for adding new users
        button_layout = QHBoxLayout()
        self.add_user_button = QPushButton(
            TranslationManager.tr("Ajouter un utilisateur")
        )
        self.add_user_button.clicked.connect(self.add_user)
        button_layout.addWidget(self.add_user_button, alignment=Qt.AlignLeft)

        self.layout.insertLayout(0, button_layout)

        # Hide the total label since it's not needed for this page
        self.hide_total_label()

        # Load and display user data
        self.load_user_data()

    def load_user_data(self):
        """Load user data from the database and populate the table."""
        try:
            response = requests.get(f"{self.api_base_url}/users")

            response.raise_for_status()
            users = response.json()

            self.table.setRowCount(len(users))
            for row_idx, user in enumerate(users):
                """
                last_login = user.created_at.strftime(
                    "%Y-%m-%d"
                )
                """  # Modify TO using a real last login field

                row_data = [
                    user["id"],
                    user["username"],
                    user["role"],
                ]

                # Populate table with user data
                for col_idx, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)

                    # Make the cell non-editable
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row_idx, col_idx, item)

                # Add action buttons for each user
                buttons_config = [
                    {
                        "text": TranslationManager.tr("Modifier"),
                        "color": "#28a745",
                        "callback": self.edit_user,
                        "width": 65,
                    },
                    {
                        "text": TranslationManager.tr("Supprimer"),
                        "color": "#dc3545",
                        "callback": self.delete_user,
                        "width": 65,
                    },
                    {
                        "text": TranslationManager.tr("Historique"),
                        "color": "#17a2b8",
                        "callback": self.view_user_history,
                        "width": 65,
                    },
                ]

                self.add_action_buttons(row_idx, user["id"], buttons_config)

        except requests.exceptions.RequestException as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                f"{TranslationManager.tr('Erreur lors du chargement')}: {str(e)}",
            )

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_user_data()

    def edit_user(self, user_id, row):
        dialog = EditUserDialog(self, user_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_user_data()

    def delete_user(self, user_id, row):
        confirmation = QMessageBox(self)
        confirmation.setIcon(QMessageBox.Question)
        confirmation.setWindowTitle(TranslationManager.tr("Confirmer la suppression"))
        confirmation.setText(
            TranslationManager.tr(
                "Êtes-vous sûr de vouloir supprimer cet utilisateur ?"
            )
        )

        yes_button = confirmation.addButton(
            TranslationManager.tr("Oui"), QMessageBox.YesRole
        )
        no_button = confirmation.addButton(
            TranslationManager.tr("Non"), QMessageBox.NoRole
        )

        confirmation.setDefaultButton(no_button)
        confirmation.exec_()

        if confirmation.clickedButton() == yes_button:
            try:

                user_response = requests.get(f"{self.api_base_url}/users/{user_id}")
                user_response.raise_for_status()
                user = user_response.json()

                response = requests.delete(f"{self.api_base_url}/users/{user_id}")
                response.raise_for_status()

                audit_response = requests.post(
                    f"{self.api_base_url}/audit_logs/",
                    json={
                        "table_name": TranslationManager.tr("Utilisateurs"),
                        "operation": TranslationManager.tr("SUPPRESSION"),
                        "record_id": user_id,
                        "user_id": self.user_id,
                        "changes": json.dumps(
                            {
                                TranslationManager.tr("username"): user["username"],
                                TranslationManager.tr("role"): user["role"],
                            }
                        ),
                    },
                )
                audit_response.raise_for_status()

                self.load_user_data()
            except requests.exceptions.RequestException as e:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    f"{TranslationManager.tr('Erreur lors de la suppression')}: {str(e)}",
                )

    def view_user_history(self, user_id, row):
        dialog = UserHistoryDialog(user_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_user_data()

    def retranslate_ui(self):

        # Update page title
        self.setWindowTitle(TranslationManager.tr("Gestion des utilisateurs"))

        # Update table headers
        self.setup_table_headers(
            [
                TranslationManager.tr("ID"),
                TranslationManager.tr("Nom d'utilisateur"),
                TranslationManager.tr("Rôle"),
                # TranslationManager.tr("Dernière connexion"),
                TranslationManager.tr("Actions"),
            ]
        )
        self.add_user_button.setText(TranslationManager.tr("Ajouter un utilisateur"))

        self.load_user_data()
