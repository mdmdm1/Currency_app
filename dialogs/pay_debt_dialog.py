from datetime import datetime
from PyQt5.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
from database.models import Customer, Debt
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError


class PayDebtDialog(BaseDialog):
    def __init__(self, debt_id, parent=None):
        super().__init__("Payer une dette", parent)
        self.debt_id = debt_id
        self.setGeometry(200, 200, 500, 400)
        # self.create_form_fields()
        self.populate_form_fields()

    def create_form_fields(self):
        self.current_debt_label = QLabel("0.00")
        self.pay_amount_input = QLineEdit()

        fields = [
            ("Dette actuelle:", self.current_debt_label),
            ("Montant à payer:", self.pay_amount_input),
        ]

        for label, widget in fields:
            self.create_input_row(label, widget)

    def populate_form_fields(self):
        session = SessionLocal()
        try:
            debt = session.query(Debt).filter_by(id=self.debt_id).first()
            if not debt:
                QMessageBox.critical(self, "Erreur", "Dette introuvable.")
                self.reject()
                return

            # Display the current debt amount
            # current_debt =
            self.current_debt_label.setText(
                self.format_french_number(debt.current_debt)
            )

        except SQLAlchemyError as e:
            QMessageBox.critical(
                self, "Erreur", f"Erreur lors du chargement des données: {str(e)}"
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
                QMessageBox.critical(self, "Erreur", "Dette introuvable.")
                return

            if pay_amount > debt.current_debt:
                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Le montant payé ne peut pas dépasser la dette actuelle.",
                )
                return

            # Update debt fields
            debt.paid_debt = (debt.paid_debt or 0) + pay_amount
            debt.current_debt = debt.amount - debt.paid_debt
            debt.updated_at = datetime.now()

            session.commit()

            QMessageBox.information(
                self,
                "Succès",
                f"La dette a été mise à jour avec succès:\n"
                f"Dette actuelle: {debt.current_debt:.2f}\n"
                f"Montant payé: {debt.paid_debt:.2f}",
            )
            self.accept()

        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Erreur SQLAlchemy: {str(e)}")
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
            QMessageBox.warning(None, "Erreur", "Veuillez entrer un montant valide.")
            return False, 0.0
