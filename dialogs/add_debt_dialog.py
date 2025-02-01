from datetime import datetime
from PyQt5.QtWidgets import QLineEdit, QDateEdit, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
from database.models import Customer, Debt
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError

from utils.translation_manager import TranslationManager
from utils.audit_logger import log_audit_entry


class AddDebtDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(TranslationManager.tr("Ajouter une dette"), parent)
        self.user_id = parent.user_id
        self.setGeometry(200, 200, 500, 400)
        # self.create_form_fields()

    def create_form_fields(self):
        # Initialize input fields for customer and debt
        self.person_name_input = QLineEdit()
        self.person_id = QLineEdit()
        self.telephone_input = QLineEdit()
        self.date_naisse_input = QDateEdit(self)
        self.date_naisse_input.setCalendarPopup(True)
        self.date_naisse_input.setDate(QDate.currentDate())
        self.date_naisse_input.setDisplayFormat("dd-MM-yyyy")

        self.amount_input = QLineEdit()
        self.debt_date_input = QDateEdit(self)
        self.debt_date_input.setCalendarPopup(True)
        self.debt_date_input.setDate(QDate.currentDate())
        self.debt_date_input.setDisplayFormat("dd-MM-yyyy")

        # Define fields with their labels
        fields = [
            (TranslationManager.tr("Nom de la personne:"), self.person_name_input),
            (TranslationManager.tr("Numéro d'identité:"), self.person_id),
            (TranslationManager.tr("Téléphone:"), self.telephone_input),
            (TranslationManager.tr("Date de naissance:"), self.date_naisse_input),
            (TranslationManager.tr("Montant:"), self.amount_input),
            (TranslationManager.tr("Date du dette:"), self.debt_date_input),
        ]

        # Create rows for input fields
        for label, widget in fields:
            self.create_input_row(label, widget)

    def on_submit(self):
        name = self.person_name_input.text().strip()
        identite = self.person_id.text().strip()
        telephone = self.telephone_input.text().strip()
        date_naisse = self.date_naisse_input.date().toPyDate()
        amount_str = self.amount_input.text().strip()
        debt_date = self.debt_date_input.date().toPyDate()

        # Validate inputs
        is_valid_name = self.validate_name(name)
        is_valid_amount, amount = self.validate_amount(amount_str)

        if not (is_valid_name and is_valid_amount):
            return

        session = SessionLocal()
        try:
            # Check if the customer exists
            customer = session.query(Customer).filter_by(identite=identite).first()

            if not customer:
                # Create a new customer
                customer = Customer(
                    name=name,
                    identite=identite,
                    telephone=telephone,
                    date_naisse=date_naisse,
                )
                session.add(customer)
                session.flush()  # Get the customer ID for the new customer

            # Add debt for the customer
            debt = session.query(Debt).filter_by(customer_id=customer.id).first()

            if debt:
                old_data = {
                    TranslationManager.tr("name"): customer.name,
                    TranslationManager.tr("montant du dette"): debt.amount,
                    TranslationManager.tr("dette actuelle"): debt.current_debt,
                }
                debt.amount += amount
                debt.debt_date = debt_date
                debt.current_debt += amount
                debt.created_at = datetime.now()

                log_audit_entry(
                    db_session=session,
                    table_name=TranslationManager.tr("Dette"),
                    operation=TranslationManager.tr("MISE A JOUR"),
                    record_id=debt.id,
                    user_id=self.user_id,
                    changes={
                        "old": old_data,
                        "new": {
                            TranslationManager.tr("name"): customer.name,
                            TranslationManager.tr("montant du dette"): debt.amount,
                            TranslationManager.tr("dette actuelle"): debt.current_debt,
                        },
                    },
                )
            else:
                debt = Debt(
                    amount=amount,
                    debt_date=debt_date,
                    current_debt=amount,
                    customer_id=customer.id,
                    created_at=datetime.now(),
                    paid_debt=0.0,
                )
                session.add(debt)
                session.commit()
                # Log audit entry
                log_audit_entry(
                    db_session=session,
                    table_name=TranslationManager.tr("Dette"),
                    operation=TranslationManager.tr("INSERTION"),
                    record_id=debt.id,
                    user_id=self.user_id,
                    changes={
                        TranslationManager.tr("nom"): customer.name,
                        TranslationManager.tr("montant"): amount,
                    },
                )

            session.commit()
            QMessageBox.information(
                self,
                TranslationManager.tr("Succès"),
                TranslationManager.tr("Dette ajoutée avec succès."),
            )
            self.accept()

        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(
                self,
                TranslationManager.tr("Erreur"),
                f"{TranslationManager.tr('Erreur SQLAlchemy')}: {str(e)}",
            )
        finally:
            session.close()

    def retranslate_ui(self):
        self.setWindowTitle(TranslationManager.tr("Ajouter une dette"))
        self.customer_label.setText(TranslationManager.tr("Client:"))
        self.amount_label.setText(TranslationManager.tr("Montant:"))
        self.date_label.setText(TranslationManager.tr("Date:"))
        self.submit_button.setText(TranslationManager.tr("Ajouter"))
