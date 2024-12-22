from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QDialog,
    QMessageBox,
    QHBoxLayout,
    QHeaderView,
)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
import cx_Oracle
import hashlib

from addemployees_page import AddEmployeeDialog
from edit_employee import EditEmployeeDialog


def connect_to_db():
    """Connect to the Oracle database with specified DSN settings."""
    dsn = cx_Oracle.makedsn("localhost", "1521", service_name="MANAGEMENT3")
    return cx_Oracle.connect(user="admin", password="2024", dsn=dsn)


class EmployeesManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup main layout and window title
        main_layout = QVBoxLayout(self)
        self.setWindowTitle("Employee Management")

        # Employee table setup
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(5)
        self.employee_table.setHorizontalHeaderLabels(
            ["First Name", "Last Name", "Permission Role", "Edit", "Delete"]
        )
        self.employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add components to main layout
        main_layout.addWidget(self.employee_table)

        # Layout for the button at the bottom left
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # Adds empty space, pushing the button to the left

        # Create Add Employee button (Plus Icon, Blue)
        self.add_employee_button = QPushButton()
        self.add_employee_button.setIcon(
            QIcon("plus.jpeg")
        )  # Replace with your own icon path
        self.add_employee_button.setIconSize(QSize(40, 40))  # Size of the icon
        self.add_employee_button.setFixedSize(50, 50)  # Fixed size for the button
        self.add_employee_button.setStyleSheet(
            """
            background-color: #4CAF50;  # Color for the button background
            border-radius: 25px;  # Circular button style
            border: none;
        """
        )
        self.add_employee_button.clicked.connect(self.open_add_employee_dialog)

        button_layout.addWidget(
            self.add_employee_button
        )  # Add the button to the layout

        # Add the button layout at the bottom of the window
        main_layout.addLayout(button_layout)

        # Initial employee data load
        self.load_employees()

    def load_employees(self):
        """Load employee data from the database and populate the table."""
        with connect_to_db() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT e.FIRST_NAME, e.LAST_NAME, e.PERMISSION_ROLE, e.EMPLOYEE_ID
                FROM EMPLOYEE e
            """
            )
            employees = cursor.fetchall()

            self.employee_table.setRowCount(len(employees))
            for row, employee in enumerate(employees):
                self.employee_table.setItem(
                    row, 0, QTableWidgetItem(employee[0])
                )  # First Name
                self.employee_table.setItem(
                    row, 1, QTableWidgetItem(employee[1])
                )  # Last Name
                self.employee_table.setItem(
                    row, 2, QTableWidgetItem(employee[2] or "")
                )  # Permission Role

                # Edit button setup
                edit_button = QPushButton()
                edit_button.setIcon(QIcon("edit.png"))
                edit_button.clicked.connect(
                    lambda _, emp_id=employee[3]: self.edit_employee(emp_id)
                )

                # Delete button setup
                delete_button = QPushButton()
                delete_button.setIcon(QIcon("delete_icon.png"))
                delete_button.clicked.connect(
                    lambda _, emp_id=employee[3]: self.delete_employee(emp_id)
                )

                # Add buttons to table
                self.employee_table.setCellWidget(row, 3, edit_button)
                self.employee_table.setCellWidget(row, 4, delete_button)

    def open_add_employee_dialog(self):
        """Open dialog to add a new employee."""
        dialog = AddEmployeeDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            first_name = dialog.first_name_input.text()
            last_name = dialog.last_name_input.text()
            carte_ident = dialog.carte_ident_input.text()
            telephone = dialog.telephone_input.text()
            date_naiss = dialog.date_naiss_input.date().toString("yyyy-MM-dd")
            password_hash = hashlib.sha256(
                dialog.password_input.text().encode()
            ).hexdigest()
            permission_role = dialog.permission_role_input.currentText()

            self.save_employee(
                first_name,
                last_name,
                carte_ident,
                telephone,
                date_naiss,
                password_hash,
                permission_role,
            )

    def save_employee(
        self,
        first_name,
        last_name,
        carte_ident,
        telephone,
        date_naiss,
        password_hash,
        permission_role,
    ):
        """Save a new employee to the database."""
        try:
            with connect_to_db() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    INSERT INTO EMPLOYEE (FIRST_NAME, LAST_NAME, CARTE_IDENT, TELEPHONE, DATE_NAISS, PASSWORD, PERMISSION_ROLE) 
                    VALUES (:first_name, :last_name, :carte_ident, :telephone, TO_DATE(:date_naiss, 'YYYY-MM-DD'), :password, :permission_role)
                    """,
                    {
                        "first_name": first_name,
                        "last_name": last_name,
                        "carte_ident": carte_ident,
                        "telephone": telephone,
                        "date_naiss": date_naiss,
                        "password": password_hash,
                        "permission_role": permission_role,
                    },
                )
                connection.commit()
            self.load_employees()
            QMessageBox.information(self, "Success", "Employee added successfully.")
        except cx_Oracle.DatabaseError as e:
            QMessageBox.critical(self, "Database Error", f"Error adding employee: {e}")

    def edit_employee(self, emp_id):
        """Open dialog to edit an existing employee's details."""
        with connect_to_db() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT FIRST_NAME, LAST_NAME, CARTE_IDENT, TELEPHONE, 
                       TO_CHAR(DATE_NAISS, 'YYYY-MM-DD'), PERMISSION_ROLE 
                FROM EMPLOYEE 
                WHERE EMPLOYEE_ID = :id
            """,
                {"id": emp_id},
            )
            result = cursor.fetchone()

            if result:
                employee_data = {
                    "first_name": result[0],
                    "last_name": result[1],
                    "carte_ident": result[2],
                    "telephone": result[3],
                    "date_naiss": result[4],
                    "permission_role": result[5],
                }

                dialog = EditEmployeeDialog(self, employee_data=employee_data)
                if dialog.exec_() == QDialog.Accepted:
                    updated_data = dialog.get_updated_data()

                    try:
                        with connect_to_db() as connection:
                            cursor = connection.cursor()
                            cursor.execute(
                                """
                                UPDATE EMPLOYEE 
                                SET FIRST_NAME = :first_name, LAST_NAME = :last_name,
                                    CARTE_IDENT = :carte_ident, TELEPHONE = :telephone,
                                    DATE_NAISS = TO_DATE(:date_naiss, 'YYYY-MM-DD'), 
                                    PERMISSION_ROLE = :permission_role
                                WHERE EMPLOYEE_ID = :id
                            """,
                                {**updated_data, "id": emp_id},
                            )
                            connection.commit()
                        self.load_employees()
                        QMessageBox.information(
                            self, "Success", "Employee updated successfully."
                        )
                    except cx_Oracle.DatabaseError as e:
                        QMessageBox.critical(
                            self, "Database Error", f"Error updating employee: {e}"
                        )
            else:
                QMessageBox.warning(self, "Not Found", "Employee not found.")

    def delete_employee(self, emp_id):
        """Delete an employee from the database after confirmation."""
        reply = QMessageBox.question(
            self,
            "Delete Employee",
            f"Are you sure you want to delete employee {emp_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                with connect_to_db() as connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        "DELETE FROM EMPLOYEE WHERE EMPLOYEE_ID = :id", {"id": emp_id}
                    )
                    connection.commit()
                self.load_employees()
                QMessageBox.information(
                    self, "Success", f"Employee {emp_id} deleted successfully."
                )
            except cx_Oracle.DatabaseError as e:
                QMessageBox.critical(
                    self, "Database Error", f"Error deleting employee: {e}"
                )
