from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
    QHeaderView,
    QMessageBox,
)
from PyQt5.QtCore import Qt
import cx_Oracle
from datetime import datetime


def connect_to_db():
    dsn = cx_Oracle.makedsn("localhost", "1521", service_name="MANAGEMENT3")
    return cx_Oracle.connect(user="admin", password="2024", dsn=dsn)


class MoneyManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Référence à la fenêtre principale
        self.setWindowTitle("Gestion des fonds")
        # self.setLayoutDirection(Qt.RightToLeft)  # Interface RTL (droite à gauche)
        self.setStyleSheet(self.load_stylesheet())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Tableau des transactions
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Nom de l'opération", "Entrée", "Sortie", "Solde"]
        )
        self.table.verticalHeader().setVisible(
            False
        )  # Masquer la colonne d'index vertical
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )  # Ajustement automatique des colonnes

        layout.addWidget(self.table)  # Ajouter le tableau au layout

        self.setLayout(layout)  # Appliquer le layout à la fenêtre

        self.load_transaction_data()  # Charger les données des transactions

    def load_stylesheet(self):
        return """
            QWidget {}
            QTableWidget {
                padding: 1px;
                border: 1px solid #ddd;
                background-color: #ffffff;
                alternate-background-color: #f5f5f5;
            }
            QTableWidget QHeaderView::section {
                background-color: #007BFF;
                color: white;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #007BFF;
                font-weight: bold;
                text-align: center;
            }
            QTableWidget::item {
                padding: 1px;
                border: 1px solid #ddd;
            }
            QTableWidget::item:selected {
                background-color: #007BFF;
                color: black;
            }
            QTableWidget::item:hover {
                background-color: #e9ecef;
            }
            QTableWidget::verticalHeader {
                border: 1px solid #ddd;
                visible: false;
            }
        """

    def load_transaction_data(self):
        with connect_to_db() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT TREASURY_OPERATIONS_ID, NAME, INPUT, OUTPUT, BALANCE FROM TREASURY_OPERATIONS ORDER BY TREASURY_OPERATIONS_ID DESC"
            )
            rows = cursor.fetchall()

            self.table.blockSignals(True)
            self.table.setRowCount(len(rows))

            self.previous_input = {
                row: 0.0 for row in range(self.table.rowCount())
            }  # Dictionnaire pour les anciennes valeurs d'entrée
            self.previous_output = {
                row: 0.0 for row in range(self.table.rowCount())
            }  # Dictionnaire pour les anciennes valeurs de sortie
            self.money_ids = {
                row: 0 for row in range(self.table.rowCount())
            }  # Dictionnaire pour les IDs des transactions

            for row_idx, row in enumerate(rows):
                for col_idx, item in enumerate(
                    row[1:]
                ):  # Ignore le premier élément (ID)
                    table_item = QTableWidgetItem(
                        f"{item:.2f}" if isinstance(item, (int, float)) else str(item)
                    )
                    table_item.setTextAlignment(Qt.AlignCenter)
                    if col_idx in [
                        0,
                        3,
                    ]:  # 0 pour 'Nom de l'opération' et 3 pour 'Solde'
                        table_item.setFlags(
                            table_item.flags() & ~Qt.ItemIsEditable
                        )  # Rendre non éditable
                    self.table.setItem(row_idx, col_idx, table_item)

                # Stocker les anciennes valeurs pour les entrées et sorties
                self.previous_input[row_idx] = float(row[2]) if row[2] else 0.0
                self.previous_output[row_idx] = float(row[3]) if row[3] else 0.0
                self.money_ids[row_idx] = row[0] if row[0] else 0

            self.table.blockSignals(False)

    def on_cell_changed(self, row, column):
        if column == 1:  # Colonne des entrées
            self.handle_input_output(row, column, True)
        elif column == 2:  # Colonne des sorties
            self.handle_input_output(row, column, False)

    def handle_input_output(self, row, column, is_input):
        input_item = self.table.item(row, column)
        input_value = input_item.text() if input_item else ""

        if input_value == "":  # Si la cellule est vide
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Réinitialisation des valeurs")
            msg_box.setText(
                "Aucune valeur saisie. Voulez-vous utiliser la valeur précédente ?"
            )
            yes_button = msg_box.addButton("Oui", QMessageBox.AcceptRole)
            no_button = msg_box.addButton("Non", QMessageBox.RejectRole)
            msg_box.setDefaultButton(yes_button)
            reply = msg_box.exec_()

            if reply == QMessageBox.AcceptRole:
                input_value = (
                    self.previous_input[row] if is_input else self.previous_output[row]
                )
                self.table.blockSignals(True)
                self.table.setItem(row, column, QTableWidgetItem(str(input_value)))
                self.table.blockSignals(False)
                self.calculate_balance(row, column, input_value, is_input)
            else:
                input_value = (
                    self.previous_input[row] if is_input else self.previous_output[row]
                )
                self.table.blockSignals(True)
                self.table.setItem(row, column, QTableWidgetItem(str(input_value)))
                self.table.blockSignals(False)
            return

        try:
            input_value = float(input_value)
        except ValueError:
            self.table.blockSignals(True)
            self.table.setItem(row, column, QTableWidgetItem("0.00"))
            self.table.blockSignals(False)
            return

        # Mise à jour du solde
        self.calculate_balance(row, column, input_value, is_input)

    def calculate_balance(self, row, column, input_value, is_input):
        input_value = float(input_value)
        if column == 1:
            output_value = (
                float(self.table.item(row, 2).text())
                if self.table.item(row, 2)
                else 0.0
            )
        else:
            output_value = (
                float(self.table.item(row, 1).text())
                if self.table.item(row, 1)
                else 0.0
            )

        balance = input_value - output_value
        balance_item = QTableWidgetItem(f"{balance:.2f}")
        self.table.blockSignals(True)
        self.table.setItem(row, 3, balance_item)
        self.table.blockSignals(False)
