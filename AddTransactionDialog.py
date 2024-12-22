import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,QWidget,QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Dialog pour ajouter une transaction
class AddTransactionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('إضافة معاملة')
        self.setWindowIcon(QIcon('icon.jpg'))
        self.setGeometry(250, 250, 400, 300)  # Adjusted height for more space

        # Initialize input fields
        self.name_input = QLineEdit()
        #self.input_input = QLineEdit()
        #self.output_input = QLineEdit()
        self.balance_input = QLineEdit()

        # Set default values
        self.input_input=0
        self.output_input=0

        # Set up main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Custom layout for each row
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)

        form_layout.addLayout(self._create_row(self.name_input, 'اسم العملية:'))
        #form_layout.addLayout(self._create_row(self.input_input, 'الإدخال:'))
        #form_layout.addLayout(self._create_row(self.output_input, 'الإخراج:'))
        form_layout.addLayout(self._create_row(self.balance_input, 'الرصيد:'))

        # Create buttons layout
        buttons_layout = QHBoxLayout()
        
        # Submit button
        self.submit_button = QPushButton('إضافة')
        self.submit_button.setStyleSheet(self._get_button_style())
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setMinimumHeight(40)

        #Cancel button
        self.cancel_button = QPushButton('إلغاء')
        self.cancel_button.setStyleSheet(self._get_button_style())
        self.cancel_button.clicked.connect(self.reject)  # This will close the dialog without accepting
        self.cancel_button.setMinimumHeight(40)

        # Add buttons to buttons layout
        buttons_layout.addWidget(self.submit_button)
        buttons_layout.addWidget(self.cancel_button)

        # Create a widget for the buttons layout
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        # Add custom layout and button to main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(buttons_widget, alignment=Qt.AlignCenter)
        # Center the dialog on the screen
        self.center_on_screen()

    def center_on_screen(self):
        # Get the screen geometry
        screen_rect = QApplication.desktop().screenGeometry()
        # Get the dialog geometry
        dialog_rect = self.geometry()
        # Calculate the position to center the dialog on the screen
        x = (screen_rect.width() - dialog_rect.width()) // 2
        y = (screen_rect.height() - dialog_rect.height()) // 2
        # Move the dialog to the calculated position
        self.move(x, y)

    def on_submit(self):
        if self.validate_inputs():
            self.accept()
        #else:
            # Show error message
            #QMessageBox.warning(self, 'خطأ في التحقق', 'يرجى تصحيح الأخطاء في المدخلات.')

    def validate_inputs(self):
        name = self.name_input.text()
        balance_text = self.balance_input.text()

        # Check if name contains only letters (could be adjusted for more specific requirements)
        if not name.replace(" ", "").isalpha():
            QMessageBox.warning(self, 'خطأ في التحقق', 'يجب أن يحتوي حقل الاسم على أحرف فقط.')
            return False

        # Check if balance is a valid number
        try:
            balance = float(balance_text)
            self.balance_input.setText(f"{balance:.2f}")
        except ValueError:
            QMessageBox.warning(self, 'خطأ في التحقق', 'يجب أن يحتوي حقل الرصيد على رقم صالح.')
            return False

        return True
        
    def get_values(self):
        return (
            self.name_input.text(),
            self.input_input,
            self.output_input,
            self.balance_input.text()
        )

    def _create_row(self, input_widget, label_text):
        # Create a horizontal layout for each row
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)

        # Create label
        label = QLabel(label_text)
        label.setStyleSheet('font-size: 16px; padding-right: 10px;')
        label.setMinimumWidth(120)

        # Set input widget styles
        input_widget.setAlignment(Qt.AlignRight)
        input_widget.setStyleSheet(self._get_line_edit_style())
        input_widget.setMinimumHeight(30)

        # Add label and input widget to the horizontal layout
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
                /* box-shadow: 0 0 5px rgba(0, 123, 255, 0.5); */
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
