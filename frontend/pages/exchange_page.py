import json
from PyQt5.QtWidgets import (
    QComboBox,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QLabel,
    QInputDialog,
    QMessageBox,
    QTableWidgetItem,
    QWidget,
    QHeaderView,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QDoubleValidator, QIcon
import requests
from pathlib import Path
from dialogs.exchange_confirm_dialog import ExchangeConfirmationDialog
from pages.base_page import BasePage
from utils.translation_manager import TranslationManager
from config import API_BASE_URL
import re
from PyQt5.QtGui import QValidator


class CurrencyExchangePage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, title=TranslationManager.tr("Échange de Devises"))
        self.user_id = parent.user_id
        self.api_base_url = API_BASE_URL

        self.init_currency_exchange_ui()

    def init_currency_exchange_ui(self):
        """Initialize the currency exchange UI."""
        # Use the table from BasePage
        self.setup_table_headers(
            [
                TranslationManager.tr("Devise"),
                TranslationManager.tr("Solde"),
                TranslationManager.tr("1 MRU à Autres"),
                TranslationManager.tr("1 Autres à MRU"),
                TranslationManager.tr("Actions"),
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)

        # Create refresh button
        self.refresh_button = QPushButton()
        icon_dir = Path(__file__).parent.parent / "icons" / "refresh-icon.ico"
        self.refresh_button.setIcon(QIcon(str(icon_dir)))
        self.refresh_button.setIconSize(QSize(18, 18))
        self.refresh_button.setText(TranslationManager.tr("Actualiser"))
        self.refresh_button.setToolTip(
            TranslationManager.tr("Actualiser les taux et les soldes")
        )
        self.refresh_button.setFixedSize(140, 60)
        self.refresh_button.setStyleSheet(
            """
            QPushButton {
                
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 5px;
                margin-right:8px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
            """
        )
        self.refresh_button.clicked.connect(self.refresh_page)

        # Create layout for refresh button at the bottom of the table
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.refresh_button)
        refresh_layout.setContentsMargins(0, 10, 0, 20)  # Add some padding

        # Add the refresh layout right after the table in the main layout
        # First, get the index of the table in the main layout
        table_index = self.layout.indexOf(self.table)
        # Insert the refresh layout after the table
        self.layout.insertLayout(table_index + 1, refresh_layout)

        # Create converter widget
        converter_widget = QWidget()
        converter_layout = QVBoxLayout(converter_widget)
        converter_layout.setContentsMargins(0, 20, 0, 0)

        # Input fields
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText(TranslationManager.tr("Entrez le montant"))
        self.amount_input.setValidator(
            QDoubleValidator(0.0, 1e10, 2, notation=QDoubleValidator.StandardNotation)
        )
        self.amount_input.setFixedWidth(200)

        self.source_currency_combo = QComboBox()
        self.source_currency_combo.setFixedWidth(200)
        self.target_currency_combo = QComboBox()
        self.target_currency_combo.setFixedWidth(200)

        # Form layout for input fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow(TranslationManager.tr("Montant :"), self.amount_input)
        form_layout.addRow(
            TranslationManager.tr("De devise :"), self.source_currency_combo
        )
        form_layout.addRow(
            TranslationManager.tr("À devise :"), self.target_currency_combo
        )

        # Convert button
        self.convert_button = QPushButton(TranslationManager.tr("Convertir"))
        self.convert_button.setFixedWidth(120)
        self.convert_button.clicked.connect(self.perform_conversion)

        self.convert_button.setStyleSheet(
            """
            QPushButton {
                
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 5px;
                margin-right:5px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
            """
        )
        # Result Label
        self.result_label = QLabel(TranslationManager.tr("Résultat : "))
        self.result_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        # Add widgets to converter layout
        converter_layout.addLayout(form_layout)
        converter_layout.addWidget(self.convert_button, alignment=Qt.AlignLeft)
        converter_layout.addWidget(self.result_label, alignment=Qt.AlignLeft)
        converter_layout.addStretch()

        # Add converter widget to main layout
        self.layout.addWidget(converter_widget)

        # Load data
        self.load_currencies_from_db()
        self.load_conversion_rates()

    def refresh_page(self):
        self.load_currencies_from_db()
        self.load_conversion_rates()

    def load_currencies_from_db(self):
        """Load currencies into the combo boxes."""
        try:
            response = requests.get(f"{self.api_base_url}/currencies")
            response.raise_for_status()
            currencies = response.json()
            self.source_currency_combo.clear()
            self.target_currency_combo.clear()

            for currency in currencies:
                self.source_currency_combo.addItem(currency["code"])
                self.target_currency_combo.addItem(currency["code"])
            self.source_currency_combo.repaint()
            self.target_currency_combo.repaint()

        except requests.exceptions.RequestException as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Impossible de charger les devises : {0}").format(
                    str(e)
                ),
            )

    def load_conversion_rates(self):
        """Load and display conversion rates in the table."""
        try:
            response = requests.get(f"{self.api_base_url}/currencies")
            response.raise_for_status()
            currencies = response.json()

            self.table.setRowCount(len(currencies))
            total = 0

            for row, currency in enumerate(currencies):
                # Calculate conversion rates
                mru_rate = 1.0
                conversion_to_others = currency["rate"] / mru_rate
                conversion_from_others = (
                    mru_rate / currency["rate"] if currency["rate"] != 0 else 0
                )
                balance = currency["balance"] if currency["balance"] else 0

                # Populate table cells
                self.table.setItem(row, 0, QTableWidgetItem(currency["code"]))
                self.table.setItem(
                    row, 1, QTableWidgetItem(self.format_french_number(balance))
                )
                self.table.setItem(
                    row, 2, QTableWidgetItem(f"{conversion_to_others:.6f}")
                )
                self.table.setItem(
                    row, 3, QTableWidgetItem(f"{conversion_from_others:.6f}")
                )

                total = sum(
                    currency["balance"] / currency["rate"] for currency in currencies
                )

                # Add modify button using BasePage's helper method
                buttons_config = [
                    {
                        "text": TranslationManager.tr("Modifier Taux"),
                        "color": "#007BFF",
                        "callback": lambda id, r: self.modify_rate(id),
                        "width": 100,
                    }
                ]
                self.add_action_buttons(row, currency["id"], buttons_config)
            self.total_prefix = TranslationManager.tr("Total Disponible")
            self.update_total_label(total, self.total_prefix)

        except requests.exceptions.RequestException as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr(
                    "Impossible de charger les taux de conversion : {0}"
                ).format(str(e)),
            )

    def modify_rate(self, currency_id):
        """Modify the rate of a currency"""
        try:
            # Fetch existing currency data
            response = requests.get(f"{self.api_base_url}/currencies/{currency_id}")
            response.raise_for_status()
            currency = response.json()

            if not currency:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Devise {0} introuvable").format(currency_id),
                )
                return

            # Ask for new rate
            dialog = QInputDialog(self)
            dialog.setWindowTitle(TranslationManager.tr("Modifier Taux"))
            dialog.setLabelText(
                TranslationManager.tr("Entrez un nouveau taux pour {0} :").format(
                    currency["code"]
                )
            )
            dialog.setTextValue(str(currency["rate"]))

            validator = FlexibleDecimalValidator(0.000001, 1.0, 6, self)
            line_edit = dialog.findChild(QLineEdit)
            if line_edit:
                line_edit.setValidator(validator)

            ok = dialog.exec()
            new_rate_text = dialog.textValue()

            if ok and new_rate_text:
                try:
                    new_rate_text = new_rate_text.replace(",", ".")
                    new_rate = float(new_rate_text)

                    # Validate that the rate is between 0 and 1
                    if new_rate <= 0 or new_rate > 1:
                        QMessageBox.warning(
                            self,
                            TranslationManager.tr("Erreur"),
                            TranslationManager.tr(
                                "Le taux doit être compris entre 0 et 1."
                            ),
                        )
                        return  # Exit the function if the rate is invalid

                    # Send API request with all required fields
                    update_data = {
                        "name": currency["name"],
                        "code": currency["code"],
                        "input": currency["input"],
                        "output": currency["output"],
                        "balance": currency["balance"],
                        "rate": new_rate,
                    }

                    update_response = requests.put(
                        f"{self.api_base_url}/currencies/{currency_id}",
                        json=update_data,
                    )

                    update_response.raise_for_status()
                    print(update_response)

                    # Log audit entry
                    audit_response = requests.post(
                        f"{self.api_base_url}/audit_logs/",
                        json={
                            "table_name": TranslationManager.tr("Devise"),
                            "operation": TranslationManager.tr("MISE A JOUR"),
                            "record_id": currency_id,
                            "user_id": self.user_id,
                            "changes": json.dumps(
                                {
                                    "old": {
                                        TranslationManager.tr("name"): currency["code"],
                                        TranslationManager.tr("taux"): currency["rate"],
                                    },
                                    "new": {
                                        TranslationManager.tr("name"): currency["code"],
                                        TranslationManager.tr("taux"): new_rate,
                                    },
                                }
                            ),
                        },
                    )
                    audit_response.raise_for_status()

                    # Reload UI after successful update
                    self.load_conversion_rates()

                    QMessageBox.information(
                        self,
                        TranslationManager.tr("Succès"),
                        TranslationManager.tr(
                            "Taux pour {0} mis à jour avec succès !"
                        ).format(currency["code"]),
                    )

                except ValueError:
                    QMessageBox.warning(
                        self,
                        TranslationManager.tr("Erreur"),
                        TranslationManager.tr("Veuillez entrer un nombre valide."),
                    )

        except requests.exceptions.RequestException as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Échec de la modification du taux : {0}").format(
                    str(e)
                ),
            )

    def perform_conversion(self):
        """Perform currency conversion based on user input using API calls."""
        try:
            # Validate input
            if not self.amount_input.text():
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Veuillez entrer un montant"),
                )
                return

            amount = float(self.amount_input.text())
            source_currency = self.source_currency_combo.currentText()
            target_currency = self.target_currency_combo.currentText()

            if source_currency == target_currency:
                self.result_label.setText(
                    TranslationManager.tr("Résultat : {0} {1}").format(
                        self.format_french_number(amount), target_currency
                    )
                )
                return

            # Fetch conversion rates from the API
            # headers = self.get_auth_headers()
            response = requests.get(f"{self.api_base_url}/currencies/")

            if response.status_code != 200:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Impossible de récupérer les taux de change"),
                )
                return

            currencies = response.json()
            source_currency_obj = next(
                (c for c in currencies if c["code"] == source_currency), None
            )
            target_currency_obj = next(
                (c for c in currencies if c["code"] == target_currency), None
            )

            if not source_currency_obj or not target_currency_obj:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Taux de change introuvables"),
                )
                return

            # Perform conversion
            converted_amount = (
                amount / source_currency_obj["rate"] * target_currency_obj["rate"]
            )

            # Check if target currency has sufficient balance
            if converted_amount > target_currency_obj["balance"]:
                QMessageBox.warning(
                    self,
                    TranslationManager.tr("Solde insuffisant"),
                    TranslationManager.tr(
                        "Le solde disponible en {0} ({1}) est insuffisant pour cette opération."
                    ).format(
                        target_currency,
                        self.format_french_number(target_currency_obj["balance"]),
                    ),
                )
                return

            # Show confirmation dialog
            dialog = ExchangeConfirmationDialog(
                source_currency,
                target_currency,
                self.format_french_number(amount),
                self.format_french_number(converted_amount),
                self,
            )
            if dialog.exec_() == QDialog.Accepted:
                self.save_conversion_to_db(
                    source_currency, target_currency, amount, converted_amount
                )
                # Update result label after successful conversion
                self.result_label.setText(
                    TranslationManager.tr("Résultat : {0} {1}").format(
                        self.format_french_number(converted_amount), target_currency
                    )
                )

        except ValueError:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Montant invalide"),
            )
        except Exception as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Échec de la conversion : {0}").format(str(e)),
            )

    def save_conversion_to_db(
        self, source_currency, target_currency, amount, converted_amount
    ):
        """Save the conversion transaction using an API call."""
        try:
            # headers = self.get_auth_headers()
            payload = {
                "source_currency": source_currency,
                "target_currency": target_currency,
                "amount": amount,
                "converted_amount": converted_amount,
                "user_id": self.user_id,
            }

            # Make API call to save the transaction
            response = requests.post(
                f"{self.api_base_url}/currencies/convert",
                json=payload,
                # headers=headers,
            )

            if response.status_code != 200:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Impossible d'enregistrer la transaction"),
                )
                return

            QMessageBox.information(
                self,
                TranslationManager.tr("Succès"),
                TranslationManager.tr("Échange effectué avec succès"),
            )
            self.load_conversion_rates()

        except Exception as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr(
                    "Impossible d'enregistrer les changements : {0}"
                ).format(str(e)),
            )

    def retranslate_ui(self):
        """Retranslate the UI elements for the CurrencyExchangePage."""
        # Update page title
        self.setWindowTitle(TranslationManager.tr("Échange de Devises"))

        # Update table headers
        self.setup_table_headers(
            [
                TranslationManager.tr("Devise"),
                TranslationManager.tr("Solde"),
                TranslationManager.tr("1 MRU à Autres"),
                TranslationManager.tr("1 Autres à MRU"),
                TranslationManager.tr("Actions"),
            ]
        )

        # Update placeholders and labels
        self.amount_input.setPlaceholderText(TranslationManager.tr("Entrez le montant"))
        self.convert_button.setText(TranslationManager.tr("Convertir"))
        self.result_label.setText(TranslationManager.tr("Résultat : "))

        """         # Update form layout labels
        self.layout().itemAt(0).widget().layout().itemAt(0).layout().itemAt(
            0
        ).widget().setText(TranslationManager.tr("Montant :"))
        self.layout().itemAt(0).widget().layout().itemAt(0).layout().itemAt(
            2
        ).widget().setText(TranslationManager.tr("De devise :"))
        self.layout().itemAt(0).widget().layout().itemAt(0).layout().itemAt(
            4
        ).widget().setText(TranslationManager.tr("À devise :"))
        """

        # Update any dynamically populated content
        self.load_currencies_from_db()
        self.load_conversion_rates()


# a custom validator to allow both dot and comma as decimal separators


class FlexibleDecimalValidator(QValidator):
    def __init__(self, bottom, top, decimals, parent=None):
        super().__init__(parent)
        self.bottom = bottom
        self.top = top
        self.decimals = decimals

    def validate(self, input_str, pos):
        # Allow empty or partial input
        if input_str == "":
            return (QValidator.Intermediate, input_str, pos)

        # Reject if both comma and dot are present
        if "," in input_str and "." in input_str:
            return (QValidator.Invalid, input_str, pos)

        # Build regex pattern for valid numbers with optional sign and one decimal separator
        # This pattern allows either a dot or a comma, but not both.
        pattern = r"^-?\d*(?:[.,]\d{0," + str(self.decimals) + "})?$"
        if not re.fullmatch(pattern, input_str):
            return (QValidator.Invalid, input_str, pos)

        # Normalize input to use dot for conversion
        normalized = input_str.replace(",", ".")
        try:
            value = float(normalized)
        except ValueError:
            return (QValidator.Invalid, input_str, pos)

        # Check if the value is within the allowed range
        if self.bottom <= value <= self.top:
            return (QValidator.Acceptable, input_str, pos)
        else:
            return (QValidator.Intermediate, input_str, pos)

    def fixup(self, input_str):
        # Optionally normalize input: here we replace commas with dots.
        return input_str.replace(",", ".")
