import json
from PyQt5.QtWidgets import (
    QLineEdit,
    QDateEdit,
    QLabel,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QWidget,
)
from PyQt5.QtCore import QDate, Qt
import requests
from database.models import Customer, Deposit
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError

from utils.translation_manager import TranslationManager
from utils.audit_logger import log_audit_entry


class AddDepositDialog(BaseDialog):
    def __init__(self, parent, customer_id=None):
        super().__init__(TranslationManager.tr("Ajouter un dépôt"), parent)
        self.setGeometry(400, 65, 500, 400)
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

    def create_buttons(self):
        self.buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(self.buttons_widget)
        buttons_layout.setSpacing(15)

        self.cancel_button = QPushButton(TranslationManager.tr("Annuler"))
        self.submit_button = QPushButton(TranslationManager.tr("Effectuer"))

        self.submit_button.setMinimumHeight(45)
        self.submit_button.setMinimumWidth(120)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setStyleSheet(self._get_primary_button_style())

        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setStyleSheet(self._get_secondary_button_style())

        self.submit_button.clicked.connect(self.on_submit)
        self.cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.submit_button)

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

        if not (identite):
            return
        if not (is_valid_name and is_valid_amount):
            return

        released_deposit = 0.0
        current_debt = amount

        try:
            if self.customer_id:
                response = requests.get(
                    f"http://127.0.0.1:8000/customers/{self.customer_id}"
                )
                if response.status_code == 404:
                    customer = None
                else:
                    response.raise_for_status()
                    customer = response.json()

            else:
                # Fetch customer data
                response = requests.get(
                    f"http://127.0.0.1:8000/customers/by-identite/{identite}"
                )
                if response.status_code == 404:
                    customer = None
                else:
                    response.raise_for_status()
                    customer = response.json()

                if customer is None:
                    # Create a new customer if not found
                    new_customer_response = requests.post(
                        "http://127.0.0.1:8000/customers/",
                        json={
                            "name": name,
                            "identite": identite,
                            "telephone": telephone,
                            "date_naisse": date_naisse.strftime("%Y-%m-%d"),
                        },
                    )
                    new_customer_response.raise_for_status()
                    customer = new_customer_response.json()

            self.update_or_create_deposit(customer, amount, deposit_date)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(
                self,
                TranslationManager.tr("Erreur"),
                f"{TranslationManager.tr('Erreur:')} {str(e)}",
            )

    def populate_form_fields(self):

        try:

            response = requests.get(
                f"http://127.0.0.1:8000/customers/{self.customer_id}"
            )
            if response.status_code == 404:
                customer = None
            else:
                response.raise_for_status()
                customer = response.json()

            self.person_name_input.setText(customer["name"])
            self.person_id.setText(customer["identite"])
            self.telephone_input.setText(customer["telephone"])

            if customer["date_naisse"]:
                date_naisse = QDate.fromString(customer["date_naisse"], "yyyy-MM-dd")
                self.date_naisse_input.setDate(date_naisse)

            self.person_name_input.setEnabled(False)
            self.person_id.setEnabled(False)
            self.telephone_input.setEnabled(False)
            self.date_naisse_input.setEnabled(False)

            self.deposit_date_input.setDate(QDate.currentDate())
            self.amount_input.setFocus()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(
                self,
                TranslationManager.tr("Erreur"),
                f"{TranslationManager.tr('Erreur lors de la récupération des données:')} {str(e)}",
            )
            self.reject()

    def update_or_create_deposit(self, customer, amount, deposit_date):
        try:
            # Fetch debt data for the customer
            deposit_response = requests.get(
                f"http://127.0.0.1:8000/deposits/by-customer-id/{customer['id']}"
            )

            if deposit_response.status_code != 404:
                deposit_response.raise_for_status()
                deposit = deposit_response.json()

                old_data = {
                    TranslationManager.tr("nom"): customer["name"],
                    TranslationManager.tr("montant du dépôt"): deposit["amount"],
                    TranslationManager.tr("dette actuelle"): deposit["current_debt"],
                }

                updated_data = {
                    "amount": deposit["amount"] + amount,
                    "current_debt": deposit["current_debt"] + amount,
                }

                updated_deposit_response = requests.put(
                    f"http://127.0.0.1:8000/deposits/{deposit["id"]}", json=updated_data
                )

                updated_deposit_response.raise_for_status()
                deposit = updated_deposit_response.json()

                audit_response = requests.post(
                    "http://127.0.0.1:8000/audit_logs/",
                    json={
                        "table_name": TranslationManager.tr("Dépôt"),
                        "operation": TranslationManager.tr("MISE A JOUR"),
                        "record_id": deposit["id"],
                        "user_id": self.user_id,
                        "changes": json.dumps(
                            {
                                "old": old_data,
                                "new": {
                                    TranslationManager.tr("name"): customer["name"],
                                    TranslationManager.tr(
                                        "montant du dette"
                                    ): updated_data["amount"],
                                    TranslationManager.tr(
                                        "dette actuelle"
                                    ): updated_data["current_debt"],
                                },
                            }
                        ),
                    },
                )
                audit_response.raise_for_status()

                QMessageBox.information(
                    self,
                    TranslationManager.tr("Dépôt mis à jour"),
                    f"{TranslationManager.tr('Le dépôt a été augmenté de')} {amount:.2f}. {TranslationManager.tr('Nouveau total:')} {deposit["amount"]:.2f}",
                )
                self.accept()
            else:
                # Create a new deposit

                new_deposit_response = requests.post(
                    "http://127.0.0.1:8000/deposits/",
                    json={
                        "amount": amount,
                        "deposit_date": deposit_date.strftime("%Y-%m-%d"),
                        "released_deposit": 0.0,
                        "current_debt": amount,
                        "customer_id": customer["id"],
                        "person_name": customer["name"],
                    },
                )
                new_deposit_response.raise_for_status()
                deposit = new_deposit_response.json()

                # Log audit entry for new debt
                audit_response = requests.post(
                    "http://127.0.0.1:8000/audit_logs/",
                    json={
                        "table_name": TranslationManager.tr("Dépôt"),
                        "operation": TranslationManager.tr("INSERTION"),
                        "record_id": deposit["id"],
                        "user_id": self.user_id,
                        "changes": json.dumps(
                            {
                                TranslationManager.tr("nom"): customer["name"],
                                TranslationManager.tr("montant"): amount,
                            }
                        ),
                    },
                )
                audit_response.raise_for_status()

                QMessageBox.information(
                    self,
                    TranslationManager.tr("Nouveau dépôt"),
                    f"{TranslationManager.tr('Un nouveau dépôt de')} {amount:.2f} {TranslationManager.tr('a été créé.')}",
                )
            self.accept()
            # return deposit

        except requests.exceptions.RequestException as e:
            raise e
