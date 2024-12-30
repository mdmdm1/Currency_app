from PyQt5.QtWidgets import (
    QTableWidgetItem,
    QPushButton,
    QSizePolicy,
    QHeaderView,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from sqlalchemy.exc import SQLAlchemyError
from dialogs.add_debt_dialog import AddDebtDialog
from dialogs.edit_debt_dialog import EditDebtDialog
from database.models import Customer, Debt
from database.database import SessionLocal
from pages.base_page import BasePage


class DebtPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent, title="Gestion des Dettes")
        self.init_ui()

    def init_ui(self):
        # Set up table headers
        self.setup_table_headers(
            [
                "Nom",
                "NNI",
                "Date de création",
                "Montant total",
                "Montant payé",
                "Dette actuelle",
                "Actions",
            ]
        )

        # Set fixed width for actions column
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 170)

        # Add debt button
        add_button = QPushButton("Ajouter une dette")
        add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_button.clicked.connect(self.add_debt)
        self.layout.addWidget(add_button, alignment=Qt.AlignBottom | Qt.AlignRight)

        self.load_debt_data()

    def load_debt_data(self):
        session = SessionLocal()
        try:
            debts = (
                session.query(Debt)
                .join(Customer, Debt.customer_id == Customer.id)
                .add_columns(
                    Customer.id,
                    Customer.name,
                    Customer.identite,
                    Debt.created_at,
                    Debt.amount,
                    Debt.paid_debt,
                    Debt.current_debt,
                )
                .all()
            )

            self.table.setRowCount(len(debts))
            total_debt = 0

            for row_idx, row in enumerate(debts):
                (
                    customer_id,
                    customer_name,
                    identite,
                    created_at,
                    total_amount,
                    paid_debt,
                    current_debt,
                ) = row[1:]
                total_debt += current_debt

                row_data = [
                    customer_name,
                    identite,
                    created_at.strftime("%Y-%m-%d"),
                    self.format_french_number(total_amount),
                    self.format_french_number(paid_debt),
                    self.format_french_number(current_debt),
                ]

                for col_idx, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)

                # Configure action buttons for this row
                buttons_config = [
                    {
                        "text": "Modifier",
                        "color": "#ffc107",
                        "callback": self.edit_debt,
                        "width": 70,
                    },
                    {
                        "text": "Supprimer",
                        "color": "#dc3545",
                        "callback": self.delete_debt,
                        "width": 70,
                    },
                ]
                self.add_action_buttons(row_idx, customer_id, buttons_config)

            self.update_total_label(total_debt, "Total Dette")

        except SQLAlchemyError as e:
            self.show_error_message("Erreur", f"Erreur lors du chargement: {str(e)}")
        finally:
            session.close()

    def add_debt(self):
        dialog = AddDebtDialog()
        if dialog.exec_():
            self.load_debt_data()

    def edit_debt(self, customer_id):
        dialog = EditDebtDialog(customer_id=customer_id)
        if dialog.exec_():
            self.load_debt_data()

    def delete_debt(self, customer_id):
        confirmation = QMessageBox.question(
            self,
            "Confirmer la suppression",
            "Êtes-vous sûr de vouloir supprimer cette dette ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirmation == QMessageBox.Yes:
            session = SessionLocal()
            try:
                debt = (
                    session.query(Debt).filter(Debt.customer_id == customer_id).first()
                )
                if debt:
                    session.delete(debt)
                    session.commit()
                    self.load_debt_data()
            except SQLAlchemyError as e:
                self.show_error_message(
                    "Erreur", f"Erreur lors de la suppression: {str(e)}"
                )
            finally:
                session.close()
