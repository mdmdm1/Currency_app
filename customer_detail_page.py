import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QFrame, QSizePolicy, QDialog)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt
class CustomerDebtWindow(QDialog):
    def __init__(self, customer, debts):
        super().__init__()

        # Vérifiez que 'customers' est une liste
        #if not isinstance(, list) or not all(isinstance(c, Customer) for c in customers):
        #    raise ValueError("customers doit être une liste d'instances de Customer")
        self.customers = customer
        self.debts = debts
        self.setWindowTitle("Profiles de Dettes des Clients")
        self.setGeometry(200, 100, 800, 600)

        # Stylesheet global avec un design modernisé
        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #2c3e50;
            }
            QLabel#Username {
                font-size: 30px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 10px;
            }
            QLabel#UserDebtLabel {
                font-size: 18px;
                font-weight: bold;
                color: #16a085;
                margin-top: 10px;
            }
            QLabel#UserDebtAmount {
                font-size: 24px;
                color: #e74c3c;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#PayButton {
                background-color: #e67e22;
                font-size: 16px;
            }
            QPushButton#PayButton:hover {
                background-color: #d35400;
            }
            QTableWidget {
                border: 1px solid #ecf0f1;
                background-color: #ffffff;
                font-size: 14px;
                color: #2c3e50;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout()

        # Section d'en-tête avec les informations des clients
        #for customer in customer:
        self.add_customer_info(main_layout, customer)
        self.setLayout(main_layout)
    def add_customer_info(self, layout, customer):
        # Informations du client
        header_layout = QVBoxLayout()
        header_card = QFrame()
        header_layout.addWidget(header_card)

        header_card_layout = QHBoxLayout(header_card)

        # Image du profil
        profile_image = QLabel(self)
        pixmap = QPixmap("user_image.png")
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        profile_image.setPixmap(pixmap)
        profile_image.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        customer_info_layout = QVBoxLayout()
        customer_name = QLabel(customer.name)
        customer_name.setObjectName("Username")
        customer_identite = QLabel(f"Identité: {customer.identite}")
        customer_telephone = QLabel(f"Téléphone: {customer.telephone}")
        customer_birthdate = QLabel(f"Date de naissance: {customer.date_naiss}")

        customer_info_layout.addWidget(customer_name)
        customer_info_layout.addWidget(customer_identite)
        customer_info_layout.addWidget(customer_telephone)
        customer_info_layout.addWidget(customer_birthdate)

        header_card_layout.addWidget(profile_image)
        header_card_layout.addLayout(customer_info_layout)

        layout.addLayout(header_layout)

        # Section pour afficher les dettes
        debt_layout = QVBoxLayout()
        debt_card = QFrame()
        debt_layout.addWidget(debt_card)

        debt_card_layout = QHBoxLayout(debt_card)

        debt_info_layout = QVBoxLayout()
        debt_label = QLabel("Montant de la Dette")
        debt_label.setObjectName("UserDebtLabel")
        #debt_amount = QLabel(f"${debt.amount}")
       # debt_amount.setObjectName("UserDebtAmount")

        debt_info_layout.addWidget(debt_label)
        #debt_info_layout.addWidget(debt_amount)

        pay_button = QPushButton("Pay Now")
        pay_button.setObjectName("PayButton")
        debt_card_layout.addWidget(pay_button)

        layout.addLayout(debt_layout)

        # Section pour afficher les transactions dans un tableau
        transactions_label = QLabel("Historique des Transactions")
        transactions_label.setFont(QFont("Arial", 16))
        layout.addWidget(transactions_label) 
        transaction_table = QTableWidget()
        transaction_table.setRowCount(5)
        transaction_table.setColumnCount(4)
        transaction_table.setHorizontalHeaderLabels(["Date de Dette", "Montant Payé", "Dette Courante", "Nom"])
        # Définir le nombre de lignes basé sur le nombre de dettes
        transaction_table.setRowCount(len(self.debts))

        # Remplir le tableau avec les données de chaque dette
        for row, debt in enumerate(self.debts):
            transaction_table.setItem(row, 0, QTableWidgetItem(debt.debt_date))
            transaction_table.setItem(row, 1, QTableWidgetItem(f"${debt.paid_debt}"))
            transaction_table.setItem(row, 2, QTableWidgetItem(f"${debt.current_debt}"))
            transaction_table.setItem(row, 3, QTableWidgetItem(customer.name))
            
        layout.addWidget(transaction_table)

        # Section pour afficher les autres informations
        additional_info_label = QLabel("Informations Supplémentaires")
        additional_info_label.setFont(QFont("Arial", 16))
        layout.addWidget(additional_info_label)

        additional_info_table = QTableWidget()
        additional_info_table.setRowCount(4)
        additional_info_table.setColumnCount(2)
        additional_info_table.setHorizontalHeaderLabels(["Champ", "Valeur"])

        #additional_info_table.setItem(0, 0, QTableWidgetItem("Client ID"))
        #additional_info_table.setItem(0, 1, QTableWidgetItem(customer.customer_id))
        for debt in self.debts:
            additional_info_table.setItem(1, 0, QTableWidgetItem("Créé Par"))
            additional_info_table.setItem(1, 1, QTableWidgetItem(debt.created_by))
            additional_info_table.setItem(2, 0, QTableWidgetItem("Créé le"))
            additional_info_table.setItem(2, 1, QTableWidgetItem(debt.created_at))
            additional_info_table.setItem(3, 0, QTableWidgetItem("Mis à Jour Par"))
            additional_info_table.setItem(3, 1, QTableWidgetItem(debt.updated_by))

        layout.addWidget(additional_info_table)

