from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton


class SidebarWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #3498db;")  # Blue color for the sidebar
        self.setFixedWidth(200)  # Fixed width for sidebar

        # Layout for sidebar buttons
        sidebar_layout = QVBoxLayout(self)

        # Add profile image (optional)
        self.add_profile_image(sidebar_layout)

        # Create sidebar buttons
        btn_home = self.create_sidebar_button("Accueil", "🏠")
        btn_currency_management = self.create_sidebar_button("Devises", "💱")
        btn_money_management = self.create_sidebar_button("Transactions", "💰")
        btn_debt = self.create_sidebar_button("Dette", "📝")
        btn_deposit = self.create_sidebar_button("Dépôt", "🏦")
        btn_employee = self.create_sidebar_button("Mangement", "🏦")
        btn_signout = self.create_sidebar_button("Déconnexion", "🔌")

        # Add buttons to the sidebar layout
        sidebar_layout.addWidget(btn_home)
        sidebar_layout.addWidget(btn_currency_management)
        sidebar_layout.addWidget(btn_money_management)
        sidebar_layout.addWidget(btn_debt)
        sidebar_layout.addWidget(btn_deposit)
        sidebar_layout.addWidget(btn_employee)
        sidebar_layout.addStretch()  # Adds space at the bottom
        sidebar_layout.addWidget(btn_signout)

        self.buttons = {
            "home": btn_home,
            "currency": btn_currency_management,
            "money": btn_money_management,
            "debt": btn_debt,
            "deposit": btn_deposit,
            "employee": btn_employee,
            "signout": btn_signout,
        }

    def add_profile_image(self, layout):
        """Adds a circular profile image to the sidebar."""
        # Add profile image
        pass

    def create_sidebar_button(self, text, icon):
        """Create a button for the sidebar with icon and text."""
        button = QPushButton(f"{icon}  {text}")
        button.setFixedHeight(40)
        return button
