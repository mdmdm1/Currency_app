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
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.models import User
from pathlib import Path

from utils.language_switcher import LanguageSwitcher
from utils.translation_manager import TranslationManager


class LoginPage(QMainWindow):
    login_successful = pyqtSignal(object)

    def __init__(self, db_session: Session):
        super().__init__()
        self.db_session = db_session

        # Get existing TranslationManager instance instead of creating new one
        self.translation_manager = TranslationManager()

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

        # Username input with fallback icon
        self.username_container = self.create_input_with_fallback(
            placeholder=TranslationManager.tr("Nom d'utilisateur"),
            icon_name="user-icon.png",
            fallback_text="👤",
        )
        self.username_input = self.username_container.input_field
        layout.addWidget(self.username_container)

        # Password input with fallback icon
        self.password_container = self.create_input_with_fallback(
            placeholder=TranslationManager.tr("Mot de passe"),
            icon_name="lock-icon2.png",
            fallback_text="🔒",
            is_password=True,
        )
        self.password_input = self.password_container.input_field
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
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

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
        """
        )

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
            # Optimize database query by selecting only necessary fields
            stmt = select(User.id, User.password, User.is_active).where(
                User.username == username
            )
            result = self.db_session.execute(stmt).first()

            if not result:
                self.show_error(
                    TranslationManager.tr("Nom d'utilisateur ou mot de passe invalide.")
                )
                return

            user_id, hashed_password, is_active = result

            if not is_active:
                self.show_error(TranslationManager.tr("Ce compte a été désactivé."))
                return

            # Use a separate thread for password verification
            QApplication.processEvents()  # Keep UI responsive
            if not self.verify_password(password, hashed_password):
                self.show_error(
                    TranslationManager.tr("Nom d'utilisateur ou mot de passe invalide.")
                )
                return

            # Construct user object with minimal data
            user = User(id=user_id, username=username, is_active=is_active)
            self.login_successful.emit(user)
            self.close()

        except Exception as e:
            self.show_error(TranslationManager.tr("Erreur de connexion : ") + str(e))

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except Exception:
            return False

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
