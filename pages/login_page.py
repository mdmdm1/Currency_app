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

from database.models import AuditLog, User
from utils.audit_logger import log_audit_entry


class LoginPage(QMainWindow):
    login_successful = pyqtSignal(object)  # Signal to notify a successful login

    def __init__(self, db_session: Session):
        super().__init__()
        self.db_session = db_session
        self.setWindowTitle("Banque de Devises - Connexion")  # Window title in French
        self.setFixedSize(400, 500)
        self.setup_ui()
        self.center_on_screen()

    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # App title
        title = QLabel("Banque de Devises")  # French translation for "Currency Bank"
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
        subtitle = QLabel(
            "Bienvenue ! Veuillez vous connecter à votre compte."
        )  # French subtitle
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Add some spacing
        layout.addSpacing(20)

        # Username input
        username_container = self.create_input(
            placeholder="Nom d'utilisateur",
            icon_path="C:/Users/medma/Desktop/Currency_app/profile.png",
        )
        print(os.path.abspath("./pages/profile.png"))

        self.username_input = username_container.input_field  # Access the QLineEdit
        layout.addWidget(username_container)

        # Password input
        password_container = self.create_input(
            "Mot de passe", "lock.png", is_password=True
        )
        self.password_input = password_container.input_field  # Access the QLineEdit
        layout.addWidget(password_container)

        # Login button
        self.login_button = QPushButton("Connexion")  # French translation for "Login"
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

        # Status message
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Set window style
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

    def create_input(self, placeholder, icon_path, is_password=False):
        container = QFrame()
        container.setFixedHeight(50)

        # Create input field
        input_field = QLineEdit(container)
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedSize(320, 50)

        if is_password:
            input_field.setEchoMode(QLineEdit.Password)

        # Create icon
        icon = QLabel(container)
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            icon.setPixmap(
                pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            icon.setText("📷")  # Placeholder for missing icons
        icon.move(15, 15)

        # Store input_field in the container for access
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
                "Veuillez entrer le nom d'utilisateur et le mot de passe."
            )  # Error in French
            return

        try:
            stmt = select(User).where(User.username == username)
            user = self.db_session.execute(stmt).scalar_one_or_none()

            if not user or not self.verify_password(password, user.password):
                self.show_error(
                    "Nom d'utilisateur ou mot de passe invalide."
                )  # Error in French
                return

            if not user.is_active:
                self.show_error("Ce compte a été désactivé.")  # Error in French
                return

            """
            log_audit_entry(
                    db_session=self.db_session,
                    table_name="UTILISATEURS",
                    operation="CONNEXION",
                    record_id=user.id,
                    user_id=user.id,
                    changes="Connexion réussie",
                    
            )
            """

            self.login_successful.emit(user)  # Emit success signal
            self.close()  # Close the login window

        except Exception as e:
            self.show_error(f"Erreur de connexion : {str(e)}")  # Error in French

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except Exception:
            return False

    def show_error(self, message: str):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px;")
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))
