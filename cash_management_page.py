from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class CashManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui(parent)

    def init_ui(self, parent):
        # Appliquer un style global
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
            }
            QLabel {
                font-family: 'Arial', sans-serif;
                font-size: 30px;
                font-weight: bold;
                color: #444;
                padding: 20px;
                margin-bottom: 30px;
                background-color: #ffffff;
                border-radius: 12px;
                border: 2px solid #e0e0e0;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
            QPushButton#backButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                min-width: 150px;
                min-height: 50px;
            }
            QPushButton#backButton:hover {
                background-color: #c62828;
            }
            QPushButton#backButton:pressed {
                background-color: #b71c1c;
            }
        """)

        # Layout principal vertical
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)  # Centrer le contenu verticalement

        # Ajouter l'en-tête
        header_label = QLabel('إدارة الخزينة')
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)

        # Layout pour les boutons
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        # Boutons
        self.button_currency_management = QPushButton('إدارة العملات')
        self.button_money_management = QPushButton('إدارة المال')
        self.button_back = QPushButton('العودة')
        self.button_back.setObjectName('backButton')

        self.button_currency_management.clicked.connect(lambda: parent.stacked_widget.setCurrentWidget(parent.currency_management_page))
        self.button_money_management.clicked.connect(lambda: parent.stacked_widget.setCurrentWidget(parent.money_management_page))
        self.button_back.clicked.connect(lambda: parent.stacked_widget.setCurrentWidget(parent.home_page))

        # Ajouter les boutons au layout
        button_layout.addWidget(self.button_currency_management)
        button_layout.addWidget(self.button_money_management)
        button_layout.addWidget(self.button_back)

        # Ajouter un espacement flexible avant et après le layout des boutons
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addLayout(button_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Configurer le layout du QWidget
        self.setLayout(main_layout)
