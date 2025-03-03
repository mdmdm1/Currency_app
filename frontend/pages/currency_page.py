from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PyQt5.QtCore import Qt
import requests
from database.database import SessionLocal
from database.models import Currency
from sqlalchemy.exc import SQLAlchemyError
from pages.base_page import BasePage
import json

from utils.translation_manager import TranslationManager
from utils.audit_logger import log_audit_entry


class CurrencyPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, title=TranslationManager.tr("Gestion des Devises"))
        self.user_id = parent.user_id
        self.api_base_url = parent.api_base_url
        self.init_ui()

    def init_ui(self):
        # Define table headers, including the new 'Code' column
        self.setup_table_headers(
            [
                TranslationManager.tr("Devise"),
                TranslationManager.tr("Code"),
                TranslationManager.tr("Montant Disponible"),
                TranslationManager.tr("Entrée"),
                TranslationManager.tr("Sortie"),
                TranslationManager.tr("Actions"),
            ]
        )

        # Fix the width of the actions column
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 190)

        # Section for adding a new currency
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)

        self.new_currency_input = QLineEdit()
        self.new_currency_input.setPlaceholderText(
            TranslationManager.tr("Entrez une nouvelle devise (ex. : Euro)")
        )

        self.new_code_input = QLineEdit()
        self.new_code_input.setPlaceholderText(
            TranslationManager.tr("Entrez le code de la devise (ex. : EUR)")
        )

        add_button = QPushButton(TranslationManager.tr("Ajouter une Devise"))
        add_button.clicked.connect(self.add_new_currency)

        top_layout.addWidget(self.new_currency_input)
        top_layout.addWidget(self.new_code_input)
        top_layout.addWidget(add_button)

        self.layout.insertWidget(0, top_container)

        # Load initial data
        self.load_currency_data()

    def load_currency_data(self):
        try:
            response = requests.get("http://127.0.0.1:8000/currencies")
            response.raise_for_status()
            currencies = response.json()
            self.table.setRowCount(len(currencies))
            total = 0

            for row, currency in enumerate(currencies):
                self.table.setItem(row, 0, QTableWidgetItem(currency["name"]))

                # Currency code
                self.table.setItem(row, 1, QTableWidgetItem(currency["code"]))

                # Available balance (formatted in French style)
                formatted_balance = self.format_french_number(currency["balance"])
                amount_item = QTableWidgetItem(formatted_balance)
                amount_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 2, amount_item)

                # Input field
                input_field = QLineEdit()
                input_field.setPlaceholderText(
                    TranslationManager.tr("Montant à ajouter")
                )
                self.table.setCellWidget(row, 3, input_field)

                # Output field
                output_field = QLineEdit()
                output_field.setPlaceholderText(
                    TranslationManager.tr("Montant à soustraire")
                )
                self.table.setCellWidget(row, 4, output_field)

                # Configure action buttons for this row
                buttons_config = [
                    {
                        "text": TranslationManager.tr("Mettre à jour"),
                        "color": "#ffc107",
                        "callback": self.update_currency,
                        "width": 80,
                    },
                    {
                        "text": TranslationManager.tr("Supprimer"),
                        "color": "#dc3545",
                        "callback": self.delete_currency,
                        "width": 80,
                    },
                ]
                self.add_action_buttons(row, currency["id"], buttons_config)

                total = sum(
                    currency["balance"] / currency["rate"] for currency in currencies
                )

            self.total_prefix = TranslationManager.tr("Total Disponible")
            self.update_total_label(total, self.total_prefix)

        except requests.exceptions.RequestException as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr(
                    "Erreur lors du chargement des devises : {0}"
                ).format(str(e)),
            )

    def add_new_currency(self):
        currency_name = self.new_currency_input.text().strip().upper()
        currency_code = self.new_code_input.text().strip().upper()

        if not currency_name or not currency_code:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Veuillez entrer un nom et un code de devise"),
            )
            return
        if len(currency_code) != 3:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Code doit être composé de trois caractères"),
            )
            return

        try:
            # headers = self.get_auth_headers()
            payload = {
                "name": currency_name,
                "code": currency_code,
                "balance": 0,
                "input": 0,
                "output": 0,
            }

            # Make API call to add a new currency
            response = requests.post(
                f"{self.api_base_url}/currencies/",
                json=payload,
                # headers=headers,
            )

            if response.status_code != 200:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Échec de l'ajout de la devise : {0}").format(
                        response.text
                    ),
                )
                return

            # Clear input fields and reload data
            self.new_currency_input.clear()
            self.new_code_input.clear()
            self.load_currency_data()

        except requests.exceptions.RequestException as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Erreur de connexion au serveur : {0}").format(
                    str(e)
                ),
            )

    def update_currency(self, currency_id, row):
        input_field = self.table.cellWidget(row, 3)
        output_field = self.table.cellWidget(row, 4)
        print(input_field.text())
        try:
            input_amount = float(input_field.text()) if input_field.text() else 0
            output_amount = float(output_field.text()) if output_field.text() else 0
            if input_amount == 0 and output_amount == 0:
                return

            # headers = self.get_auth_headers()
            payload = {
                "input": input_amount,
                "output": output_amount,
            }

            # Make API call to update the currency
            response = requests.put(
                f"{self.api_base_url}/currencies/{currency_id}",
                json=payload,
                # headers=headers,
            )

            if response.status_code != 200:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Échec de la mise à jour : {0}").format(
                        response.text
                    ),
                )
                return

            # Clear input fields and reload data
            input_field.clear()
            output_field.clear()
            self.load_currency_data()

        except ValueError:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr(
                    "Veuillez entrer des montants valides pour l'entrée et la sortie"
                ),
            )
        except requests.exceptions.RequestException as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Erreur de connexion au serveur : {0}").format(
                    str(e)
                ),
            )

    def delete_currency(self, currency_id, row):
        confirmation = QMessageBox(self)
        confirmation.setIcon(QMessageBox.Question)
        confirmation.setWindowTitle(TranslationManager.tr("Confirmer la suppression"))
        confirmation.setText(
            TranslationManager.tr("Êtes-vous sûr de vouloir supprimer cette devise ?")
        )

        yes_button = confirmation.addButton(
            TranslationManager.tr("Oui"), QMessageBox.YesRole
        )
        no_button = confirmation.addButton(
            TranslationManager.tr("Non"), QMessageBox.NoRole
        )

        confirmation.setDefaultButton(no_button)
        confirmation.exec_()

        if confirmation.clickedButton() == yes_button:
            try:
                # headers = self.get_auth_headers()
                currency_response = requests.get(
                    f"http://127.0.0.1:8000/currencies/{currency_id}"
                )
                currency_response.raise_for_status()
                currency = currency_response.json()

                # Make API call to delete the currency
                response = requests.delete(
                    f"{self.api_base_url}/currencies/{currency_id}",
                    # headers=headers,
                )

                if response.status_code != 200:
                    self.show_error_message(
                        TranslationManager.tr("Erreur"),
                        TranslationManager.tr(
                            "Erreur lors de la suppression : {0}"
                        ).format(response.text),
                    )
                    return

                # Log the deletion in the audit log
                audit_response = requests.post(
                    "http://127.0.0.1:8000/audit_logs/",
                    json={
                        "table_name": TranslationManager.tr("Devise"),
                        "operation": TranslationManager.tr("SUPPRESSION"),
                        "record_id": currency_id,
                        "user_id": self.user_id,
                        "changes": json.dumps(
                            {
                                TranslationManager.tr("name"): currency["name"],
                                TranslationManager.tr("code"): currency["code"],
                                TranslationManager.tr("montant disponible"): currency[
                                    "balance"
                                ],
                                TranslationManager.tr("entrée"): currency["input"],
                                TranslationManager.tr("sortie"): currency["output"],
                            }
                        ),
                    },
                )
                audit_response.raise_for_status()

                # Reload data after successful deletion
                self.load_currency_data()

            except requests.exceptions.RequestException as e:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr(
                        "Erreur de connexion au serveur : {0}"
                    ).format(str(e)),
                )

    def retranslate_ui(self):
        # Update the window title
        self.setWindowTitle(TranslationManager.tr("Gestion des Devises"))

        # Update table headers
        self.setup_table_headers(
            [
                TranslationManager.tr("Devise"),
                TranslationManager.tr("Code"),
                TranslationManager.tr("Montant Disponible"),
                TranslationManager.tr("Entrée"),
                TranslationManager.tr("Sortie"),
                TranslationManager.tr("Actions"),
            ]
        )

        # Update placeholder text for input fields
        self.new_currency_input.setPlaceholderText(
            TranslationManager.tr("Entrez une nouvelle devise (ex. : Euro)")
        )
        self.new_code_input.setPlaceholderText(
            TranslationManager.tr("Entrez le code de la devise (ex. : EUR)")
        )

        # Update the "Add Currency" button text
        self.layout.itemAt(0).widget().layout().itemAt(2).widget().setText(
            TranslationManager.tr("Ajouter une Devise")
        )

        # Update placeholder text and button labels in the table
        for row in range(self.table.rowCount()):
            # Input field
            input_field = self.table.cellWidget(row, 3)
            if input_field:
                input_field.setPlaceholderText(
                    TranslationManager.tr("Montant à ajouter")
                )

            # Output field
            output_field = self.table.cellWidget(row, 4)
            if output_field:
                output_field.setPlaceholderText(
                    TranslationManager.tr("Montant à soustraire")
                )

            # Action buttons
            button_layout = self.table.cellWidget(row, 5).layout()
            if button_layout:
                update_button = button_layout.itemAt(0).widget()
                update_button.setText(TranslationManager.tr("Mettre à jour"))

                delete_button = button_layout.itemAt(1).widget()
                delete_button.setText(TranslationManager.tr("Supprimer"))

        self.total_prefix = TranslationManager.tr("Total Disponible")
        self.load_currency_data
