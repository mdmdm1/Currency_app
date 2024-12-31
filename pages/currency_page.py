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


class CurrencyPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent, title="Gestion des Devises")
        self.init_ui()

    def init_ui(self):
        # Définir les en-têtes de table
        self.setup_table_headers(
            ["Devise", "Montant Disponible", "Entrée", "Sortie", "Actions"]
        )

        # Fixer la largeur de la colonne d'actions
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 190)

        # Section pour ajouter une nouvelle devise
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)

        self.new_currency_input = QLineEdit()
        self.new_currency_input.setPlaceholderText(
            "Entrez une nouvelle devise (ex. : EUR)"
        )

        add_button = QPushButton("Ajouter une Devise")
        add_button.clicked.connect(self.add_new_currency)

        top_layout.addWidget(self.new_currency_input)
        top_layout.addWidget(add_button)

        self.layout.insertWidget(0, top_container)

        # Charger les données initiales
        self.load_currency_data()

    def load_currency_data(self):
        session = SessionLocal()
        try:
            currencies = session.query(Currency).all()
            self.table.setRowCount(len(currencies))

            for row, currency in enumerate(currencies):
                # Currency name
                self.table.setItem(row, 0, QTableWidgetItem(currency.name))

                # Available balance (formatted in French style)
                formatted_balance = self.format_french_number(currency.balance)
                amount_item = QTableWidgetItem(formatted_balance)
                amount_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 1, amount_item)

                # Input field
                input_field = QLineEdit()
                input_field.setPlaceholderText("Montant à ajouter")
                self.table.setCellWidget(row, 2, input_field)

                # Output field
                output_field = QLineEdit()
                output_field.setPlaceholderText("Montant à soustraire")
                self.table.setCellWidget(row, 3, output_field)

                # Configurer les boutons d'action pour cette ligne
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

            # Mettre à jour le total
            total = sum(currency.balance for currency in currencies)
            self.update_total_label(total, "Total Disponible")

        except SQLAlchemyError as e:
            self.show_error_message(
                "Erreur", f"Erreur lors du chargement des devises : {str(e)}"
            )
        finally:
            session.close()

    def add_action_buttons(self, row, currency_id, buttons_config):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        self.table.setRowHeight(row, 50)

        for config in buttons_config:
            button = QPushButton(config["text"])
            button = QPushButton(config["text"])
            button.setFixedSize(config.get("width", 70), 35)

            base_color = config["color"]
            hover_color, pressed_color = self.get_button_colors(base_color)

            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {base_color};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 0px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """
            )

            button.setFixedWidth(config["width"])
            button.clicked.connect(
                lambda checked, cb=config["callback"]: cb(currency_id, row)
            )
            layout.addWidget(button)

        self.table.setCellWidget(row, 4, container)

    def add_new_currency(self):
        currency_name = self.new_currency_input.text().strip().upper()
        if not currency_name:
            self.show_error_message("Erreur", "Veuillez entrer un nom de devise")
            return

        session = SessionLocal()
        try:
            # Vérifier si la devise existe déjà
            if session.query(Currency).filter_by(name=currency_name).first():
                self.show_error_message("Erreur", "Cette devise existe déjà")
                return

            # Ajouter une nouvelle devise
            new_currency = Currency(name=currency_name, balance=0, input=0, output=0)
            session.add(new_currency)
            session.commit()

            # Vider le champ de saisie et recharger les données
            self.new_currency_input.clear()
            self.load_currency_data()

        except SQLAlchemyError as e:
            session.rollback()
            self.show_error_message(
                "Erreur", f"Échec de l'ajout de la devise : {str(e)}"
            )
        finally:
            session.close()

    def update_currency(self, currency_id, row):

        input_field = self.table.cellWidget(row, 2)
        output_field = self.table.cellWidget(row, 3)

        try:
            input_amount = float(input_field.text()) if input_field.text() else 0
            output_amount = float(output_field.text()) if output_field.text() else 0

            session = SessionLocal()
            try:
                currency = session.query(Currency).filter_by(id=currency_id).first()
                if not currency:
                    raise ValueError("Devise introuvable")

                # Mettre à jour les montants
                currency.input += input_amount
                currency.output += output_amount
                currency.balance = currency.balance + input_amount - output_amount

                session.commit()

                # Vider les champs de saisie et recharger les données
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
                    session.delete(currency)
                    session.commit()
                    self.load_currency_data()
            except SQLAlchemyError as e:
                self.show_error_message(
                    "Erreur", f"Erreur lors de la suppression : {str(e)}"
                )
            finally:
                session.close()
