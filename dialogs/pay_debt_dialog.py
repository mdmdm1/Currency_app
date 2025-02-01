from datetime import datetime
from PyQt5.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
from database.models import Customer, Debt
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError

from utils.translation_manager import TranslationManager
from utils.audit_logger import log_audit_entry


class PayDebtDialog(BaseDialog):
    def __init__(self, parent, debt_id):
        super().__init__(TranslationManager.tr("Pay Debt"), parent)
        self.debt_id = debt_id
        self.user_id = parent.user_id
        self.setGeometry(200, 200, 500, 400)
        self.populate_form_fields()

    def create_form_fields(self):
        self.current_debt_label = QLabel("0.00")
        self.pay_amount_input = QLineEdit()

        fields = [
            (TranslationManager.tr("Current Debt:"), self.current_debt_label),
            (TranslationManager.tr("Amount to Pay:"), self.pay_amount_input),
        ]

        for label, widget in fields:
            self.create_input_row(label, widget)

    def populate_form_fields(self):
        session = SessionLocal()
        try:
            debt = session.query(Debt).filter_by(id=self.debt_id).first()
            if not debt:
                QMessageBox.critical(
                    self,
                    TranslationManager.tr("Error"),
                    TranslationManager.tr("Debt not found."),
                )
                self.reject()
                return

            # Display the current debt amount
            self.current_debt_label.setText(
                self.format_french_number(debt.current_debt)
            )

        except SQLAlchemyError as e:
            QMessageBox.critical(
                self,
                TranslationManager.tr("Error"),
                TranslationManager.tr("Error loading data:") + f" {str(e)}",
            )
            self.reject()
        finally:
            session.close()

    def on_submit(self):
        pay_amount_str = self.pay_amount_input.text().strip()

        is_valid_amount, pay_amount = self.validate_amount(pay_amount_str)

        if not is_valid_amount:
            return

        session = SessionLocal()
        try:
            debt = session.query(Debt).filter_by(id=self.debt_id).first()

            if not debt:
                QMessageBox.critical(
                    self,
                    TranslationManager.tr("Error"),
                    TranslationManager.tr("Debt not found."),
                )
                return

            customer = session.query(Customer).filter_by(id=debt.customer_id).first()
            if pay_amount > debt.current_debt:
                QMessageBox.warning(
                    self,
                    TranslationManager.tr("Error"),
                    TranslationManager.tr(
                        "The paid amount cannot exceed the current debt."
                    ),
                )
                return

            old_data = {
                "name": customer.name,
                "Paid Debt": debt.paid_debt,
                "Current Debt": debt.amount,
            }
            # Update debt fields
            debt.paid_debt = (debt.paid_debt or 0) + pay_amount
            debt.current_debt = debt.amount - debt.paid_debt
            debt.updated_at = datetime.now()

            session.commit()

            # Log audit entry
            log_audit_entry(
                db_session=session,
                table_name="Debt",
                operation="PAY",
                record_id=debt.id,
                user_id=self.user_id,
                changes={
                    "old": old_data,
                    "new": {
                        "name": customer.name,
                        "Paid Debt": debt.paid_debt,
                        "Current Debt": debt.amount,
                    },
                },
            )
            QMessageBox.information(
                self,
                TranslationManager.tr("Success"),
                TranslationManager.tr("The debt has been successfully updated:")
                + "\n"
                + TranslationManager.tr("Current Debt:")
                + f" {debt.current_debt:.2f}\n"
                + TranslationManager.tr("Paid Amount:")
                + f" {debt.paid_debt:.2f}",
            )
            self.accept()

        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(
                self,
                TranslationManager.tr("Error"),
                TranslationManager.tr("SQLAlchemy Error:") + f" {str(e)}",
            )
        finally:
            session.close()

    @staticmethod
    def validate_amount(amount_str):
        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError
            return True, amount
        except ValueError:
            QMessageBox.warning(
                None,
                TranslationManager.tr("Error"),
                TranslationManager.tr("Please enter a valid amount."),
            )
            return False, 0.0
