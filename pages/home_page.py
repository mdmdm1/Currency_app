from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QSizePolicy,
    QScrollArea,
)
from PyQt5.QtCore import Qt
from sqlalchemy import func, desc
from database.database import SessionLocal
from database.models import (
    Currency,
    Debt,
    Deposit,
    Customer,
    TreasuryOperation,
    AuditLog,
    User,
)


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("Initializing HomePage")
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the dashboard UI"""
        # print("Setting up UI")

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Statistics Grid
        self.stats_frame = self.create_stats_frame()
        self.main_layout.addWidget(self.stats_frame)

        # Recent Activity with ScrollArea
        self.activity_frame = self.create_activity_frame()
        self.main_layout.addWidget(self.activity_frame)

        self.stats_frame.setObjectName("stat-card")
        self.activity_frame.setObjectName("activity-frame")
        # print("UI setup complete")

    def create_stat_widget(self, title, value, subtitle=""):
        """Create a styled widget for displaying statistics"""
        widget = QFrame()
        widget.setObjectName("stat-card")
        widget.setStyleSheet(
            """
            QFrame#stat-card {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                min-height: 120px;
                min-width: 200px;
            }
        """
        )

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title label with ID for easy finding
        title_label = QLabel(title)
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("color: #666; font-size: 14px;")

        # Value label with ID for easy finding
        value_label = QLabel(str(value))
        value_label.setObjectName("value_label")
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #007BFF;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #888; font-size: 12px;")
            layout.addWidget(subtitle_label)

        return widget

    def create_stats_frame(self):
        """Create the statistics grid section"""
        frame = QFrame()
        frame.setObjectName("stats-frame")

        grid = QGridLayout(frame)
        grid.setSpacing(15)

        # Create statistics widgets with default values
        self.stats_widgets = {
            "currency": self.create_stat_widget("Total des Devises", "Chargement..."),
            "debt": self.create_stat_widget("Total des Dettes", "Chargement..."),
            "deposit": self.create_stat_widget("Total des Dépôts", "Chargement..."),
            "customers": self.create_stat_widget("Nombre de Clients", "Chargement..."),
        }

        # Add widgets to grid
        grid.addWidget(self.stats_widgets["currency"], 0, 0)
        grid.addWidget(self.stats_widgets["debt"], 0, 1)
        grid.addWidget(self.stats_widgets["deposit"], 1, 0)
        grid.addWidget(self.stats_widgets["customers"], 1, 1)

        return frame

    def create_activity_frame(self):
        """Create the recent activity section"""
        outer_frame = QFrame()
        outer_frame.setObjectName("activity-frame")
        outer_frame.setStyleSheet(
            """
            QFrame#activity-frame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """
        )

        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Activités Récentes")
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;"
        )
        outer_layout.addWidget(title)

        # Scroll Area for activities
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """
        )

        # Content widget for scroll area
        self.activity_list = QFrame()
        self.activity_list.setStyleSheet("background-color: transparent;")
        self.activity_list_layout = QVBoxLayout(self.activity_list)
        self.activity_list_layout.setSpacing(5)

        # Add a placeholder message
        placeholder = QLabel("Chargement des activités récentes...")
        placeholder.setAlignment(Qt.AlignCenter)
        self.activity_list_layout.addWidget(placeholder)

        scroll_area.setWidget(self.activity_list)
        outer_layout.addWidget(scroll_area)

        return outer_frame

    def create_activity_item(self, log):
        """Create a widget for a single activity item"""
        widget = QFrame()
        widget.setObjectName("activity-item")
        widget.setStyleSheet(
            """
            QFrame#activity-item {
                background-color: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                font-size: 12px;
                padding: 2px;
            }
        """
        )

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        try:
            # Activity description
            description = QLabel(
                f"{log.operation} sur {log.table_name} " f"(ID: {log.record_id})"
            )
            description.setStyleSheet(
                """
                color: #333;
                font-size: 12px;
            """
            )
            description.setWordWrap(True)

            # Timestamp
            timestamp = QLabel(log.timestamp.strftime("%d/%m/%Y %H:%M"))
            timestamp.setStyleSheet(
                """
                color: #888;
                font-size: 11px;
            """
            )
            timestamp.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

            layout.addWidget(description, stretch=1)
            layout.addWidget(timestamp)

        except Exception as e:
            print(f"Error creating activity item: {e}")
            error_label = QLabel("Erreur lors du chargement de l'activité")
            error_label.setStyleSheet("color: red; font-size: 12px;")
            layout.addWidget(error_label)

        return widget

    def update_stat_widget(self, widget, value):
        """Update the value of a stat widget"""
        value_label = widget.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(str(value))

    def load_data(self):
        """Load and display all dashboard data"""
        # print("Loading data")
        try:
            session = SessionLocal()
            try:
                # Currency statistics
                currency_total = (
                    session.query(func.sum(Currency.balance / Currency.rate)).scalar()
                    or 0
                )
                self.update_stat_widget(
                    self.stats_widgets["currency"],
                    f"{self.format_french_number(currency_total)} MRU",
                )

                # Debt statistics
                debt_total = session.query(func.sum(Debt.current_debt)).scalar() or 0
                self.update_stat_widget(
                    self.stats_widgets["debt"],
                    f"{self.format_french_number(debt_total)} MRU",
                )

                # Deposit statistics
                deposit_total = (
                    session.query(func.sum(Deposit.current_debt)).scalar() or 0
                )
                self.update_stat_widget(
                    self.stats_widgets["deposit"],
                    f"{self.format_french_number(deposit_total)} MRU",
                )

                # Customer count
                customer_count = session.query(func.count(Customer.id)).scalar() or 0
                self.update_stat_widget(
                    self.stats_widgets["customers"], str(customer_count)
                )

                # Clear previous activities
                while self.activity_list_layout.count():
                    child = self.activity_list_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

                # Recent activities
                recent_logs = (
                    session.query(AuditLog)
                    .order_by(desc(AuditLog.timestamp))
                    .limit(5)
                    .all()
                )

                if recent_logs:
                    for log in recent_logs:
                        activity_widget = self.create_activity_item(log)
                        self.activity_list_layout.addWidget(activity_widget)
                else:
                    no_activity = QLabel("Aucune activité récente")
                    no_activity.setStyleSheet("font-size: 12px; color: #666;")
                    no_activity.setAlignment(Qt.AlignCenter)
                    self.activity_list_layout.addWidget(no_activity)

                # Add stretch to push activities to the top
                self.activity_list_layout.addStretch()

            finally:
                session.close()

        except Exception as e:
            print(f"Error loading data: {e}")
            self.show_error_message(
                "Erreur", "Une erreur est survenue lors du chargement des données."
            )

    def format_french_number(self, amount):
        """Format number in French style"""
        try:
            integer_part, decimal_part = f"{amount:.2f}".split(".")
            integer_part = " ".join(
                [
                    integer_part[max(i - 3, 0) : i]
                    for i in range(len(integer_part), 0, -3)
                ][::-1]
            )
            return f"{integer_part},{decimal_part}"
        except Exception as e:
            print(f"Error formatting number: {e}")
            return str(amount)

    def show_error_message(self, title, message):
        """Show error message"""
        error_label = QLabel(f"{title}: {message}")
        error_label.setStyleSheet("color: red; font-size: 12px;")
        self.main_layout.addWidget(error_label)

    def showEvent(self, event):
        """Refresh data when the page becomes visible"""
        super().showEvent(event)
        self.load_data()
