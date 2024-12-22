import sys
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
    QHeaderView,
    QWidget,
    QMessageBox,
    QLineEdit,
    QDateEdit,
    QLabel,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
import cx_Oracle
from datetime import datetime


def connect_to_db():
    dsn = cx_Oracle.makedsn("localhost", "1521", service_name="MANAGEMENT3")
    return cx_Oracle.connect(user="admin", password="2024", dsn=dsn)


class AddDepositDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un dépôt")
        self.setWindowIcon(QIcon("icon.jpg"))
        self.setGeometry(
            250, 250, 400, 300
        )  # Ajuster les dimensions pour plus d'espace

        # Initialiser les champs d'entrée
        self.person_name_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.deposit_date_input = QDateEdit(self)
        self.deposit_date_input.setCalendarPopup(True)  # Afficher un calendrier popup
        self.deposit_date_input.setDate(
            QDate.currentDate()
        )  # Date par défaut : aujourd'hui
        self.deposit_date_input.setDisplayFormat("dd-MMM-yy")  # Format de date

        # Mise en page principale
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Mise en page personnalisée pour chaque ligne
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)

        form_layout.addLayout(
            self._create_row(self.person_name_input, "Nom de la personne :")
        )
        form_layout.addLayout(self._create_row(self.amount_input, "Montant :"))
        form_layout.addLayout(
            self._create_row(self.deposit_date_input, "Date du dépôt :")
        )

        # Mise en page des boutons "Ajouter" et "Annuler"
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        # Bouton "Ajouter"
        self.submit_button = QPushButton("Ajouter")
        self.submit_button.setStyleSheet(self._get_button_style())
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setMinimumHeight(40)

        # Bouton "Annuler"
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setStyleSheet(self._get_button_style())
        self.cancel_button.clicked.connect(
            self.reject
        )  # Fermer la boîte de dialogue sans accepter
        self.cancel_button.setMinimumHeight(40)

        # Ajouter les boutons à la mise en page
        buttons_layout.addWidget(self.submit_button)
        buttons_layout.addWidget(self.cancel_button)

        # Widget pour les boutons
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        # Ajouter les mises en page à la disposition principale
        main_layout.addLayout(form_layout)
        main_layout.addWidget(buttons_widget, alignment=Qt.AlignCenter)

        # Centrer la boîte de dialogue sur l'écran
        self.center_on_screen()

    def center_on_screen(self):
        screen_rect = QApplication.desktop().screenGeometry()
        dialog_rect = self.geometry()
        x = (screen_rect.width() - dialog_rect.width()) // 2
        y = (screen_rect.height() - dialog_rect.height()) // 2
        self.move(x, y)

    def get_values(self):
        return (
            self.person_name_input.text(),
            self.amount_input.text(),
            self.deposit_date_input.text(),
        )

    def on_submit(self):
        if self.validate_inputs():
            self.accept()

    def validate_inputs(self):
        name = self.person_name_input.text()
        balance_text = self.amount_input.text()

        # Vérifier si le nom contient uniquement des lettres
        if not name.replace(" ", "").isalpha():
            QMessageBox.warning(
                self,
                "Erreur de validation",
                "Le champ Nom doit contenir uniquement des lettres.",
            )
            return False

        # Vérifier si le montant est un nombre valide
        try:
            balance = float(balance_text)
            self.amount_input.setText(f"{balance:.2f}")
        except ValueError:
            QMessageBox.warning(
                self,
                "Erreur de validation",
                "Le champ Montant doit contenir un nombre valide.",
            )
            return False

        return True

    def _create_row(self, input_widget, label_text):
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)

        label = QLabel(label_text)
        label.setStyleSheet("font-size: 16px; padding-right: 10px;")
        label.setMinimumWidth(120)

        input_widget.setAlignment(Qt.AlignRight)
        if isinstance(input_widget, QLineEdit):
            input_widget.setStyleSheet(self._get_line_edit_style())
        input_widget.setMinimumHeight(30)

        row_layout.addWidget(input_widget, alignment=Qt.AlignRight)
        row_layout.addWidget(label, alignment=Qt.AlignLeft)

        return row_layout

    def _get_line_edit_style(self):
        return """
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
                background-color: #fafafa;
                text-align: right;
            }
            QLineEdit:focus {
                border-color: #007BFF;
                background-color: #ffffff;
            }
        """

    def _get_button_style(self):
        return """
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """
