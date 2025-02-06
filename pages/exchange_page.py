from PyQt5.QtWidgets import (
    QComboBox,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
    QDialog,
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QSizePolicy,
    QHeaderView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from database.models import Currency
from database.database import SessionLocal
from dialogs.exchange_confirm_dialog import ExchangeConfirmationDialog
from pages.base_page import BasePage
from utils.translation_manager import TranslationManager
from utils.audit_logger import log_audit_entry


class CurrencyExchangePage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, title=TranslationManager.tr("Échange de Devises"))
        self.user_id = parent.user_id
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
        self.convert_button.setFixedWidth(200)
        self.convert_button.clicked.connect(self.perform_conversion)

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

    def load_currencies_from_db(self):
        """Load currencies into the combo boxes."""
        session = SessionLocal()
        try:
            currencies = session.query(Currency).all()
            self.source_currency_combo.clear()
            self.target_currency_combo.clear()

            for currency in currencies:
                self.source_currency_combo.addItem(currency.code)
                self.target_currency_combo.addItem(currency.code)

        except Exception as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Impossible de charger les devises : {0}").format(
                    str(e)
                ),
            )
        finally:
            session.close()

    def load_conversion_rates(self):
        """Load and display conversion rates in the table."""
        session = SessionLocal()
        try:
            currencies = session.query(Currency).all()
            self.table.setRowCount(len(currencies))

            for row, currency in enumerate(currencies):
                # Calculate conversion rates
                mru_rate = 1.0
                conversion_to_others = currency.rate / mru_rate
                conversion_from_others = (
                    mru_rate / currency.rate if currency.rate != 0 else 0
                )
                balance = currency.balance if hasattr(currency, "balance") else 0

                # Populate table cells
                self.table.setItem(row, 0, QTableWidgetItem(currency.code))
                self.table.setItem(
                    row, 1, QTableWidgetItem(self.format_french_number(balance))
                )
                self.table.setItem(
                    row, 2, QTableWidgetItem(f"{conversion_to_others:.6f}")
                )
                self.table.setItem(
                    row, 3, QTableWidgetItem(f"{conversion_from_others:.6f}")
                )

                total = sum(currency.balance / currency.rate for currency in currencies)

                # Add modify button using BasePage's helper method
                buttons_config = [
                    {
                        "text": TranslationManager.tr("Modifier Taux"),
                        "color": "#007BFF",
                        "callback": lambda id, r: self.modify_rate(id),
                        "width": 100,
                    }
                ]
                self.add_action_buttons(row, currency.code, buttons_config)
            self.total_prefix = TranslationManager.tr("Total Disponible")
            self.update_total_label(total, self.total_prefix)
        except Exception as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr(
                    "Impossible de charger les taux de conversion : {0}"
                ).format(str(e)),
            )
        finally:
            session.close()

    def modify_rate(self, currency_code):
        """Modify the rate of a currency."""
        session = SessionLocal()
        try:
            currency = session.query(Currency).filter_by(code=currency_code).first()
            if not currency:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Devise {0} introuvable").format(
                        currency_code
                    ),
                )
                return

            dialog = QInputDialog(self)
            dialog.setWindowTitle(TranslationManager.tr("Modifier Taux"))
            dialog.setLabelText(
                TranslationManager.tr("Entrez un nouveau taux pour {0} :").format(
                    currency_code
                )
            )
            dialog.setTextValue(str(currency.rate))

            # Use a validator to allow only valid double values
            validator = CustomDoubleValidator(0.000001, 1000000.0, 6, self)
            line_edit = dialog.findChild(QLineEdit)
            if line_edit:
                line_edit.setValidator(validator)

            ok = dialog.exec()
            new_rate_text = dialog.textValue()

            if ok and new_rate_text:
                try:

                    new_rate_text = new_rate_text.replace(",", ".")
                    new_rate = float(new_rate_text)
                    # Record old state for audit log
                    old_data = {"taux": currency.rate}

                    currency.rate = new_rate
                    session.commit()
                except ValueError:
                    QMessageBox.warning(
                        self,
                        TranslationManager.tr("Erreur"),
                        TranslationManager.tr("Veuillez entrer un nombre valide."),
                    )

                # Log audit entry
                log_audit_entry(
                    db_session=session,
                    table_name=TranslationManager.tr("Devise"),
                    operation=TranslationManager.tr("MISE A JOUR"),
                    record_id=currency.id,
                    user_id=self.user_id,
                    changes={
                        "old": old_data,
                        "new": {
                            "taux": currency.rate,
                        },
                    },
                )
                self.load_conversion_rates()
                self.show_message(
                    TranslationManager.tr("Succès"),
                    TranslationManager.tr(
                        "Taux pour {0} mis à jour avec succès !"
                    ).format(currency_code),
                )

        except Exception as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Échec de la modification du taux : {0}").format(
                    str(e)
                ),
            )
        finally:
            session.close()

    def perform_conversion(self):
        """Perform currency conversion based on user input."""
        session = SessionLocal()
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

            # Fetch conversion rates
            source_currency_obj = (
                session.query(Currency).filter_by(code=source_currency).first()
            )
            target_currency_obj = (
                session.query(Currency).filter_by(code=target_currency).first()
            )

            if not source_currency_obj or not target_currency_obj:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Taux de change introuvables"),
                )
                return

            # Perform conversion
            converted_amount = (
                amount / source_currency_obj.rate * target_currency_obj.rate
            )

            # Check if target currency has sufficient balance
            if converted_amount > target_currency_obj.balance:
                QMessageBox.warning(
                    self,
                    TranslationManager.tr("Solde insuffisant"),
                    TranslationManager.tr(
                        "Le solde disponible en {0} ({1}) est insuffisant pour cette opération."
                    ).format(
                        target_currency,
                        self.format_french_number(target_currency_obj.balance),
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
        finally:
            session.close()

    def save_conversion_to_db(
        self, source_currency, target_currency, amount, converted_amount
    ):
        """Save the conversion transaction to the database."""
        session = SessionLocal()
        try:
            source_currency_obj = (
                session.query(Currency).filter_by(code=source_currency).first()
            )
            target_currency_obj = (
                session.query(Currency).filter_by(code=target_currency).first()
            )

            if not source_currency_obj or not target_currency_obj:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Devises introuvables"),
                )
                return

            # Record old state for audit log
            old_data = {
                "source": source_currency_obj.code,
                "cible": target_currency_obj.code,
                "solde source": source_currency_obj.balance,
                "solde cible": target_currency_obj.balance,
            }
            # Update amounts
            target_currency_obj.balance -= converted_amount
            target_currency_obj.output += converted_amount

            source_currency_obj.balance += amount
            source_currency_obj.input += amount

            # Log audit entry
            log_audit_entry(
                db_session=session,
                table_name=TranslationManager.tr("Devise"),
                operation=TranslationManager.tr("ECHANGE"),
                record_id=target_currency_obj.id,
                user_id=self.user_id,
                changes={
                    "old": old_data,
                    "new": {
                        "source": source_currency_obj.code,
                        "cible": target_currency_obj.code,
                        "solde source": source_currency_obj.balance,
                        "solde cible": target_currency_obj.balance,
                    },
                },
            )
            session.commit()

            QMessageBox.information(
                self,
                TranslationManager.tr("Succès"),
                TranslationManager.tr("Échange effectué avec succès"),
            )
            self.load_conversion_rates()

        except Exception as e:
            session.rollback()
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr(
                    "Impossible d'enregistrer les changements : {0}"
                ).format(str(e)),
            )
        finally:
            session.close()

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
class CustomDoubleValidator(QDoubleValidator):
    def validate(self, input_str, pos):
        # Replace comma with dot for validation
        input_str = input_str.replace(",", ".")
        return super().validate(input_str, pos)
