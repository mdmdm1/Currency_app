from PyQt5.QtWidgets import QLineEdit, QLabel, QDateEdit, QMessageBox
from PyQt5.QtCore import QDate
from dialogs.base_dialog import BaseDialog
from database.models import Currency
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError


class AddCurrencyDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Ajouter une devise", parent)
        self.setGeometry(250, 250, 500, 300)

    def create_form_fields(self):
        # Initialize input fields
        self.currency_name_input = QLineEdit()
        self.currency_name_input.setPlaceholderText("Nom de la devise (ex: USD, EUR)")

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Montant disponible")

        # Define fields with their labels
        fields = [
            ("Nom de la devise:", self.currency_name_input),
            ("Montant disponible:", self.amount_input),
        ]

        # Create rows with modern styling
        for label, widget in fields:
            self.create_input_row(label, widget)

    def validate_inputs(self):
        name = self.currency_name_input.text().strip()
        amount_str = self.amount_input.text().strip()

        if not name:
            QMessageBox.warning(
                self, "Erreur de validation", "Le nom de la devise est requis."
            )
            return False

        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self, "Erreur de validation", "Veuillez entrer un montant valide."
            )
            return False

        return True

    def get_values(self):
        return (
            self.currency_name_input.text().strip(),
            float(self.amount_input.text().strip()),
        )

    def on_submit(self):
        if not self.validate_inputs():
            return

        name = self.currency_name_input.text().strip()
        amount = float(self.amount_input.text().strip())

        session = SessionLocal()
        try:
            currency = session.query(Currency).filter_by(name=name).first()
            if currency:
                QMessageBox.warning(self, "Erreur", "La devise existe déjà")

                return

            else:
                # Create a new currency
                currency = Currency(name=name, balance=amount)
                session.add(currency)
                QMessageBox.information(
                    self, "Succès", "Une nouvelle devise a été ajoutée avec succès."
                )

            session.commit()
            self.accept()
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(
                self, "Erreur", f"Erreur lors de l'ajout ou de la mise à jour: {str(e)}"
            )
        finally:
            session.close()

    def populate_form_fields(self):
        session = SessionLocal()
        try:
            currency = session.query(Currency).filter_by(id=self.currency_id).first()
            if currency:
                self.currency_name_input.setText(currency.name)
                self.amount_input.setText(f"{currency.amount:.2f}")
            else:
                QMessageBox.warning(self, "Erreur", "La devise spécifiée n'existe pas.")
                self.reject()
        except SQLAlchemyError as e:
            QMessageBox.critical(
                self, "Erreur", f"Erreur lors de la récupération des données: {str(e)}"
            )
            self.reject()
        finally:
            session.close()
