from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QFrame,
    QDateEdit,
    QWidget,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon


class BaseDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("edit.png"))
        self.setGeometry(250, 250, 500, 450)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f8f9fa;
                border-radius: 10px;
            }
        """
        )

        self.setup_ui()
        self.center_on_screen()

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(25)
        self.main_layout.setContentsMargins(30, 30, 30, 30)

        # Add title
        title_label = QLabel(self.windowTitle())
        title_label.setStyleSheet(
            """
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """
        )
        self.main_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #e0e0e0;")
        self.main_layout.addWidget(separator)

        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(20)

        self.create_form_fields()
        self.create_buttons()

        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.buttons_widget, alignment=Qt.AlignCenter)
        self.setLayout(self.main_layout)

    def create_input_row(self, label_text, input_widget, reverse=False):
        container = QFrame()
        container.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QFrame:hover {
                border: 1px solid #bdbdbd;
            }
        """
        )

        row_layout = QHBoxLayout(container)
        row_layout.setContentsMargins(15, 10, 15, 10)
        row_layout.setSpacing(15)

        label = QLabel(label_text)
        label.setStyleSheet(
            """
            QLabel {
                color: #555;
                font-size: 15px;
                font-weight: 500;
            }
        """
        )
        label.setMinimumWidth(140)

        input_widget.setStyleSheet(self._get_input_style())
        input_widget.setMinimumHeight(35)

        # if isinstance(input_widget, QLineEdit):
        #    input_widget.setAlignment(Qt.AlignRight)

        if reverse:
            row_layout.addWidget(input_widget)
            row_layout.addWidget(label)
        else:
            row_layout.addWidget(label)
            row_layout.addWidget(input_widget)

        self.form_layout.addWidget(container)
        return container

    def create_buttons(self):
        self.buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(self.buttons_widget)
        buttons_layout.setSpacing(15)

        self.cancel_button = QPushButton("Annuler")
        self.submit_button = QPushButton("Effectuer")

        self.submit_button.setMinimumHeight(45)
        self.submit_button.setMinimumWidth(120)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setStyleSheet(self._get_primary_button_style())

        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setStyleSheet(self._get_secondary_button_style())

        self.submit_button.clicked.connect(self.on_submit)
        self.cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.submit_button)

    def _get_input_style(self):
        return """
            QLineEdit, QDateEdit {
                border: none;
                padding: 5px;
                font-size: 15px;
                background: transparent;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
                height: 20px;
                background: transparent;
            }
            QDateEdit::down-arrow {
                image: url(calendar.png); 
                width: 16px;
                height: 16px;
            }
        """

    def _get_primary_button_style(self):
        return """
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton:pressed { background-color: #0a58ca; }
        """

    def _get_secondary_button_style(self):
        return """
            QPushButton {
                background-color: white;
                color: #6c757d;
                border: 1px solid #6c757d;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                color: #5c636a;
            }
            QPushButton:pressed { background-color: #f0f0f0; }
        """

    def validate_name(self, name):
        if not name.replace(" ", "").isalpha():
            self.show_error("Le champ nom doit contenir uniquement des lettres.")
            return False
        return True

    def validate_amount(self, amount_text):
        try:
            amount = float(amount_text)
            return True, amount
        except ValueError:
            self.show_error("Le champ montant doit contenir un nombre valide.")
            return False, None

    def show_error(self, message):
        QMessageBox.warning(self, "Erreur de validation", message)

    def center_on_screen(self):
        screen_rect = QApplication.desktop().screenGeometry()
        dialog_rect = self.geometry()
        x = (screen_rect.width() - dialog_rect.width()) // 2
        y = (screen_rect.height() - dialog_rect.height()) // 2
        self.move(x, y)

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

    def format_french_number(self, amount):
        """Format number in French style"""
        integer_part, decimal_part = f"{amount:.2f}".split(".")
        integer_part = " ".join(
            [integer_part[max(i - 3, 0) : i] for i in range(len(integer_part), 0, -3)][
                ::-1
            ]
        )
        return f"{integer_part},{decimal_part}"
