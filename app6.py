import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from home_page import HomePage
from pages.currency_page import CurrencyPage
from pages.exchange_page import CurrencyExchangePage
from pages.debt_page import DebtPage
from pages.deposit_page import DepositPage
from pages.login_page import LoginPage
from pages.user_management_page import UserManagementPage
from database.database import SessionLocal
from database.models import User
from utils.verify_admin import is_user_admin


class MainWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.is_admin = is_user_admin(user_id)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("MoneyManagement")
        self.setGeometry(95, 90, 1200, 650)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create and setup sidebar
        self.setup_sidebar(main_layout)

        # Setup main content area
        self.setup_main_content(main_layout)

        # Load stylesheet
        self.load_stylesheet("style.css")

    def setup_sidebar(self, main_layout):
        """Setup the sidebar with navigation buttons"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)

        # Profile section
        profile_frame = QFrame()
        profile_frame.setObjectName("profile-frame")
        profile_layout = QVBoxLayout(profile_frame)

        # Profile image
        profile_image = QLabel()
        profile_pixmap = QPixmap("icons/profile.png").scaled(
            80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        profile_image.setPixmap(profile_pixmap)
        profile_image.setAlignment(Qt.AlignCenter)
        profile_image.setObjectName("profile-image")

        # Username label
        username = self.get_user_name(self.user_id)
        username_label = QLabel("Bienvenue, " + str(username))
        username_label.setAlignment(Qt.AlignCenter)
        username_label.setObjectName("username-label")

        profile_layout.addWidget(profile_image)
        profile_layout.addWidget(username_label)
        sidebar_layout.addWidget(profile_frame)

        # Navigation buttons
        nav_buttons = [
            ("🏠 Accueil", self.show_home),
            ("💱 Devises", self.show_currency),
            ("💰 Transactions", self.show_transactions),
            ("📝 Dette", self.show_debt),
            ("🏦 Dépôt", self.show_deposit),
        ]

        if self.is_admin:
            nav_buttons.append(("👥 Gestion des employés", self.show_employees))

        # Create navigation buttons
        for text, slot in nav_buttons:
            btn = QPushButton(text)
            btn.setObjectName("nav-button")
            btn.clicked.connect(slot)
            sidebar_layout.addWidget(btn)

        # Add logout button at the bottom
        sidebar_layout.addStretch()
        logout_btn = QPushButton("🔌 Déconnexion")
        logout_btn.setObjectName("logout-button")
        logout_btn.clicked.connect(self.sign_out)
        sidebar_layout.addWidget(logout_btn)

        main_layout.addWidget(sidebar)

    def setup_main_content(self, main_layout):
        """Setup the main content area"""
        self.stack = QStackedWidget()
        self.stack.setObjectName("main-content")

        # Initialize pages
        self.pages = {
            "home": HomePage(self),
            "currency": CurrencyPage(self),
            "transactions": CurrencyExchangePage(self),
            "debt": DebtPage(self),
            "deposit": DepositPage(self),
        }

        if self.is_admin:
            self.pages["employees"] = UserManagementPage(self)

        # Add pages to stack
        for page in self.pages.values():
            self.stack.addWidget(page)

        main_layout.addWidget(self.stack)

    # Navigation methods
    def show_home(self):
        self.stack.setCurrentWidget(self.pages["home"])

    def show_currency(self):
        self.stack.setCurrentWidget(self.pages["currency"])

    def show_transactions(self):
        self.stack.setCurrentWidget(self.pages["transactions"])

    def show_debt(self):
        self.stack.setCurrentWidget(self.pages["debt"])

    def show_deposit(self):
        self.stack.setCurrentWidget(self.pages["deposit"])

    def show_employees(self):
        if self.is_admin and "employees" in self.pages:
            self.stack.setCurrentWidget(self.pages["employees"])

    def sign_out(self):
        """Handle sign-out action"""
        self.close()
        self.login_page = LoginPage(SessionLocal())
        self.login_page.login_successful.connect(self.show_main_window)
        self.login_page.show()

    @staticmethod
    def get_user_name(user_id):
        session = SessionLocal()
        try:
            user = session.get(User, user_id)
            if not user:
                return False  # User not found

            return user.username
        except Exception as e:
            print(f"Error while getting the username: {e}")
            return False  # Return False in case of an error
        finally:
            session.close()

    @staticmethod
    def show_main_window(user):
        """Show main window after successful login"""
        main_window = MainWindow(user.id)
        main_window.show()

    def load_stylesheet(self, filename):
        """Load CSS stylesheet"""
        try:
            with open(filename, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Warning: Stylesheet {filename} not found")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_session = SessionLocal()  # Initialize your database session

    # Create and show the login page
    login_page = LoginPage(db_session)

    def show_main_window(user):
        """Callback to show the main window after login."""
        main_window = MainWindow(user.id)
        main_window.show()

    # Connect the login signal to the function
    login_page.login_successful.connect(show_main_window)
    login_page.show()

    sys.exit(app.exec_())
