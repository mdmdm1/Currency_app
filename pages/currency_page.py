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
from database.database import SessionLocal
from database.models import Currency
from sqlalchemy.exc import SQLAlchemyError
from pages.base_page import BasePage
import json

from utils.audit_logger import log_audit_entry


class CurrencyPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, title="Gestion des Devises")
        self.user_id = parent.user_id
        self.init_ui()

    def init_ui(self):
        # Define table headers, including the new 'Code' column
        self.setup_table_headers(
            [
                "Devise",
                "Code",
                "Montant Disponible",
                "Entrée",
                "Sortie",
                "Actions",
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
            "Entrez une nouvelle devise (ex. : Euro)"
        )

        self.new_code_input = QLineEdit()
        self.new_code_input.setPlaceholderText(
            "Entrez le code de la devise (ex. : EUR)"
        )

        add_button = QPushButton("Ajouter une Devise")
        add_button.clicked.connect(self.add_new_currency)

        top_layout.addWidget(self.new_currency_input)
        top_layout.addWidget(self.new_code_input)
        top_layout.addWidget(add_button)

        self.layout.insertWidget(0, top_container)

        print("id=" + str(self.user_id))
        # Load initial data
        self.load_currency_data()

    def load_currency_data(self):
        session = SessionLocal()
        try:
            currencies = session.query(Currency).all()
            self.table.setRowCount(len(currencies))

            for row, currency in enumerate(currencies):
                # Currency name
                self.table.setItem(row, 0, QTableWidgetItem(currency.name))

                # Currency code
                self.table.setItem(row, 1, QTableWidgetItem(currency.code))

                # Available balance (formatted in French style)
                formatted_balance = self.format_french_number(currency.balance)
                amount_item = QTableWidgetItem(formatted_balance)
                amount_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 2, amount_item)

                # Input field
                input_field = QLineEdit()
                input_field.setPlaceholderText("Montant à ajouter")
                self.table.setCellWidget(row, 3, input_field)

                # Output field
                output_field = QLineEdit()
                output_field.setPlaceholderText("Montant à soustraire")
                self.table.setCellWidget(row, 4, output_field)

                # Configure action buttons for this row
                buttons_config = [
                    {
                        "text": "Mettre à jour",
                        "color": "#ffc107",
                        "callback": self.update_currency,
                        "width": 80,
                    },
                    {
                        "text": "Supprimer",
                        "color": "#dc3545",
                        "callback": self.delete_currency,
                        "width": 80,
                    },
                ]
                self.add_action_buttons(row, currency.id, buttons_config)

            # Update the total
            total = sum(currency.balance for currency in currencies)
            self.update_total_label(total, "Total Disponible")

        except SQLAlchemyError as e:
            self.show_error_message(
                "Erreur", f"Erreur lors du chargement des devises : {str(e)}"
            )
        finally:
            session.close()

    def add_new_currency(self):
        currency_name = self.new_currency_input.text().strip().upper()
        currency_code = self.new_code_input.text().strip().upper()

        if not currency_name or not currency_code:
            self.show_error_message(
                "Erreur", "Veuillez entrer un nom et un code de devise"
            )
            return
        if len(currency_code) != 3:
            self.show_error_message(
                "Erreur", "Code doit être composé de trois caractères"
            )
            return
        session = SessionLocal()
        try:
            # Check if the currency or code already exists
            if (
                session.query(Currency).filter_by(name=currency_name).first()
                or session.query(Currency).filter_by(code=currency_code).first()
            ):
                self.show_error_message("Erreur", "Cette devise ou ce code existe déjà")
                return

            # Add a new currency
            new_currency = Currency(
                name=currency_name, code=currency_code, balance=0, input=0, output=0
            )
            session.add(new_currency)
            session.commit()

            # Log audit entry
            log_audit_entry(
                db_session=session,
                table_name="Devise",
                operation="INSERTION",
                record_id=new_currency.id,
                user_id=self.user_id,
                changes={"nom": currency_name, "code": currency_code, "solde": 0},
            )
            # Clear input fields and reload data
            self.new_currency_input.clear()
            self.new_code_input.clear()
            self.load_currency_data()

        except SQLAlchemyError as e:
            session.rollback()
            self.show_error_message(
                "Erreur", f"Échec de l'ajout de la devise : {str(e)}"
            )
        finally:
            session.close()

    def update_currency(self, currency_id, row):
        input_field = self.table.cellWidget(row, 3)
        output_field = self.table.cellWidget(row, 4)
        try:
            input_amount = float(input_field.text()) if input_field.text() else 0
            output_amount = float(output_field.text()) if output_field.text() else 0
            if input_amount == 0 and output_amount == 0:
                return
            session = SessionLocal()
            try:
                currency = session.query(Currency).filter_by(id=currency_id).first()
                if not currency:
                    raise ValueError("Devise introuvable")

                # Record old state for audit log
                old_data = {
                    "input": currency.input,
                    "output": currency.output,
                    "solde": currency.balance,
                }

                # Update amounts
                currency.input += input_amount
                currency.output += output_amount
                currency.balance = currency.balance + input_amount - output_amount

                session.commit()

                # Log audit entry
                log_audit_entry(
                    db_session=session,
                    table_name="Devise",
                    operation="MISE A JOUR",
                    record_id=currency_id,
                    user_id=self.user_id,
                    changes={
                        "old": old_data,
                        "new": {
                            "name": currency.name,
                            "input": currency.input,
                            "output": currency.output,
                            "balance": currency.balance,
                        },
                    },
                )
                # Clear input fields and reload data
                input_field.clear()
                output_field.clear()
                self.load_currency_data()

            except SQLAlchemyError as e:
                session.rollback()
                self.show_error_message("Erreur", f"Échec de la mise à jour : {str(e)}")
            finally:
                session.close()

        except ValueError as e:
            self.show_error_message(
                "Erreur",
                "Veuillez entrer des montants valides pour l'entrée et la sortie",
            )

    def delete_currency(self, currency_id, row):
        confirmation = QMessageBox.question(
            self,
            "Confirmer la Suppression",
            "Êtes-vous sûr de vouloir supprimer cette devise ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirmation == QMessageBox.Yes:
            session = SessionLocal()
            try:
                currency = (
                    session.query(Currency).filter(Currency.id == currency_id).first()
                )
                if currency:

                    # Record the deleted data for audit log
                    deleted_data = {
                        "nom": currency.name,
                        "code": currency.code,
                        "solde": currency.balance,
                        "entree": currency.input,
                        "sortie": currency.output,
                    }
                    session.delete(currency)
                    session.commit()

                    # Log audit entry
                    log_audit_entry(
                        db_session=session,
                        table_name="Devise",
                        operation="SUPPRESSION",
                        record_id=currency_id,
                        user_id=self.user_id,
                        changes=deleted_data,
                    )
                    self.load_currency_data()
            except SQLAlchemyError as e:
                self.show_error_message(
                    "Erreur", f"Erreur lors de la suppression : {str(e)}"
                )
            finally:
                session.close()
