from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, 
    QDateEdit, QComboBox, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap

class EditEmployeeDialog(QDialog):
    def __init__(self, parent=None, employee_data=None):
        super().__init__(parent)
        
        # Set window title and size
        self.setWindowTitle("Edit Employee")
        self.setFixedSize(500, 600)  # Same size as AddEmployeeDialog

        # Apply similar stylesheet as AddEmployeeDialog
        self.setStyleSheet("""
            QDialog {
                background-color: #F9F9F9;
                font-family: Arial;
                font-size: 14px;
            }
            QLabel {
                font-weight: bold;
                color: #333333;
            }
            QLineEdit, QDateEdit, QComboBox {
                padding: 6px;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border-color: #4CAF50;
            }
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton#cancelButton {
                background-color: #f44336;
                color: white;
            }
            QPushButton#saveButton {
                background-color: #4CAF50;
                color: white;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()
        
        # Profile picture (placeholder)
        profile_pic = QLabel()
        profile_pic.setPixmap(QPixmap("default_profile.png").scaled(100, 100, Qt.KeepAspectRatio))
        profile_pic.setAlignment(Qt.AlignCenter)
        form_layout.addRow(profile_pic)

        # First Name
        self.first_name_input = QLineEdit()
        self.first_name_input.setText(employee_data["first_name"])
        form_layout.addRow("First Name*", self.first_name_input)

        # Last Name
        self.last_name_input = QLineEdit()
        self.last_name_input.setText(employee_data["last_name"])
        form_layout.addRow("Last Name*", self.last_name_input)

        # Identity Card
        self.carte_ident_input = QLineEdit()
        self.carte_ident_input.setText(employee_data["carte_ident"])
        form_layout.addRow("Carte Ident", self.carte_ident_input)

        # Telephone
        self.telephone_input = QLineEdit()
        self.telephone_input.setText(employee_data["telephone"])
        form_layout.addRow("Telephone", self.telephone_input)

        # Date of Birth
        self.date_naiss_input = QDateEdit()
        self.date_naiss_input.setCalendarPopup(True)
        self.date_naiss_input.setDate(QDate.fromString(employee_data["date_naiss"], "yyyy-MM-dd"))
        form_layout.addRow("Date of Birth", self.date_naiss_input)

        # Permission Role
        self.permission_role_input = QComboBox()
        self.permission_role_input.addItems(["super_employee", "employee", "Guest"])
        self.permission_role_input.setCurrentText(employee_data["permission_role"])
        form_layout.addRow("Permission Role", self.permission_role_input)

        # Add form to main layout
        main_layout.addLayout(form_layout)

        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)

        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.on_save_clicked)

        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)

    def on_save_clicked(self):
        """Check fields and accept if data is valid."""
        if not self.first_name_input.text() or not self.last_name_input.text():
            QMessageBox.warning(self, "Error", "Please fill in all required fields.")
            return

        # Accept the dialog if all fields are validated
        self.accept()

    def get_updated_data(self):
        """Return updated employee data from dialog fields."""
        return {
            "first_name": self.first_name_input.text(),
            "last_name": self.last_name_input.text(),
            "carte_ident": self.carte_ident_input.text(),
            "telephone": self.telephone_input.text(),
            "date_naiss": self.date_naiss_input.date().toString("yyyy-MM-dd"),
            "permission_role": self.permission_role_input.currentText(),
        }
