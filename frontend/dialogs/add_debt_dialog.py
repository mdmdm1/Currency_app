from datetime import datetime
import json
from PyQt5.QtWidgets import (
    QLineEdit,
    QDateEdit,
    QLabel,
    QHBoxLayout,
    QMessageBox,
    QSizePolicy,
    QPushButton,
    QWidget,
)
from PyQt5.QtCore import QDate, Qt
import requests
from database.models import Customer, Debt
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError

from utils.translation_manager import TranslationManager
from utils.audit_logger import log_audit_entry


class AddDebtDialog(BaseDialog):
    def __init__(self, parent):  # Parent is DebtPage
        super().__init__(TranslationManager.tr("Ajouter une dette"), parent)
        self.user_id = parent.user_id
        # self.setGeometry(400, 65, 500, 400)

    def create_form_fields(self):
        """Create form fields with proper RTL/LTR ordering"""
        # Clear existing fields
        for i in reversed(range(self.form_layout.count())):
            self.form_layout.itemAt(i).widget().deleteLater()

        # Create specific widgets and store as class attributes
        self.person_name_input = QLineEdit()
        self.person_id = QLineEdit()
        self.telephone_input = QLineEdit()
        self.date_naisse_input = self._create_date_input()
        self.amount_input = QLineEdit()
        self.debt_date_input = self._create_date_input()

        self.person_name_input.setObjectName("person-name")
        self.person_id.setObjectName("person-id")
        self.telephone_input.setObjectName("telephone")
        self.amount_input.setObjectName("amount")
        self.debt_date_input.setObjectName("debt-date")

        self.setStyleSheet(
            """
            QLineEdit#person-name {
                background-color: #fff3cd;
                border: 1px solid #ffecb5;
            }

            QLineEdit#amount {
                font-weight: bold;
                color: green;
            }
        """
        )

        # Define fields with their labels and widgets
        self.fields = [
            (TranslationManager.tr("Nom de la personne:"), self.person_name_input),
            (TranslationManager.tr("Numéro d'identité:"), self.person_id),
            (TranslationManager.tr("Téléphone:"), self.telephone_input),
            (TranslationManager.tr("Date de naissance:"), self.date_naisse_input),
            (TranslationManager.tr("Montant:"), self.amount_input),
            (TranslationManager.tr("Date du dette:"), self.debt_date_input),
        ]

        # Create rows
        for label, widget in self.fields:
            self.create_input_row(label, widget)

    def _create_date_input(self):
        date_input = QDateEdit(self)
        date_input.setCalendarPopup(True)
        date_input.setDate(QDate.currentDate())
        date_input.setDisplayFormat("dd-MM-yyyy")
        return date_input

    def on_submit(self):
        name = self.person_name_input.text().strip()
        identite = self.person_id.text().strip()
        telephone = self.telephone_input.text().strip()
        date_naisse = self.date_naisse_input.date().toPyDate()
        amount_str = self.amount_input.text().strip()
        debt_date = self.debt_date_input.date().toPyDate()

        # Validate inputs
        is_valid_name = self.validate_name(name)
        is_validate_identite = self.validate_identite(identite)
        is_valid_amount, amount = self.validate_amount(amount_str)

        if not is_validate_identite:
            return
        if not (is_valid_name and is_valid_amount):
            return

        try:
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

            # Fetch debt data for the customer
            debt_response = requests.get(
                f"http://127.0.0.1:8000/debts/by-customer-id/{customer['id']}"
            )

            if debt_response.status_code == 404:
                debt = None  # No debt found
            else:
                debt_response.raise_for_status()
                debt = debt_response.json()

            if debt is None:
                # Create new debt
                new_debt_response = requests.post(
                    "http://127.0.0.1:8000/debts/",
                    json={
                        "amount": amount,
                        "debt_date": debt_date.strftime("%Y-%m-%d"),
                        "current_debt": amount,
                        "customer_id": customer["id"],
                        "created_at": datetime.now().date().isoformat(),
                        "paid_debt": 0.0,
                    },
                )
                new_debt_response.raise_for_status()
                debt = new_debt_response.json()

                # Log audit entry for new debt
                audit_response = requests.post(
                    "http://127.0.0.1:8000/audit_logs/",
                    json={
                        "table_name": TranslationManager.tr("Dette"),
                        "operation": TranslationManager.tr("INSERTION"),
                        "record_id": debt["id"],
                        "user_id": self.user_id,
                        "changes": {
                            TranslationManager.tr("nom"): customer["name"],
                            TranslationManager.tr("montant"): amount,
                        },
                    },
                )
                audit_response.raise_for_status()

            else:
                # Update existing debt
                old_data = {
                    TranslationManager.tr("name"): customer["name"],
                    TranslationManager.tr("montant du dette"): debt["amount"],
                    TranslationManager.tr("dette actuelle"): debt["current_debt"],
                }
                updated_data = {
                    "amount": debt["amount"] + amount,
                    "debt_date": debt_date.strftime("%Y-%m-%d"),
                    "current_debt": debt["current_debt"] + amount,
                    "updated_at": datetime.now().date().isoformat(),
                }

                updated_debt_response = requests.put(
                    f"http://127.0.0.1:8000/debts/{debt["id"]}", json=updated_data
                )

                updated_debt_response.raise_for_status()
                debt = updated_debt_response.json()

                audit_response = requests.post(
                    "http://127.0.0.1:8000/audit_logs/",
                    json={
                        "table_name": TranslationManager.tr("Dette"),
                        "operation": TranslationManager.tr("MISE A JOUR"),
                        "record_id": debt["id"],
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
                TranslationManager.tr("Succès"),
                TranslationManager.tr("Dette ajoutée avec succès."),
            )
            self.accept()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(
                self, TranslationManager.tr("Erreur"), f"Erreur: {str(e)}"
            )

    def retranslate_ui(self):

        print("Retranslating AddDebtDialog UI")
        self.setWindowTitle(TranslationManager.tr("Ajouter une dette"))

        # Remove existing widgets from form layout
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Recreate form fields
        self.cancel_button = QPushButton(TranslationManager.tr("Annuler"))
        self.submit_button = QPushButton(TranslationManager.tr("Effectuer"))
        self.submit_button.setObjectName("submit-button")
        self.cancel_button.setObjectName("cancel-button")

        # self.create_form_fields()
        # self.create_buttons()

        # Set layout direction
        main_window = self._find_main_window()
        if main_window and main_window.translation_manager.current_language == "ar":
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

        self.adjustSize()
