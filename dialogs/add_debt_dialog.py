from datetime import datetime
from PyQt5.QtWidgets import QLineEdit, QDateEdit, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
from database.models import Customer, Debt
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError


class AddDebtDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Ajouter une dette", parent)
        self.setGeometry(250, 250, 500, 400)
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
            ("Nom de la personne:", self.person_name_input),
            ("Numéro d'identité:", self.person_id),
            ("Téléphone:", self.telephone_input),
            ("Date de naissance:", self.date_naisse_input),
            ("Montant:", self.amount_input),
            ("Date du dette:", self.debt_date_input),
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
            QMessageBox.information(self, "Succès", "Dette ajoutée avec succès.")
            self.accept()

        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Erreur SQLAlchemy: {str(e)}")
        finally:
            session.close()
