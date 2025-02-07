from pathlib import Path
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
    QDialog,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from dialogs.add_debt_dialog import AddDebtDialog
from utils.language_switcher import LanguageSwitcher
from pages.home_page import HomePage
from pages.currency_page import CurrencyPage
from pages.exchange_page import CurrencyExchangePage
from pages.debt_page import DebtPage
from pages.deposit_page import DepositPage
from pages.login_page import LoginPage
from pages.user_management_page import UserManagementPage
from database.database import SessionLocal
from database.models import User
from utils.translation_manager import TranslationManager
from utils.verify_admin import is_user_admin


class MainWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.is_admin = is_user_admin(user_id)
        self.active_button = None
        # Define icons directory
        self.icons_dir = Path(__file__).parent / "icons"

        # Initialize translation manager using same instance
        self.translation_manager = TranslationManager()

        # self.translation_manager.load_language("fr")

        self.setup_language_switcher()

        # Initialize pages
        self.pages = {
            "home": HomePage(self),
            "currency": CurrencyPage(self),
            "transactions": CurrencyExchangePage(self),
            "debt": DebtPage(self),
            "deposit": DepositPage(self),
            # "add_debt": AddDebtDialog(self),
        }

        if self.is_admin:
            self.pages["employees"] = UserManagementPage(self)

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("GestiFin Pro")
        self.setGeometry(95, 60, 1200, 650)

        # Set window icon
        icon_path = self.icons_dir / "icons" / "app_icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create and setup sidebar
        self.setup_sidebar(main_layout)

        # Setup main content area
        self.setup_main_content(main_layout)

        # Load stylesheet
        # self.load_stylesheet("style.css")

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
        username_label = QLabel(
            TranslationManager.tr("Bienvenue, ") + TranslationManager.tr(str(username))
        )
        username_label.setAlignment(Qt.AlignCenter)
        username_label.setObjectName("username-label")

        profile_layout.addWidget(profile_image)
        profile_layout.addWidget(username_label)
        sidebar_layout.addWidget(profile_frame)

        # Navigation buttons with icons
        nav_buttons = [
            (TranslationManager.tr("Accueil"), "home.svg", self.show_home),
            (TranslationManager.tr("Devises"), "currency.svg", self.show_currency),
            (TranslationManager.tr("Échanges"), "exchange.svg", self.show_transactions),
            (TranslationManager.tr("Dette"), "debt.svg", self.show_debt),
            (TranslationManager.tr("Dépôt"), "deposit.svg", self.show_deposit),
        ]

        if self.is_admin:
            nav_buttons.append(
                (
                    TranslationManager.tr("Gestion des employés"),
                    "users.svg",
                    self.show_employees,
                )
            )

        # Create navigation buttons
        self.nav_button_group = []
        for text, icon_name, slot in nav_buttons:
            btn = QPushButton(text)
            btn.setObjectName("nav-button")

            # Set icon
            icon_path = self.icons_dir / icon_name
            if icon_path.exists():
                btn.setIcon(QIcon(str(icon_path)))

            btn.clicked.connect(
                lambda checked, b=btn, s=slot: self.handle_nav_click(b, s)
            )
            sidebar_layout.addWidget(btn)
            self.nav_button_group.append(btn)

        # Add language switcher before logout button
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.language_switcher)

        # Logout button
        logout_btn = QPushButton(TranslationManager.tr("Logout"))
        # Logout button icon
        sidebar_layout.addStretch()
        logout_btn = QPushButton(TranslationManager.tr("Déconnexion"))
        logout_btn.setObjectName("logout-button")
        logout_icon_path = self.icons_dir / "logout.svg"
        if logout_icon_path.exists():
            logout_btn.setIcon(QIcon(str(logout_icon_path)))
        logout_btn.clicked.connect(self.sign_out)
        sidebar_layout.addWidget(logout_btn)

        main_layout.addWidget(sidebar)

    def handle_nav_click(self, button, slot):
        """Handle navigation button clicks"""
        # Update active state for all buttons
        for btn in self.nav_button_group:
            btn.setProperty("active", btn == button)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Call the navigation slot
        slot()

    def retranslate_ui(self):
        """Update all UI texts when language changes"""
        print("Retranslating UI...")
        tr = TranslationManager.tr

        # Update window title
        self.setWindowTitle(tr("GestiFin Pro"))

        # Recreate nav buttons with translated text
        nav_button_data = [
            (tr("Accueil"), "home.svg", self.show_home),
            (tr("Devises"), "currency.svg", self.show_currency),
            (tr("Échanges"), "exchange.svg", self.show_transactions),
            (tr("Dette"), "debt.svg", self.show_debt),
            (tr("Dépôt"), "deposit.svg", self.show_deposit),
        ]

        if self.is_admin:
            nav_button_data.append(
                (tr("Gestion des employés"), "users.svg", self.show_employees)
            )

        # Recreate navigation buttons
        for i, (text, icon_name, slot) in enumerate(nav_button_data):
            btn = self.nav_button_group[i]
            btn.setText(text)

        # Update logout button
        logout_btn = self.findChild(QPushButton, "logout-button")
        if logout_btn:
            logout_btn.setText(tr("Déconnexion"))

        # Update username label
        username = self.get_user_name(self.user_id)
        username_label = self.findChild(QLabel, "username-label")
        if username_label:
            username_label.setText(tr("Bienvenue, ") + username)

        # Update all pages
        for page in self.pages.values():
            if hasattr(page, "retranslate_ui"):
                page.retranslate_ui()

        # Set layout direction based on language
        if self.translation_manager.current_language == "ar":
            self.setLayoutDirection(Qt.RightToLeft)
            # Propagate to all child widgets
            for child in self.findChildren(QWidget):
                child.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)
            for child in self.findChildren(QWidget):
                child.setLayoutDirection(Qt.LeftToRight)

    def setup_language_switcher(self):
        """Initialize the language switcher"""
        self.language_switcher = LanguageSwitcher(self.translation_manager, self)

        self.language_switcher.language_changed.connect(self.retranslate_ui)

    """
    def on_language_changed(self, lang_code):
        print(f"Language changed to: {lang_code}")
        self.retranslate_ui()
    """

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


def load_stylesheet():

    with open("style.css", "r") as file:
        return file.read()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    translation_manager = TranslationManager(app)

    # Load and apply the stylesheet
    stylesheet = load_stylesheet()
    app.setStyleSheet(stylesheet)
    # Set the application icon
    icons_dir = Path(__file__).parent / "icons"
    icon_path = icons_dir / "app-icon.png"

    if icon_path.exists():
        app_icon = QIcon(str(icon_path))
        app.setWindowIcon(app_icon)
    else:
        print(f"Warning: Application icon not found at {icon_path}")

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
