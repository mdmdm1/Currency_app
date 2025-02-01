from datetime import datetime
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QHBoxLayout,
    QMessageBox,
    QDialog,
)
from PyQt5.QtCore import QDate
from database.models import Customer, Debt
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError

from utils.translation_manager import TranslationManager


class ConfirmationDialog(QDialog):
    """A dialog to confirm the exchange rate before saving."""

    def __init__(
        self, source_currency, target_currency, amount, converted_amount, parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle(TranslationManager.tr("Confirm Exchange"))
        self.setModal(True)

        # Create layout
        layout = QVBoxLayout(self)

        # Add exchange information
        layout.addWidget(
            QLabel(TranslationManager.tr("Source Currency:") + f" {source_currency}")
        )
        layout.addWidget(
            QLabel(TranslationManager.tr("Target Currency:") + f" {target_currency}")
        )
        layout.addWidget(
            QLabel(TranslationManager.tr("Amount:") + f" {amount} {source_currency}")
        )
        layout.addWidget(
            QLabel(
                TranslationManager.tr("Converted Amount:")
                + f" {converted_amount} {target_currency}"
            )
        )

        # Buttons
        button_layout = QHBoxLayout()
        self.confirm_button = QPushButton(TranslationManager.tr("Confirm"))
        self.cancel_button = QPushButton(TranslationManager.tr("Cancel"))

        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
