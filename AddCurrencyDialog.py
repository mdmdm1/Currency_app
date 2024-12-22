import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Dialog pour ajouter une devise
class AddCurrencyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('إضافة عملة')
        self.setWindowIcon(QIcon('icon.jpg'))
        self.setGeometry(250, 250, 400, 300)

        # Initialize input fields
        self.name_input = QLineEdit()
        self.input_input = 0
        self.output_input = 0
        self.balance_input = QLineEdit()

        # Set up main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Custom layout for each row
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)

        form_layout.addLayout(self._create_row(self.name_input, 'اسم العملة:'))
        form_layout.addLayout(self._create_row(self.balance_input, 'الرصيد:'))

        # Button layout with "إضافة" and "الغاء"
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Submit button
        self.submit_button = QPushButton('إضافة')
        self.submit_button.setStyleSheet(self._get_button_style())
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setMinimumHeight(40)
        
        # Cancel button
        self.cancel_button = QPushButton('إلغاء')
        self.cancel_button.setStyleSheet(self._get_button_style())
        self.cancel_button.clicked.connect(self.reject)  # This will close the dialog without accepting
        self.cancel_button.setMinimumHeight(40)

        # Add buttons to the button layout
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.cancel_button)
        

        # Add form layout and button layout to main layout
        main_layout.addLayout(form_layout)
        button_container = QHBoxLayout()
        button_container.addLayout(button_layout)
        button_container.setAlignment(Qt.AlignCenter)

        main_layout.addLayout(button_container)
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
        
    

    def _create_row(self, input_widget, label_text):
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)

        label = QLabel(label_text)
        label.setStyleSheet('font-size: 16px; padding-right: 10px;')
        label.setMinimumWidth(120)

        input_widget.setAlignment(Qt.AlignRight)
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
    
    def _get_cancel_button_style(self):
        return """
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #494e52;
            }
        """

    def _get_message_box_style(self):
        return """
            QMessageBox {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 10px;
            }
            QMessageBox QLabel {
                font-family: 'Cairo', sans-serif;
                font-size: 16px;
                color: #333333;
            }
            QMessageBox QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #0056b3;
            }
            QMessageBox QPushButton:pressed {
                background-color: #004085;
            }
        """

    def get_values(self):
        return (self.name_input.text(), 
                float(self.input_input), 
                float(self.output_input), 
                self.balance_input.text())


