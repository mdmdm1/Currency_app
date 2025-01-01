from PyQt5.QtWidgets import (
    QComboBox,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
    QLabel,
    QTableWidgetItem,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from database.models import Currency
from database.database import SessionLocal
from pages.base_page import BasePage


class CurrencyExchangePage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent, title="Currency Exchange")
        self.init_currency_exchange_ui()

    def init_currency_exchange_ui(self):
        """Initialize the currency exchange UI."""
        # Input fields
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        self.amount_input.setValidator(
            QDoubleValidator(0.0, 1e10, 2, notation=QDoubleValidator.StandardNotation)
        )

        self.source_currency_combo = QComboBox()
        self.target_currency_combo = QComboBox()

        # Buttons
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.perform_conversion)

        # Result Label
        self.result_label = QLabel("Result: ")
        self.result_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow("Amount:", self.amount_input)
        form_layout.addRow("From Currency:", self.source_currency_combo)
        form_layout.addRow("To Currency:", self.target_currency_combo)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.convert_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.result_label, alignment=Qt.AlignLeft)

        self.layout.addLayout(layout)

        self.load_currencies_from_db()

    def load_currencies_from_db(self):
        """Load currencies into the combo boxes and table from the database."""
        session = SessionLocal()
        try:

            # Fetch currencies from the database
            currencies = session.query(Currency).all()
            self.table.setRowCount(len(currencies))
            self.source_currency_combo.clear()
            self.target_currency_combo.clear()

            for row, currency in enumerate(currencies):
                # Populate table
                self.table.setItem(row, 0, QTableWidgetItem(currency.name))
                self.table.setItem(row, 1, QTableWidgetItem(currency.id))
                self.table.setItem(
                    row, 2, QTableWidgetItem(f"{currency.rate:.4f}")
                )  # Format rate to 4 decimal places

                # Populate combo boxes
                self.source_currency_combo.addItem(currency.id)
                self.target_currency_combo.addItem(currency.id)

        except Exception as e:
            self.show_error_message("Error", f"Failed to load currencies: {str(e)}")

    def perform_conversion(self):
        """Perform currency conversion based on user input."""
        session = SessionLocal()
        try:
            amount = float(self.amount_input.text())
            source_currency = self.source_currency_combo.currentText()
            target_currency = self.target_currency_combo.currentText()

            if source_currency == target_currency:
                self.result_label.setText("Result: Same currency selected")
                return

            # Fetch conversion rates from the database
            source_currency_obj = (
                session.query(Currency).filter_by(id=source_currency).first()
            )
            target_currency_obj = (
                session.query(Currency).filter_by(id=target_currency).first()
            )

            if not source_currency_obj or not target_currency_obj:
                self.show_error_message("Error", "Currency rates not found")
                return

            # Perform conversion
            converted_amount = (
                amount / source_currency_obj.rate * target_currency_obj.rate
            )
            self.result_label.setText(
                f"Result: {self.format_french_number(converted_amount)} {target_currency}"
            )
        except Exception as e:
            self.show_error_message("Error", f"Conversion failed: {str(e)}")
