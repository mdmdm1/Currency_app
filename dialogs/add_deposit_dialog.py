from PyQt5.QtWidgets import QLineEdit, QDateEdit, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
from database.models import Customer, Deposit
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError


class AddDepositDialog(BaseDialog):
    def __init__(self, parent=None, customer_id=None):
        super().__init__("Ajouter un dépôt", parent)
        self.setGeometry(250, 250, 500, 400)
        self.customer_id = customer_id
        # self.create_form_fields()
        if self.customer_id:
            self.populate_form_fields()

    def create_form_fields(self):
        # Initialize input fields
        self.person_name_input = QLineEdit()
        self.person_id = QLineEdit()
        self.telephone_input = QLineEdit()
        self.date_naisse_input = QDateEdit(self)
        self.date_naisse_input.setCalendarPopup(True)
        self.date_naisse_input.setDate(QDate.currentDate())
        self.date_naisse_input.setDisplayFormat("dd-MM-yyyy")

        self.amount_input = QLineEdit()
        self.deposit_date_input = QDateEdit(self)
        self.deposit_date_input.setCalendarPopup(True)
        self.deposit_date_input.setDate(QDate.currentDate())
        self.deposit_date_input.setDisplayFormat("dd-MM-yyyy")

        # Define fields with their labels
        fields = [
            ("Nom de la personne:", self.person_name_input),
            ("Numéro d'identité:", self.person_id),
            ("Téléphone:", self.telephone_input),
            ("Date de naissance:", self.date_naisse_input),
            ("Montant:", self.amount_input),
            ("Date du dépôt:", self.deposit_date_input),
        ]

        # Create rows with modern styling
        for label, widget in fields:
            self.create_input_row(label, widget)

    def validate_inputs(self):
        if not self.validate_name(self.person_name_input.text()):
            return False

        valid, amount = self.validate_amount(self.amount_input.text())
        if valid:
            self.amount_input.setText(f"{amount:.2f}")
            return True
        return False

    def get_values(self):
        return (
            self.person_name_input.text(),
            self.person_id.text(),
            self.telephone_input.text(),
            self.date_naisse_input.text(),
            self.amount_input.text(),
            self.deposit_date_input.text(),
        )

    def on_submit(self):
        name = self.person_name_input.text().strip()
        identite = self.person_id.text().strip()
        telephone = self.telephone_input.text().strip()
        date_naisse = self.date_naisse_input.date().toPyDate()
        amount_str = self.amount_input.text().strip()
        deposit_date = self.deposit_date_input.date().toPyDate()

        is_valid_name = self.validate_name(name)
        is_valid_amount, amount = self.validate_amount(amount_str)

        if not (is_valid_name and is_valid_amount):
            return

        released_deposit = 0.0
        current_debt = amount

        session = SessionLocal()
        """import logging

        logging.basicConfig(level=logging.DEBUG)"""

        try:
            # Use customer ID if provided; otherwise, find or create a new customer
            if self.customer_id:
                customer = (
                    session.query(Customer).filter_by(id=self.customer_id).first()
                )
            else:
                customer = session.query(Customer).filter_by(identite=identite).first()
                if not customer:
                    customer = Customer(
                        name=name,
                        identite=identite,
                        telephone=telephone,
                        date_naisse=date_naisse,
                    )
                    session.add(customer)
                    session.flush()

            # Update or create deposit
            self.update_or_create_deposit(session, customer, amount, deposit_date)

            session.commit()
            self.accept()

        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Erreur SQLAlchemy: {str(e)}")
        finally:
            session.close()

    def populate_form_fields(self):
        """
        Populate form fields with customer data and handle existing deposits
        """
        session = SessionLocal()
        try:
            # Get both customer and their latest deposit information

            customer_with_deposit = (
                session.query(Customer, Deposit)
                .outerjoin(Deposit, Customer.id == Deposit.customer_id)
                .filter(Customer.id == self.customer_id)
                .first()
            )

            customer, deposit = customer_with_deposit

            # Populate customer information
            self.person_name_input.setText(customer.name)
            self.person_id.setText(customer.identite)
            self.telephone_input.setText(customer.telephone)

            # Convert date_naisse to QDate if it exists
            if customer.date_naisse:
                self.date_naisse_input.setDate(customer.date_naisse)

            # Disable customer info fields since we're adding to existing customer
            self.person_name_input.setEnabled(False)
            self.person_id.setEnabled(False)
            self.telephone_input.setEnabled(False)
            self.date_naisse_input.setEnabled(False)

            # Set today's date for the new deposit
            self.deposit_date_input.setDate(QDate.currentDate())

            # Focus on the amount field since it's the main field to fill
            self.amount_input.setFocus()

        except SQLAlchemyError as e:
            QMessageBox.critical(
                self, "Erreur", f"Erreur lors de la récupération des données: {str(e)}"
            )
            self.reject()
        finally:
            session.close()

    def update_or_create_deposit(self, session, customer, amount, deposit_date):
        """
        Update an existing deposit or create a new one.
        """
        try:
            deposit = session.query(Deposit).filter_by(customer_id=customer.id).first()

            if deposit:
                # Update existing deposit
                deposit.amount += amount
                deposit.current_debt += amount
                # Don't update deposit_date as it should reflect the initial deposit date

                QMessageBox.information(
                    self,
                    "Dépôt mis à jour",
                    f"Le dépôt a été augmenté de {amount:.2f}. "
                    f"Nouveau total: {deposit.amount:.2f}",
                )
            else:
                # Create new deposit
                deposit = Deposit(
                    amount=amount,
                    deposit_date=deposit_date,
                    released_deposit=0.0,
                    current_debt=amount,
                    customer_id=customer.id,
                    person_name=customer.name,
                )
                session.add(deposit)

                QMessageBox.information(
                    self,
                    "Nouveau dépôt",
                    f"Un nouveau dépôt de {amount:.2f} a été créé.",
                )

            return deposit

        except SQLAlchemyError as e:
            raise e
