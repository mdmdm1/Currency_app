from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
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

from utils.translation_manager import TranslationManager


class BaseDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("./icons/app-icon.png"))
        # self.setGeometry(400, 65, 500, 400)

        self.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }

            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
            }

            QLineEdit:focus:focus {
                border: 1px solid #007BFF;
                background-color: #f8f9fa;
            }

            QWidget#buttons_widget {
                background-color: #f1f1f1;
                padding: 10px;
            }
        """
        )

        # )
        self.labels = []  # Initialize labels list in base class
        self.fields = []  # Initialize fields list in base class
        self.setup_ui()
        # self.center_on_screen()
        # Get the MainWindow instance from DebtPage's parent
        main_window = parent.parent()  # DebtPage's parent is MainWindow
        if hasattr(main_window, "language_switcher"):
            # Connect to the MainWindow's language_switcher signal
            main_window.language_switcher.language_changed.connect(
                self.on_language_changed
            )

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(25)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(self.main_layout)

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

        # Create form layout for fields
        self.form_layout = QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        self.create_form_fields()
        self.create_buttons()

        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.buttons_widget, alignment=Qt.AlignCenter)
        self.setLayout(self.main_layout)
        self.adjustSize()

    def create_input_row(self, label_text, input_widget):
        """Create a row with dynamic RTL/LTR ordering"""
        # Create labels and widgets
        label = QLabel(label_text)

        # Get current language direction
        is_rtl = False
        main_window = self._find_main_window()
        if main_window:
            is_rtl = main_window.translation_manager.current_language == "ar"

        """        # Configure widget alignment and direction based on language
        if is_rtl:
            input_widget.setLayoutDirection(Qt.RightToLeft)
            input_widget.setAlignment(Qt.AlignRight)
            label.setAlignment(Qt.AlignRight)
        else:
            input_widget.setLayoutDirection(Qt.LeftToRight)
            input_widget.setAlignment(Qt.AlignLeft)
            label.setAlignment(Qt.AlignLeft)
        """
        # Create a container to hold the row
        container = QWidget()
        row_layout = QHBoxLayout(container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        # Add widgets in the correct order based on language
        if is_rtl:
            row_layout.addWidget(input_widget, stretch=7)
            row_layout.addWidget(label, stretch=3)
        else:
            row_layout.addWidget(label, stretch=3)
            row_layout.addWidget(input_widget, stretch=7)

        # Add the container to the form layout
        self.form_layout.addWidget(container)

        return container

    def _find_main_window(self):
        """Helper to find main window"""
        widget = self.parent()
        while widget:
            if hasattr(widget, "translation_manager"):
                return widget
            widget = widget.parent()
        return None

    def create_buttons(self):
        self.buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(self.buttons_widget)
        buttons_layout.setSpacing(15)

        self.cancel_button = QPushButton(TranslationManager.tr("Annuler"))
        self.submit_button = QPushButton(TranslationManager.tr("Effectuer"))

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

    """def create_buttons(self):
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
    """

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
            background-color: #007BFF;
            color: white;
            font-size: 16px;
            padding: 10px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        """

    def _get_secondary_button_style(self):
        return """
        QPushButton {
            background-color: #6c757d;
            color: white;
            font-size: 16px;
            padding: 10px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #545b62;
        }
        """

    def validate_name(self, name):
        if not name.replace(" ", "").isalpha():
            self.show_error("Le champ nom doit contenir uniquement des lettres.")
            return False
        return True

    def validate_identite(self, identite):
        if not identite.strip():
            self.show_error("Le champ identite ne peut pas être vide. ")
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
