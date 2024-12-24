from PyQt5.QtWidgets import QLineEdit, QDateEdit, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
from dialogs.base_dialog import BaseDialog
import cx_Oracle


def connect_to_db():
    dsn = cx_Oracle.makedsn("localhost", "1521", service_name="MANAGEMENT3")
    return cx_Oracle.connect(user="admin", password="2024", dsn=dsn)


class AddDepositDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Ajouter un dépôt", parent)
        self.setGeometry(250, 250, 500, 400)

    def create_form_fields(self):
        # Initialize input fields
        self.person_name_input = QLineEdit()
        self.person_id = QLineEdit()
        self.amount_input = QLineEdit()
        self.deposit_date_input = QDateEdit(self)
        self.deposit_date_input.setCalendarPopup(True)
        self.deposit_date_input.setDate(QDate.currentDate())

        self.deposit_date_input.setDisplayFormat("dd-MM-yyyy")

        print(self.deposit_date_input.styleSheet())

        # Define fields with their labels
        fields = [
            ("Nom de la personne:", self.person_name_input),
            ("Numéro d'identité:", self.person_id),
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
            self.amount_input.text(),
            self.deposit_date_input.text(),
        )

    def on_submit(self):
        # Validate inputs
        name = self.name_input.text().strip()
        is_valid_name = self.validate_name(name)
        is_valid_amount, amount = self.validate_amount(self.amount_input.text().strip())

        if not (is_valid_name and is_valid_amount):
            return

        deposit_date = self.date_input.date().toString("dd-MMM-yyyy")
        released_deposit = 0.0  # Default value for new deposit
        current_debt = (
            amount  # Assuming current debt equals the deposit amount initially
        )

        # Insert data into the database
        try:
            with connect_to_db() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    INSERT INTO deposits (person_name, amount, deposit_date, released_deposit, current_debt)
                    VALUES (:person_name, :amount, TRUNC(TO_DATE(:deposit_date, 'DD-MON-YY')), :released_deposit, :current_debt)
                    """,
                    {
                        "person_name": name,
                        "amount": float(amount),
                        "deposit_date": deposit_date,
                        "released_deposit": float(released_deposit),
                        "current_debt": float(current_debt),
                    },
                )
                connection.commit()

            QMessageBox.information(self, "Succès", "Dépôt ajouté avec succès.")
            self.accept()  # Close the dialog
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {str(e)}")
