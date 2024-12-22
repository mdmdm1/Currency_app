import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QDateEdit, QPushButton, QLabel
)
from PyQt5.QtCore import Qt, QDate

class EditDepositDialog(QDialog):
    def __init__(self, person_name, amount, deposit_date, released_deposit, current_debt):
        super().__init__()
        self.setWindowTitle('تعديل الإيداع')
        self.setGeometry(300, 300, 400, 300)

        # Initialize input widgets
        self.person_name_input = QLineEdit(person_name)
        self.amount_input = QLineEdit(amount)
        self.released_deposit_input = QLineEdit(released_deposit)
        self.current_debt_input = QLineEdit(current_debt)
        self.deposit_date_input = QDateEdit(self)
        self.deposit_date_input.setDate(QDate.currentDate())  # Set the default date to today
        self.deposit_date_input.setDisplayFormat("dd-MMM-yy")

        # Set up main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Custom layout for each row
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)

        form_layout.addLayout(self._create_row(self.person_name_input, 'اسم الشخص:'))
        form_layout.addLayout(self._create_row(self.amount_input, 'المبلغ:'))
        form_layout.addLayout(self._create_row(self.released_deposit_input, 'الإيداع المحرر:'))
        form_layout.addLayout(self._create_row(self.current_debt_input, 'الديون الحالية:'))
        form_layout.addLayout(self._create_row(self.deposit_date_input, 'تاريخ الإيداع:'))

        # Submit button
        self.submit_button = QPushButton('تحديث')
        self.submit_button.setStyleSheet(self._get_button_style())
        self.submit_button.clicked.connect(self.accept)

        # Add custom layout and button to main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)

    def get_values(self):
        return (
            self.person_name_input.text(),
            self.amount_input.text(),
            self.deposit_date_input.text(),
            self.released_deposit_input.text(),
            self.current_debt_input.text()
        )

    def _create_row(self, input_widget, label_text):
        # Create a horizontal layout for each row
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)

        # Set input widget styles
        input_widget.setAlignment(Qt.AlignRight)
        input_widget.setStyleSheet(self._get_line_edit_style())
        input_widget.setMinimumHeight(30)

        # Create label
        label = QLabel(label_text)
        label.setStyleSheet('font-size: 16px; padding-right: 10px;')
        label.setMinimumWidth(120)
        
        # Add input widget and label to the horizontal layout
        row_layout.addWidget(input_widget)
        row_layout.addWidget(label)

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
                box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
            }
            QDateEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
                background-color: #fafafa;
                text-align: right;
            }
            QDateEdit:focus {
                border-color: #007BFF;
                background-color: #ffffff;
                box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
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


