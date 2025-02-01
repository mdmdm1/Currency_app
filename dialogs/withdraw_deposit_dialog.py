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

from utils.translation_manager import TranslationManager
from utils.audit_logger import log_audit_entry


class WithdrawDepositDialog(BaseDialog):
    def __init__(self, parent, customer_id):
        super().__init__(TranslationManager.tr("Withdrawal"), parent)
        self.setGeometry(250, 250, 300, 400)
        self.user_id = parent.user_id
        self.customer_id = customer_id

    def create_form_fields(self):
        # Input for withdrawal amount
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText(
            TranslationManager.tr("Amount to withdraw")
        )
        self.amount_input.setValidator(
            QDoubleValidator(0, 1e9, 2)
        )  # Allow only valid numeric input
        self.create_input_row(TranslationManager.tr("Amount:"), self.amount_input)

        # Input for withdrawal date
        self.withdraw_date_input = QDateEdit(QDate.currentDate())
        self.withdraw_date_input.setCalendarPopup(True)
        self.create_input_row(
            TranslationManager.tr("Withdrawal Date:"), self.withdraw_date_input
        )

    def on_submit(self):
        # Validate withdrawal amount
        amount_valid, amount = self.validate_amount(self.amount_input.text())
        if not amount_valid:
            return

        # Validate if an amount is specified
        if amount <= 0:
            self.show_error(
                TranslationManager.tr("The amount must be greater than zero.")
            )
            return

        try:
            session = SessionLocal()

            deposit = (
                session.query(Deposit).filter_by(customer_id=self.customer_id).first()
            )
            customer = session.query(Customer).filter_by(id=self.customer_id).first()
            # Check if the customer has sufficient balance
            if deposit.current_debt < amount:
                self.show_error(
                    TranslationManager.tr("Insufficient balance for withdrawal.")
                )
                return

            old_data = {
                TranslationManager.tr("Name"): customer.name,
                TranslationManager.tr("Released Deposit"): deposit.released_deposit,
                TranslationManager.tr("Current Debt"): deposit.current_debt,
            }

            # Deduct the amount and save changes
            deposit.current_debt -= amount
            deposit.released_deposit += amount

            # Log audit entry
            log_audit_entry(
                db_session=session,
                table_name=TranslationManager.tr("Deposit"),
                operation=TranslationManager.tr("WITHDRAW"),
                record_id=deposit.id,
                user_id=self.user_id,
                changes={
                    "old": old_data,
                    "new": {
                        TranslationManager.tr("Name"): customer.name,
                        TranslationManager.tr(
                            "Released Deposit"
                        ): deposit.released_deposit,
                        TranslationManager.tr("Current Debt"): deposit.current_debt,
                    },
                },
            )
            # if current_debt is 0, delete the deposit
            if deposit.current_debt == 0:
                session.delete(deposit)

            # commit changes to the database
            session.commit()

            # Inform the user of success
            QMessageBox.information(
                self,
                TranslationManager.tr("Success"),
                TranslationManager.tr("Withdrawal completed successfully."),
            )

            self.accept()

        except SQLAlchemyError as e:
            session.rollback()
            self.show_error(
                f"{TranslationManager.tr('Error accessing the database:')} {str(e)}"
            )
        finally:
            session.close()
