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
    QLineEdit,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

# Importation des pages (assurez-vous que ces modules sont correctement définis dans votre projet)
from home_page import HomePage
from cash_management_page import CashManagementPage
from debt_management_page import DebtManagementPage

# from currency_management_page import CurrencyManagementPage
from pages.currency_page import CurrencyPage
from pages.exchange_page import CurrencyExchangePage

from money_management_page import MoneyManagementPage

# from debt_pagefr import DebtPage
from pages.debt_page import DebtPage

# from deposit_pagefr2 import DepositPage
from pages.deposit_page import DepositPage

# from employees_page import EmployeesManagementPage
from pages.login_page import LoginPage
from pages.user_management_page import UserManagementPage
from database.database import SessionLocal


class MainWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        # Configuration de la fenêtre principale
        self.setWindowTitle("Moneymanagement")
        self.setGeometry(100, 100, 1100, 600)

        # Layout principal horizontal
        main_layout = QHBoxLayout(self)

        # ---- Barre latérale ----
        sidebar = QFrame(self)
        sidebar.setStyleSheet(
            "background-color: #3498db;"
        )  # Couleur bleue pour la barre latérale
        sidebar.setFixedWidth(200)  # Largeur fixe pour la barre latérale

        # Layout de la barre latérale
        sidebar_layout = QVBoxLayout(sidebar)

        # Ajout de l'image circulaire en haut à gauche
        self.add_profile_image(sidebar_layout)

        # Création des boutons de la barre latérale
        btn_home = self.create_sidebar_button("Accueil", "🏠")
        btn_currency_management = self.create_sidebar_button("Devises", "💱")
        btn_money_management = self.create_sidebar_button("Transactions", "💰")
        btn_debt = self.create_sidebar_button("Dette", "📝")
        btn_deposit = self.create_sidebar_button("Dépôt", "🏦")
        btn_signout = self.create_sidebar_button("Déconnexion", "🔌")
        btn_employee = self.create_sidebar_button("Mangement ", "🏦")

        # Ajouter les boutons à la barre latérale
        sidebar_layout.addWidget(btn_home)
        sidebar_layout.addWidget(btn_currency_management)
        sidebar_layout.addWidget(btn_money_management)
        sidebar_layout.addWidget(btn_debt)
        sidebar_layout.addWidget(btn_deposit)
        sidebar_layout.addWidget(btn_employee)
        sidebar_layout.addStretch()  # Ajout d'un espace flexible pour pousser le bouton "Sign Out" en bas
        sidebar_layout.addWidget(btn_signout)

        # ---- Contenu principal (StackedWidget) ----
        self.stack = QStackedWidget(self)

        # Création des pages pour chaque section
        self.home_page = HomePage(self)
        self.currency_management_page = CurrencyPage(self)
        self.money_management_page = CurrencyExchangePage(self)
        self.debt_page = DebtPage(self)
        self.deposit_page = DepositPage(self)
        self.employee_page = UserManagementPage(self)

        # Ajouter les pages au QStackedWidget
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.currency_management_page)
        self.stack.addWidget(self.money_management_page)
        self.stack.addWidget(self.debt_page)
        self.stack.addWidget(self.deposit_page)
        self.stack.addWidget(self.employee_page)

        # Connecter les boutons aux pages
        btn_home.clicked.connect(lambda: self.stack.setCurrentWidget(self.home_page))
        btn_currency_management.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.currency_management_page)
        )
        btn_money_management.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.money_management_page)
        )
        btn_debt.clicked.connect(lambda: self.stack.setCurrentWidget(self.debt_page))
        btn_deposit.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.deposit_page)
        )
        btn_employee.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.employee_page)
        )

        # ---- Top Bar avec la barre de recherche et l'icône du profil ----
        top_layout = QHBoxLayout()
        search_bar = QLineEdit(self)
        search_bar.setPlaceholderText("Search...")
        search_bar.setFixedHeight(30)
        search_bar.setStyleSheet("padding: 5px; font-size: 16px;")
        search_bar.setFixedWidth(400)

        # Icône de profil à droite
        profile_icon = QLabel("👤", self)
        profile_icon.setAlignment(Qt.AlignRight)
        profile_icon.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        top_layout.addWidget(search_bar)
        top_layout.addWidget(profile_icon)

        # Layout pour la partie droite (barre de recherche + contenu)
        right_layout = QVBoxLayout()
        right_layout.addLayout(top_layout)
        right_layout.addWidget(self.stack)

        # Ajouter la barre latérale et le contenu principal au layout principal
        main_layout.addWidget(sidebar)
        main_layout.addLayout(right_layout)

        # Appliquer les styles
        self.load_stylesheet("style.css")

    def load_stylesheet(self, filename):
        """Charge une feuille de style CSS depuis un fichier."""
        with open(filename, "r") as f:
            self.setStyleSheet(f.read())

    def add_profile_image(self, layout):
        """Ajoute une image circulaire pour le profil."""
        profile_image = QLabel(self)
        profile_image.setPixmap(
            QPixmap("default_profile.png").scaled(
                50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        profile_image.setStyleSheet(
            "border-radius: 25px; margin: 10px;"
        )  # Style circulaire
        layout.addWidget(profile_image)

    def create_sidebar_button(self, text, icon):
        """Crée un bouton pour la barre latérale avec une icône et du texte."""
        button = QPushButton(f"{icon}  {text}")
        button.setFixedHeight(40)
        return button


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
