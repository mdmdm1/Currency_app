from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QDialog, QLabel, QPushButton,
    QDateEdit, QComboBox, QCheckBox, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap
import hashlib  # Pour générer le hash du mot de passe

class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Add Employee")
        self.setFixedSize(500, 600)  # Taille augmentée pour inclure plus de champs

        # Style général pour l'interface
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
            QPushButton#nextButton {
                background-color: #4CAF50;
                color: white;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Formulaire
        form_layout = QFormLayout()
        
        # Image de profil
        profile_pic = QLabel()
        profile_pic.setPixmap(QPixmap("default_profile.png").scaled(100, 100, Qt.KeepAspectRatio))
        profile_pic.setAlignment(Qt.AlignCenter)
        form_layout.addRow(profile_pic)

        # Champs de saisie pour prénom et nom
        self.first_name_input = QLineEdit()
        form_layout.addRow("First Name*", self.first_name_input)

        self.last_name_input = QLineEdit()
        form_layout.addRow("Last Name*", self.last_name_input)

        self.carte_ident_input = QLineEdit()
        form_layout.addRow("Carte Ident", self.carte_ident_input)

        self.telephone_input = QLineEdit()
        form_layout.addRow("Telephone", self.telephone_input)

        self.date_naiss_input = QDateEdit()
        self.date_naiss_input.setCalendarPopup(True)
        self.date_naiss_input.setDate(QDate.currentDate())
        form_layout.addRow("Date of Birth", self.date_naiss_input)

        # Champ de mot de passe et confirmation
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password*", self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Confirm Password*", self.confirm_password_input)

        self.permission_role_input = QComboBox()
        self.permission_role_input.addItems(["super_employee", "employee", "Guest"])
        form_layout.addRow("Permission Role", self.permission_role_input)

        # Ajout du formulaire principal au layout principal
        main_layout.addLayout(form_layout)

        # Boutons en bas
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        self.next_button = QPushButton("Next")
        self.next_button.setObjectName("nextButton")
        self.next_button.clicked.connect(self.on_next_clicked)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.next_button)
        
        main_layout.addLayout(button_layout)

    def on_next_clicked(self):
        """Vérifie les mots de passe et affiche un message d'erreur si nécessaire."""
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if not self.first_name_input.text() or not self.last_name_input.text():
            QMessageBox.warning(self, "Error", "Please fill in all required fields.")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        
        # Générer le hash du mot de passe
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Affiche un message de succès (ou passe aux étapes suivantes)
        QMessageBox.information(self, "Success", f"Password Hash: {password_hash}")
        self.accept()  # Pour fermer la fenêtre après le succès
