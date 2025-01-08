from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QDialog
from PyQt5.QtCore import Qt

from dialogs.add_user_dialog import AddUserDialog
from pages.base_page import BasePage


class UserManagementPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent, title="User Management")
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI for user management."""
        # Set up table headers
        headers = ["Username", "Privileges", "Last Login", "Actions"]
        self.setup_table_headers(headers)

        # Add a button for adding new users
        button_layout = QHBoxLayout()
        self.add_user_button = QPushButton("Add User")
        self.add_user_button.clicked.connect(self.add_user)
        button_layout.addWidget(self.add_user_button, alignment=Qt.AlignLeft)

        self.layout.insertLayout(0, button_layout)

        # Hide the total label since it's not needed for this page
        self.hide_total_label()

    def populate_table(self, users):
        """Populate the table with user data."""
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table.setItem(row, 0, self.create_table_item(user["username"]))
            self.table.setItem(row, 1, self.create_table_item(user["privileges"]))
            self.table.setItem(row, 2, self.create_table_item(user["last_login"]))

            # Add action buttons for each user
            self.add_action_buttons(
                row,
                user["id"],
                [
                    {
                        "text": "Edit",
                        "color": "#28a745",
                        "callback": self.edit_user,
                        "width": 70,
                    },
                    {
                        "text": "Delete",
                        "color": "#dc3545",
                        "callback": self.delete_user,
                        "width": 70,
                    },
                    {
                        "text": "History",
                        "color": "#17a2b8",
                        "callback": self.view_user_history,
                        "width": 70,
                    },
                ],
            )

    def add_user(self):
        dialog = AddUserDialog()
        if dialog.exec_() == QDialog.Accepted:
            print("User added successfully!")

    def edit_user(self, user_id, row):
        """Edit the selected user."""
        print(f"Edit User {user_id} at row {row}")

    def delete_user(self, user_id, row):
        """Delete the selected user."""
        print(f"Delete User {user_id} at row {row}")

    def view_user_history(self, user_id, row):
        """View the history of the selected user."""
        print(f"View History for User {user_id} at row {row}")
