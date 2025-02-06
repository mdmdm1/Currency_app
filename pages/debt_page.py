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
from dialogs.pay_debt_dialog import PayDebtDialog
from database.models import Customer, Debt
from database.database import SessionLocal
from pages.base_page import BasePage
from utils.translation_manager import TranslationManager
from utils.audit_logger import log_audit_entry


class DebtPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, title=TranslationManager.tr("Gestion des Dettes"))
        self.user_id = parent.user_id
        self.init_ui()

    def init_ui(self):
        # Set up table headers
        self.setup_table_headers(
            [
                TranslationManager.tr("Nom"),
                TranslationManager.tr("NNI"),
                TranslationManager.tr("Date de création"),
                TranslationManager.tr("Montant total"),
                TranslationManager.tr("Montant payé"),
                TranslationManager.tr("Dette actuelle"),
                TranslationManager.tr("Actions"),
            ]
        )

        # Set fixed width for actions column
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 170)

        # Add debt button
        self.add_button = QPushButton(TranslationManager.tr("Ajouter une dette"))
        self.add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.add_button.clicked.connect(self.add_debt)
        self.layout.addWidget(self.add_button, alignment=Qt.AlignBottom | Qt.AlignRight)

        self.load_debt_data()

    def load_debt_data(self):
        session = SessionLocal()
        try:
            debts = (
                session.query(Debt)
                .join(Customer, Debt.customer_id == Customer.id)
                .add_columns(
                    Customer.name,
                    Customer.identite,
                    Debt.id,
                    Debt.created_at,
                    Debt.amount,
                    Debt.paid_debt,
                    Debt.current_debt,
                )
                .filter(Debt.current_debt > 0)
                .all()
            )

            self.table.setRowCount(len(debts))
            total_debt = 0

            for row_idx, row in enumerate(debts):
                (
                    customer_name,
                    identite,
                    debt_id,
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

                    # Disable editing for the item
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    self.table.setItem(row_idx, col_idx, item)
                # Configure action buttons for this row
                buttons_config = [
                    {
                        "text": TranslationManager.tr("Payer"),
                        "color": "#ffc107",
                        "callback": self.pay_debt,
                        "width": 70,
                    },
                    {
                        "text": TranslationManager.tr("Supprimer"),
                        "color": "#dc3545",
                        "callback": self.delete_debt,
                        "width": 76,
                    },
                ]
                self.add_action_buttons(row_idx, debt_id, buttons_config)

            self.total_prefix = TranslationManager.tr("Total Dette")
            self.update_total_label(total_debt, TranslationManager.tr("Total Dette"))

        except SQLAlchemyError as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                f"{TranslationManager.tr('Erreur lors du chargement')}: {str(e)}",
            )
        finally:
            session.close()

    def add_debt(self):
        dialog = AddDebtDialog(self)
        if dialog.exec_():
            self.load_debt_data()

    def pay_debt(self, debt_id, row):
        dialog = PayDebtDialog(self, debt_id=debt_id)
        if dialog.exec_():
            self.load_debt_data()

    def delete_debt(self, debt_id, row):
        confirmation = QMessageBox.question(
            self,
            TranslationManager.tr("Confirmer la suppression"),
            TranslationManager.tr("Êtes-vous sûr de vouloir supprimer cette dette ?"),
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirmation == QMessageBox.Yes:
            session = SessionLocal()
            try:
                debt = session.query(Debt).filter(Debt.id == debt_id).first()
                customer = (
                    session.query(Customer).filter_by(id=Debt.customer_id).first()
                )

                if debt:
                    # Record the deleted data for audit log
                    deleted_data = {
                        TranslationManager.tr("name"): customer.name,
                        TranslationManager.tr("montant"): debt.amount,
                        TranslationManager.tr("date du dette"): debt.debt_date.strftime(
                            "%Y-%m-%d"
                        ),
                        TranslationManager.tr("dette actuelle"): debt.current_debt,
                        TranslationManager.tr("dette payer"): debt.paid_debt,
                        TranslationManager.tr(
                            "date du creation"
                        ): debt.created_at.strftime("%Y-%m-%d"),
                    }

                    session.delete(debt)
                    session.commit()

                    # Log audit entry
                    log_audit_entry(
                        db_session=session,
                        table_name=TranslationManager.tr("Dette"),
                        operation=TranslationManager.tr("SUPPRESSION"),
                        record_id=debt_id,
                        user_id=self.user_id,
                        changes=deleted_data,
                    )
                    self.load_debt_data()
            except SQLAlchemyError as e:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    f"{TranslationManager.tr('Erreur lors de la suppression')}: {str(e)}",
                )
            finally:
                session.close()

    def retranslate_ui(self):
        # Update the window title
        self.setWindowTitle(TranslationManager.tr("Gestion des Dettes"))

        # Update table headers
        self.setup_table_headers(
            [
                TranslationManager.tr("Nom"),
                TranslationManager.tr("NNI"),
                TranslationManager.tr("Date de création"),
                TranslationManager.tr("Montant total"),
                TranslationManager.tr("Montant payé"),
                TranslationManager.tr("Dette actuelle"),
                TranslationManager.tr("Actions"),
            ]
        )

        # Update the Add Debt button text
        for widget in self.layout.children():
            if isinstance(widget, QPushButton) and widget.text() != "":
                widget.setText(TranslationManager.tr("buttons.Update Debt"))

        self.add_button.setText(TranslationManager.tr("Ajouter une dette"))

        # Update the AddDebtDialog if it's open
        # if hasattr(self, "add_debt_dialog"):
        #    self.add_debt_dialog.retranslate_ui()

        self.load_debt_data()
