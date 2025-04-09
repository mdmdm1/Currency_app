import os
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QFrame,
    QApplication,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap
import bcrypt
import requests
from pathlib import Path

from utils.language_switcher import LanguageSwitcher
from utils.translation_manager import TranslationManager
from config import API_BASE_URL


class LoginPage(QMainWindow):
    login_successful = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        # Get existing TranslationManager instance
        self.translation_manager = TranslationManager()

        # API base URL
        self.api_base_url = API_BASE_URL
        self.setWindowTitle(TranslationManager.tr("GestiFin Pro - Connexion"))
        self.setFixedSize(400, 500)

        # Define resources directory
        self.icons_dir = Path(__file__).parent.parent / "icons"
        if not self.icons_dir.exists():
            self.icons_dir.mkdir(parents=True)

        self.setup_language_switcher()
        self.setup_ui()
        self.center_on_screen()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # App title
        title = QLabel("GestiFin Pro")
        title.setStyleSheet(
            """
            QLabel {
                color: #2c3e50;
                font-size: 28px;
                font-weight: bold;
            }
        """
        )
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        self.subtitle = QLabel(
            TranslationManager.tr("Bienvenue ! Veuillez vous connecter à votre compte.")
        )
        self.subtitle.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        self.subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitle)

        layout.addSpacing(20)

        # Username input
        self.username_container = self.create_input_with_fallback(
            placeholder=TranslationManager.tr("Nom d'utilisateur"),
            icon_name="user-icon.png",
            fallback_text="👤",
        )
        self.username_input = self.username_container.input_field
        self.username_input.returnPressed.connect(
            self.focus_password
        )  # Connect Enter key
        layout.addWidget(self.username_container)

        # Password input
        self.password_container = self.create_input_with_fallback(
            placeholder=TranslationManager.tr("Mot de passe"),
            icon_name="lock-icon2.png",
            fallback_text="🔒",
            is_password=True,
        )
        self.password_input = self.password_container.input_field
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_container)

        # Login button
        self.login_button = QPushButton(TranslationManager.tr("Connexion"))
        self.login_button.setFixedHeight(50)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2475a8;
            }
        """
        )
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        layout.addWidget(self.language_switcher)

        # Status message
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Add stretch to push the signature to the bottom
        layout.addStretch()

        # Company signature
        signature_label = QLabel("© 2025 ITDEVGiant")
        signature_label.setObjectName("signatureLabel")  # For styling
        signature_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(signature_label)

        # Window style
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f6fa;
            }
            QLineEdit {
                padding: 12px;
                padding-left: 45px;
                border: 2px solid #dcdde1;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            #signatureLabel {
                color: #7f8c8d;
                font-size: 12px;
            }
        """
        )

    def focus_password(self):
        self.password_input.setFocus()

    def create_input_with_fallback(
        self, placeholder, icon_name, fallback_text, is_password=False
    ):
        container = QFrame()
        container.setFixedHeight(50)
        container.setObjectName("login-container")

        # Create input field
        input_field = QLineEdit(container)
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedSize(320, 50)

        if is_password:
            input_field.setEchoMode(QLineEdit.Password)

        # Create icon with fallback
        icon = QLabel(container)
        icon_path = self.icons_dir / icon_name

        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                icon.setPixmap(
                    pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
            else:
                icon.setText(fallback_text)
        else:
            icon.setText(fallback_text)

        icon.move(15, 15)

        container.input_field = input_field
        return container

    def center_on_screen(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_error(
                TranslationManager.tr(
                    "Veuillez entrer le nom d'utilisateur et le mot de passe."
                )
            )
            return

        try:
            # Make API request to login endpoint
            response = requests.post(
                f"{self.api_base_url}/auth/login",
                json={"username": username, "password": password},
            )

            if response.status_code == 401:
                error_data = response.json()

                if error_data["detail"] == "Invalid username or password":
                    self.show_error(
                        TranslationManager.tr(
                            "Nom d'utilisateur ou mot de passe invalide."
                        )
                    )

                elif error_data["detail"] == "Account is disabled":
                    self.show_error(TranslationManager.tr("Ce compte a été désactivé."))
                return

            if response.status_code != 200:
                self.show_error(TranslationManager.tr("Erreur de connexion au serveur"))
                return

            # Parse response data
            user_data = response.json()

            # Create a simple user object with the required data
            class User:
                def __init__(self, id, username, is_active, access_token):
                    self.id = id
                    self.username = username
                    self.is_active = is_active
                    self.access_token = access_token

            user = User(
                id=user_data["id"],
                username=user_data["username"],
                is_active=user_data["is_active"],
                access_token=user_data["access_token"],
            )

            # Store the token for future API requests
            self.save_token(user_data["access_token"])

            self.login_successful.emit(user)
            self.close()

        except requests.RequestException as e:
            self.show_error(TranslationManager.tr("Erreur de connexion : ") + str(e))

    def save_token(self, token: str):
        """Save the authentication token for future use"""
        # You might want to store this more securely in a real application
        QApplication.instance().access_token = token

    def setup_language_switcher(self):
        """Initialize the language switcher"""
        self.language_switcher = LanguageSwitcher(self.translation_manager)
        self.language_switcher.language_changed.connect(self.retranslate_ui)

    def show_error(self, message: str):
        self.status_label.setText(message)
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))

    def retranslate_ui(self):
        """Update all UI texts when language changes"""
        tr = TranslationManager.tr

        self.setWindowTitle(tr("GestiFin Pro - Connexion"))
        self.subtitle.setText(tr("Bienvenue ! Veuillez vous connecter à votre compte."))
        self.username_container.input_field.setPlaceholderText(tr("Nom d'utilisateur"))
        self.password_container.input_field.setPlaceholderText(tr("Mot de passe"))
        self.login_button.setText(tr("Connexion"))

        # Clear any existing error message
        if self.status_label.text():
            current_error = self.status_label.text()
            # Translate common error messages
            if (
                current_error
                == "Veuillez entrer le nom d'utilisateur et le mot de passe."
            ):
                self.status_label.setText(
                    tr("Veuillez entrer le nom d'utilisateur et le mot de passe.")
                )
            elif current_error == "Nom d'utilisateur ou mot de passe invalide.":
                self.status_label.setText(
                    tr("Nom d'utilisateur ou mot de passe invalide.")
                )
            elif current_error == "Ce compte a été désactivé.":
                self.status_label.setText(tr("Ce compte a été désactivé."))
            elif current_error.startswith("Erreur de connexion : "):
                self.status_label.setText(
                    tr("Erreur de connexion : ") + current_error.split(": ", 1)[1]
                )
