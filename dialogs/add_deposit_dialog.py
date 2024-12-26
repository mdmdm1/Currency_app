from PyQt5.QtWidgets import QLineEdit, QDateEdit, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
from database.models import Customer, Deposit
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError


class AddDepositDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Ajouter un dépôt", parent)
        self.setGeometry(250, 250, 500, 400)

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
        import logging

        logging.basicConfig(level=logging.DEBUG)

        try:
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

            deposit = Deposit(
                person_name=name,
                amount=amount,
                deposit_date=deposit_date,
                released_deposit=released_deposit,
                current_debt=current_debt,
                customer_id=customer.id,
            )
            session.add(deposit)
            session.commit()

            QMessageBox.information(self, "Succès", "Dépôt ajouté avec succès.")
            self.accept()

        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Erreur SQLAlchemy: {str(e)}")
            import traceback

            print(traceback.format_exc())

        finally:
            session.close()
