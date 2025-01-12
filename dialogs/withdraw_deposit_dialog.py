from PyQt5.QtWidgets import (
    QLineEdit,
    QWidget,
    QDateEdit,
    QLabel,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QDoubleValidator
from database.models import Customer, Deposit
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError

from utils.audit_logger import log_audit_entry


class WithdrawDepositDialog(BaseDialog):
    def __init__(self, parent, customer_id):
        super().__init__("Retrait", parent)
        self.setGeometry(250, 250, 300, 400)
        self.user_id = parent.user_id
        self.customer_id = customer_id

    def create_form_fields(self):
        # Input for withdrawal amount
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Montant à retirer")
        self.amount_input.setValidator(
            QDoubleValidator(0, 1e9, 2)
        )  # Allow only valid numeric input
        self.create_input_row("Montant:", self.amount_input)

        # Input for withdrawal date
        self.withdraw_date_input = QDateEdit(QDate.currentDate())
        self.withdraw_date_input.setCalendarPopup(True)
        self.create_input_row("Date de retrait:", self.withdraw_date_input)

    def on_submit(self):
        # Validate withdrawal amount
        amount_valid, amount = self.validate_amount(self.amount_input.text())
        if not amount_valid:
            return

        # Validate if an amount is specified
        if amount <= 0:
            self.show_error("Le montant doit être supérieur à zéro.")
            return

        try:
            # Database logic: deduct the amount from the customer's balance
            from sqlalchemy.orm import Session
            from sqlalchemy.exc import SQLAlchemyError
            from database.database import SessionLocal
            from database.models import Customer

            session = SessionLocal()

            deposit = (
                session.query(Deposit).filter_by(customer_id=self.customer_id).first()
            )
            customer = session.query(Customer).filter_by(id=self.customer_id).first()
            # Check if the customer has sufficient balance
            if deposit.current_debt < amount:
                self.show_error("Solde insuffisant pour effectuer ce retrait.")
                return

            old_data = {
                "nom": customer.name,
                "Depot libere": deposit.released_deposit,
                "dette actuelle": deposit.current_debt,
            }

            # Deduct the amount and save changes
            deposit.current_debt -= amount
            deposit.released_deposit += amount

            # Log audit entry
            log_audit_entry(
                db_session=session,
                table_name="Dépôt",
                operation="RETIRER",
                record_id=deposit.id,
                user_id=self.user_id,
                changes={
                    "old": old_data,
                    "new": {
                        "nom": customer.name,
                        "depot libere": deposit.released_deposit,
                        "dette courant": deposit.current_debt,
                    },
                },
            )
            # if current_debt is 0, delete the deposit
            if deposit.current_debt == 0:
                session.delete(deposit)

            # commit changes to the database
            session.commit()

            # Inform the user of success
            QMessageBox.information(self, "Succès", "Retrait effectué avec succès.")

            # Add any necessary logging or additional logic here
            # For example, record a transaction log if needed
            # Comment: Successfully updated the customer's balance in the database.

            self.accept()

        except SQLAlchemyError as e:
            session.rollback()
            self.show_error(f"Erreur lors de l'accès à la base de données: {str(e)}")
        finally:
            session.close()
