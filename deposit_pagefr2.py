from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QLabel,
)
from PyQt5.QtCore import Qt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from dialogs.add_deposit_dialog import AddDepositDialog
from database.models import (
    Customer,
    Deposit,
)
from database.database import SessionLocal
from dialogs.withdraw_deposit_dialog import WithdrawDepositDialog


class DepositPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Gestion des dépôts")
        self.setStyleSheet(self.load_stylesheet())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "Nom",
                "NNI",
                "Date de dépôt",
                "Montant initial",
                "Dépôt libéré",
                "Dette actuelle",
                "Actions",
            ]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        # Total Deposited Amount
        self.total_amount_label = QLabel("Total Déposé: 0")
        self.total_amount_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.total_amount_label, alignment=Qt.AlignLeft)

        # Add "Add Deposit" Button
        add_button = QPushButton("Ajouter un dépôt")
        add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_button.clicked.connect(self.add_deposit)
        layout.addWidget(add_button, alignment=Qt.AlignBottom | Qt.AlignRight)

        self.setLayout(layout)
        self.load_deposit_data()

        # After setting up the table headers
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Set the actions column to a fixed width
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 170)

        self.table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)

        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)

    def load_stylesheet(self):
        return """
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QTableWidget {
                border: 1px solid #ddd;
                background-color: #ffffff;
                alternate-background-color: #f5f5f5;
            }
            QTableWidget QHeaderView::section {
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                text-align: center;
            }
        """

    def load_deposit_data(self):
        session = SessionLocal()
        try:
            deposits = (
                session.query(Deposit)
                .join(Customer, Deposit.customer_id == Customer.id)
                .add_columns(
                    Customer.id,  # Include Customer.id in the columns
                    Customer.name,
                    Customer.identite,
                    Deposit.deposit_date,
                    Deposit.amount,
                    Deposit.released_deposit,
                    Deposit.current_debt,
                )
                .filter(Deposit.current_debt > 0)
                .all()
            )
            self.table.setRowCount(len(deposits))
            total_deposited = 0

            for row_idx, row in enumerate(deposits):
                (
                    customer_id,  # Extract Customer.id
                    customer_name,
                    identite,
                    deposit_date,
                    amount,
                    released_deposit,
                    current_debt,
                ) = row[
                    1:
                ]  # Adjust to include customer_id
                total_deposited += amount

                row_data = [
                    customer_name,
                    identite,
                    deposit_date.strftime("%Y-%m-%d"),
                    self.format_french_number(amount),
                    self.format_french_number(released_deposit),
                    self.format_french_number(current_debt),
                ]
                for col_idx, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)

                # Pass the extracted customer_id to the action buttons
                self.add_action_buttons(row_idx, customer_id)

            self.total_amount_label.setText(
                f"Total Déposé: {self.format_french_number(total_deposited)}"
            )

        except SQLAlchemyError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {str(e)}")
        finally:
            session.close()

    def add_action_buttons(self, row, customer_id):

        # Set the row height to accommodate the buttons
        self.table.setRowHeight(row, 50)  # Increased row height

        # Create a horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Adjust margins
        layout.setSpacing(6)  # Increase spacing between buttons

        # Withdraw button
        withdraw_button = QPushButton("Retirer")
        withdraw_button.setFixedSize(70, 35)
        withdraw_button.setStyleSheet(
            """
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """
        )
        withdraw_button.clicked.connect(lambda: self.withdraw(customer_id))

        # Add button
        add_button = QPushButton("Ajouter")
        add_button.setFixedSize(70, 35)
        add_button.setStyleSheet(
            """
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """
        )
        add_button.clicked.connect(lambda: self.update_deposit(customer_id))

        # Add buttons to layout
        layout.addWidget(withdraw_button)
        layout.addWidget(add_button)

        # Create container widget
        button_widget = QWidget()
        button_widget.setLayout(layout)

        # Adjust the column width to better fit the buttons
        self.table.setColumnWidth(6, 170)  # Adjust the width of the actions column

        # Add the button widget to the table cell
        self.table.setCellWidget(row, 6, button_widget)

    def add_deposit(self):
        dialog = AddDepositDialog()
        if dialog.exec_():

            self.load_deposit_data()  # Reload data after adding
            # self.save_ids_to_file()  # Save IDs to file

    def update_deposit(self, customer_id):
        dialog = AddDepositDialog(customer_id=customer_id)
        if dialog.exec_():

            self.load_deposit_data()

    def withdraw(self, identite):

        dialog = WithdrawDepositDialog(identite)
        if dialog.exec_():
            self.load_deposit_data()

    def format_french_number(self, amount):
        # Convert the number to a string with 2 decimal places
        integer_part, decimal_part = f"{amount:.2f}".split(".")
        # Add spaces or periods as group separators
        integer_part = " ".join(
            [integer_part[max(i - 3, 0) : i] for i in range(len(integer_part), 0, -3)][
                ::-1
            ]
        )
        # Combine integer part with the decimal part
        return f"{integer_part},{decimal_part}"
