from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt

class DebtManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui(parent)

    def init_ui(self, parent):
        # Appliquer un style global
        self.setLayoutDirection(Qt.RightToLeft)
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
                background-color: #f44336;  /* Couleur de fond différente */
                color: white;
                border-radius: 5px;        /* Bordure plus petite */
                padding: 10px;             /* Moins de padding */
                font-size: 16px;           /* Taille de police différente */
                min-width: 150px;          /* Largeur minimale plus petite */
                min-height: 50px;          /* Hauteur minimale plus petite */
            }
            QPushButton#backButton:hover {
                background-color: #c62828;  /* Couleur de fond lors du survol */
            }
            QPushButton#backButton:pressed {
                background-color: #b71c1c;  /* Couleur de fond lors du clic */
            }
        """)

        # Layout principal vertical
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)  # Centrer le contenu verticalement

        # Titre de la page
        self.title_label = QLabel('إدارة الديون')
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        # Layout pour les boutons verticalement
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)  # Centrer les boutons verticalement dans le layout des boutons

        # Boutons
        self.button_debt_management = QPushButton('إدارة الديون')
        self.button_deposit_management = QPushButton('إدارة الودائع')
        self.button_back = QPushButton('العودة')  # Bouton de retour

        # Définir un nom d'objet pour le bouton de retour
        self.button_back.setObjectName('backButton')

        # Connecter les boutons aux pages correspondantes
        self.button_debt_management.clicked.connect(lambda: parent.stacked_widget.setCurrentWidget(parent.debt_page))
        self.button_deposit_management.clicked.connect(lambda: parent.stacked_widget.setCurrentWidget(parent.deposit_page))
        self.button_back.clicked.connect(lambda: parent.stacked_widget.setCurrentWidget(parent.home_page))  # Retour à la page d'accueil

        # Ajouter les boutons au layout
        button_layout.addWidget(self.button_debt_management)
        button_layout.addWidget(self.button_deposit_management)
        button_layout.addWidget(self.button_back)  # Ajouter le bouton de retour

        # Ajouter un espacement flexible avant et après le layout des boutons
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addLayout(button_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Configurer le layout du QWidget
        self.setLayout(main_layout)
