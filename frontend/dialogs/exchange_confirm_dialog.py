from PyQt5.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QDialog,
)

from utils.translation_manager import TranslationManager


class ExchangeConfirmationDialog(QDialog):
    """A dialog to confirm the exchange rate before saving."""

    def __init__(
        self, source_currency, target_currency, amount, converted_amount, parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle(TranslationManager.tr("Confirmer l'échange"))
        self.setModal(True)

        # Create layout
        layout = QVBoxLayout(self)

        # Add exchange information
        layout.addWidget(
            QLabel(TranslationManager.tr("Devise source:") + f" {source_currency}")
        )
        layout.addWidget(
            QLabel(TranslationManager.tr("Devise cible:") + f" {target_currency}")
        )
        layout.addWidget(
            QLabel(TranslationManager.tr("Montant:") + f" {amount} {source_currency}")
        )
        layout.addWidget(
            QLabel(
                TranslationManager.tr("Montant converti:")
                + f" {converted_amount} {target_currency}"
            )
        )

        # Buttons
        button_layout = QHBoxLayout()
        self.confirm_button = QPushButton(TranslationManager.tr("Confirmer"))
        self.cancel_button = QPushButton(TranslationManager.tr("Annuler"))

        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
