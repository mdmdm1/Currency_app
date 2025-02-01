from PyQt5.QtWidgets import QLineEdit, QDateEdit, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
from database.models import Customer, Deposit
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError

from utils.translation_manager import TranslationManager
from utils.audit_logger import log_audit_entry


class AddDepositDialog(BaseDialog):
    def __init__(self, parent, customer_id=None):
        super().__init__(TranslationManager.tr("Ajouter un dépôt"), parent)
        self.setGeometry(250, 250, 500, 400)
        self.user_id = parent.user_id
        self.customer_id = customer_id
        if self.customer_id:
            try:
                self.populate_form_fields()
            except Exception as e:
                QMessageBox.warning(
                    self,
                    TranslationManager.tr("Erreur"),
                    f"{TranslationManager.tr('Échec de récupération des données:')} {str(e)}",
                )

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
            (TranslationManager.tr("Nom de la personne:"), self.person_name_input),
            (TranslationManager.tr("Numéro d'identité:"), self.person_id),
            (TranslationManager.tr("Téléphone:"), self.telephone_input),
            (TranslationManager.tr("Date de naissance:"), self.date_naisse_input),
            (TranslationManager.tr("Montant:"), self.amount_input),
            (TranslationManager.tr("Date du dépôt:"), self.deposit_date_input),
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

        try:
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

            self.update_or_create_deposit(session, customer, amount, deposit_date)

            session.commit()
            self.accept()

        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(
                self,
                TranslationManager.tr("Erreur"),
                f"{TranslationManager.tr('Erreur SQLAlchemy:')} {str(e)}",
            )
        finally:
            session.close()

    def populate_form_fields(self):
        session = SessionLocal()
        try:
            customer_with_deposit = (
                session.query(Customer, Deposit)
                .outerjoin(Deposit, Customer.id == Deposit.customer_id)
                .filter(Customer.id == self.customer_id)
                .first()
            )

            customer, deposit = customer_with_deposit

            self.person_name_input.setText(customer.name)
            self.person_id.setText(customer.identite)
            self.telephone_input.setText(customer.telephone)

            if customer.date_naisse:
                self.date_naisse_input.setDate(customer.date_naisse)

            self.person_name_input.setEnabled(False)
            self.person_id.setEnabled(False)
            self.telephone_input.setEnabled(False)
            self.date_naisse_input.setEnabled(False)

            self.deposit_date_input.setDate(QDate.currentDate())
            self.amount_input.setFocus()

        except SQLAlchemyError as e:
            QMessageBox.critical(
                self,
                TranslationManager.tr("Erreur"),
                f"{TranslationManager.tr('Erreur lors de la récupération des données:')} {str(e)}",
            )
            self.reject()
        finally:
            session.close()

    def update_or_create_deposit(self, session, customer, amount, deposit_date):
        try:
            deposit = session.query(Deposit).filter_by(customer_id=customer.id).first()

            if deposit:
                old_data = {
                    TranslationManager.tr("nom"): customer.name,
                    TranslationManager.tr("montant du dépôt"): deposit.amount,
                    TranslationManager.tr("dette actuelle"): deposit.current_debt,
                }

                deposit.amount += amount
                deposit.current_debt += amount

                log_audit_entry(
                    db_session=session,
                    table_name=TranslationManager.tr("Dépôt"),
                    operation=TranslationManager.tr("MISE A JOUR"),
                    record_id=deposit.id,
                    user_id=self.user_id,
                    changes={
                        TranslationManager.tr("old"): old_data,
                        TranslationManager.tr("new"): {
                            TranslationManager.tr("nom"): customer.name,
                            TranslationManager.tr("montant du dépôt"): deposit.amount,
                            TranslationManager.tr(
                                "dette courante"
                            ): deposit.current_debt,
                        },
                    },
                )

                QMessageBox.information(
                    self,
                    TranslationManager.tr("Dépôt mis à jour"),
                    f"{TranslationManager.tr('Le dépôt a été augmenté de')} {amount:.2f}. {TranslationManager.tr('Nouveau total:')} {deposit.amount:.2f}",
                )
            else:
                deposit = Deposit(
                    amount=amount,
                    deposit_date=deposit_date,
                    released_deposit=0.0,
                    current_debt=amount,
                    customer_id=customer.id,
                    person_name=customer.name,
                )
                session.add(deposit)
                session.commit()

                log_audit_entry(
                    db_session=session,
                    table_name=TranslationManager.tr("Dépôt"),
                    operation=TranslationManager.tr("INSERTION"),
                    record_id=deposit.id,
                    user_id=self.user_id,
                    changes={
                        TranslationManager.tr("nom"): customer.name,
                        TranslationManager.tr("montant"): amount,
                    },
                )

                QMessageBox.information(
                    self,
                    TranslationManager.tr("Nouveau dépôt"),
                    f"{TranslationManager.tr('Un nouveau dépôt de')} {amount:.2f} {TranslationManager.tr('a été créé.')}",
                )

            return deposit

        except SQLAlchemyError as e:
            raise e
