from PyQt5.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QDialog,
    QTableWidgetItem,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from sqlalchemy.exc import SQLAlchemyError
from database.database import SessionLocal
from database.models import User
from dialogs.add_user_dialog import AddUserDialog
from dialogs.edit_user_dialog import EditUserDialog
from dialogs.user_history_dialog import UserHistoryDialog
from pages.base_page import BasePage


class UserManagementPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, title="Gestion des utilisateurs")
        self.user_id = parent.user_id
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI for user management."""
        # Set up table headers
        headers = ["Nom d'utilisateur", "Rôle", "Dernière connexion", "Actions"]
        self.setup_table_headers(headers)

        # Add a button for adding new users
        button_layout = QHBoxLayout()
        self.add_user_button = QPushButton("Ajouter un utilisateur")
        self.add_user_button.clicked.connect(self.add_user)
        button_layout.addWidget(self.add_user_button, alignment=Qt.AlignLeft)

        self.layout.insertLayout(0, button_layout)

        # Hide the total label since it's not needed for this page
        self.hide_total_label()

        # Load and display user data
        self.load_user_data()

    def load_user_data(self):
        """Load user data from the database and populate the table."""
        session = SessionLocal()
        try:
            users = session.query(User).all()

            self.table.setRowCount(len(users))
            for row_idx, user in enumerate(users):
                last_login = user.created_at.strftime(
                    "%Y-%m-%d"
                )  # Modify TO using a real last login field

                row_data = [
                    user.username,
                    user.role,
                    last_login,
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
                        "text": "Modifier",
                        "color": "#28a745",
                        "callback": self.edit_user,
                        "width": 65,
                    },
                    {
                        "text": "Supprimer",
                        "color": "#dc3545",
                        "callback": self.delete_user,
                        "width": 65,
                    },
                    {
                        "text": "Historique",
                        "color": "#17a2b8",
                        "callback": self.view_user_history,
                        "width": 65,
                    },
                ]

                self.add_action_buttons(row_idx, user.id, buttons_config)

        except SQLAlchemyError as e:
            self.show_error_message("Erreur", f"Erreur lors du chargement: {str(e)}")
        finally:
            session.close()

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_user_data()

    def edit_user(self, user_id, row):
        dialog = EditUserDialog(self, user_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_user_data()

    def delete_user(self, user_id, row):
        confirmation = QMessageBox.question(
            self,
            "Confirmer la suppression",
            "Êtes-vous sûr de vouloir supprimer cette dette ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirmation == QMessageBox.Yes:
            session = SessionLocal()
            try:
                user = session.query(User).get(user_id)
                if user:
                    session.delete(user)
                    session.commit()
                    self.load_user_data()
            except SQLAlchemyError as e:
                self.show_error_message(
                    "Erreur", f"Erreur lors de la suppression: {str(e)}"
                )
            finally:
                session.close()

    def view_user_history(self, user_id, row):
        dialog = UserHistoryDialog(user_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_user_data()
