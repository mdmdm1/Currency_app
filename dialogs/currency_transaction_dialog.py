from dialogs.base_dialog import BaseDialog
from PyQt5.QtWidgets import QLineEdit, QDateEdit, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
from database.models import Customer, Deposit
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError


class CurrencyTransactionDialog(BaseDialog):
    def __init__(self, transaction_type, currency, parent=None):
        super().__init__(f"{transaction_type} de {currency}", parent)
        self.currency = currency
        self.transaction_type = transaction_type

    def create_form_fields(self):
        # Amount field
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.create_input_row("Montant:", self.amount_input)

        # Date field
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.create_input_row("Date:", self.date_input)

        # Note field
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Note (optionnel)")
        self.create_input_row("Note:", self.note_input)

    def on_submit(self):
        amount_text = self.amount_input.text().replace(" ", "").replace(",", ".")
        valid, amount = self.validate_amount(amount_text)

        if not valid:
            return

        # TODO: Add your database transaction logic here

        self.accept()
