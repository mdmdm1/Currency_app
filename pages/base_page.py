from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QSizePolicy,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QLabel,
)
from PyQt5.QtCore import Qt, QLocale

from utils.translation_manager import TranslationManager


class BasePage(QWidget):
    def __init__(self, parent=None, title="Base Page"):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle(title)
        # self.setStyleSheet(self.load_base_stylesheet())
        self.init_base_ui()

    def init_base_ui(self):
        """Initialize the base UI elements common to all pages"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 18, 18)
        self.layout.setSpacing(15)

        # Table Widget
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)

        self.layout.addWidget(self.table)

        # Total Amount Label
        self.total_amount_label = QLabel("Total: 0")
        self.total_amount_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.layout.addWidget(self.total_amount_label, alignment=Qt.AlignLeft)

        self.setLayout(self.layout)

    def load_base_stylesheet(self):
        """Load the base stylesheet common to all pages"""
        return """
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QTableWidget {
                border: 1px solid #ddd;
                background-color: #ffffff;
                alternate-background-color: #f5f5f5;
            }
            QTableWidget QHeaderView::section {
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                text-align: center;
            }
        """

    def setup_table_headers(self, headers):
        """Set up table headers with the given list of header labels"""
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

    def get_button_colors(self, base_color):
        """
        Get hover and pressed colors based on base color
        Returns tuple of (hover_color, pressed_color)
        """
        color_map = {
            "#007BFF": ("#0056b3", "#004085"),  # Blue (primary)
            "#28a745": ("#218838", "#1e7e34"),  # Green (success)
            "#dc3545": ("#c82333", "#bd2130"),  # Red (danger)
            "#ffc107": ("#e0a800", "#d39e00"),  # Yellow (warning)
            "#17a2b8": ("#138496", "#117a8b"),  # Cyan (info)
            "#6c757d": ("#5a6268", "#545b62"),  # Gray (secondary)
        }

        return color_map.get(
            base_color, ("#0056b3", "#004085")
        )  # Default to blue if color not found

    def add_action_buttons(self, row, identifier, buttons_config):
        """
        Add action buttons to a table row
        buttons_config is a list of dictionaries with keys:
        'text', 'color', 'callback', 'width'
        """
        self.table.setRowHeight(row, 50)

        # Create container widget with proper alignment
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")

        # Create layout with proper centering
        layout = QHBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)

        for button_config in buttons_config:
            button = QPushButton(button_config["text"])
            button.setFixedSize(button_config.get("width", 70), 35)

            base_color = button_config["color"]
            hover_color, pressed_color = self.get_button_colors(base_color)

            # Updated button stylesheet without the invalid property
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {base_color};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 0px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """
            )

            # Set size policy to help with centering
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            button.clicked.connect(
                lambda checked, i=identifier, r=row, c=button_config["callback"]: c(
                    i, r
                )
            )
            layout.addWidget(button)

        # Set the container as the cell widget
        self.table.setCellWidget(row, self.table.columnCount() - 1, container)

    def format_french_number(self, number):
        """Format a number according to the current locale."""
        locale = QLocale()
        if (
            self.parent_window.translation_manager.current_language == "ar"
        ):  # Check if the current language is Arabic
            locale = QLocale(
                QLocale.French, QLocale.France
            )  # Use Arabic locale for RTL
        return locale.toString(float(number), "f", 2)  # Format with 2 decimal places

    def show_error_message(self, title, message):
        """Show error message dialog"""
        QMessageBox.critical(self, title, message)

    def update_total_label(self, total, prefix="Total"):
        """Update the total amount label"""
        self.total_amount_label.setText(f"{prefix}: {self.format_french_number(total)}")

    def hide_total_label(self):
        """Hide the total amount label."""
        self.total_amount_label.hide()
