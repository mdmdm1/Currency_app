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
from PyQt5.QtCore import Qt


class BasePage(QWidget):
    def __init__(self, parent=None, title="Base Page"):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle(title)
        self.setStyleSheet(self.load_base_stylesheet())
        self.init_base_ui()

    def init_base_ui(self):
        """Initialize the base UI elements common to all pages"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
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

    def add_action_buttons(self, row, identifier, buttons_config):
        """
        Add action buttons to a table row
        buttons_config is a list of dictionaries with keys:
        'text', 'color', 'callback', 'width'
        """
        self.table.setRowHeight(row, 50)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        for button_config in buttons_config:
            button = QPushButton(button_config["text"])
            button.setFixedSize(button_config.get("width", 70), 35)
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {button_config['color']};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.get_hover_color(button_config['color'])};
                }}
                QPushButton:pressed {{
                    background-color: {self.get_pressed_color(button_config['color'])};
                }}
            """
            )
            button.clicked.connect(
                lambda checked, i=identifier, c=button_config["callback"]: c(i)
            )
            layout.addWidget(button)

        button_widget = QWidget()
        button_widget.setLayout(layout)
        self.table.setCellWidget(row, self.table.columnCount() - 1, button_widget)

    def get_hover_color(self, base_color):
        """Calculate hover color (slightly darker)"""
        # Simple implementation - you might want to enhance this
        return base_color.replace(")", ", 0.9)").replace("rgb", "rgba")

    def get_pressed_color(self, base_color):
        """Calculate pressed color (even darker)"""
        # Simple implementation - you might want to enhance this
        return base_color.replace(")", ", 0.8)").replace("rgb", "rgba")

    def format_french_number(self, amount):
        """Format number in French style"""
        integer_part, decimal_part = f"{amount:.2f}".split(".")
        integer_part = " ".join(
            [integer_part[max(i - 3, 0) : i] for i in range(len(integer_part), 0, -3)][
                ::-1
            ]
        )
        return f"{integer_part},{decimal_part}"

    def show_error_message(self, title, message):
        """Show error message dialog"""
        QMessageBox.critical(self, title, message)

    def update_total_label(self, total, prefix="Total"):
        """Update the total amount label"""
        self.total_amount_label.setText(f"{prefix}: {self.format_french_number(total)}")
