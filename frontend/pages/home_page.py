from datetime import datetime
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
import requests
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
from utils.translation_manager import TranslationManager
from pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, title=TranslationManager.tr("page d'accueil"))
        self.user_id = parent.user_id

        # Remove BasePage elements not needed in HomePage
        self.layout.removeWidget(self.table)
        self.layout.removeWidget(self.total_amount_label)
        self.table.deleteLater()
        self.total_amount_label.deleteLater()

        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the dashboard UI"""
        # Adjust layout settings to match original HomePage
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Statistics Grid
        self.stats_frame = self.create_stats_frame()
        self.layout.addWidget(self.stats_frame)

        # Recent Activity with ScrollArea
        self.activity_frame = self.create_activity_frame()
        self.layout.addWidget(self.activity_frame)

        self.stats_frame.setObjectName("stat-card")
        self.activity_frame.setObjectName("activity-frame")

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

        # Title label
        title_label = QLabel(TranslationManager.tr(title))
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("color: #666; font-size: 14px;")

        # Value label
        value_label = QLabel(str(TranslationManager.tr(value)))
        value_label.setObjectName("value_label")
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #007BFF;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        if subtitle:
            subtitle_label = QLabel(TranslationManager.tr(subtitle))
            subtitle_label.setStyleSheet("color: #888; font-size: 12px;")
            layout.addWidget(subtitle_label)

        return widget

    def create_stats_frame(self):
        """Create the statistics grid section"""
        frame = QFrame()
        frame.setObjectName("stats-frame")

        grid = QGridLayout(frame)
        grid.setSpacing(15)

        self.stats_widgets = {
            "currency": self.create_stat_widget("Total des Devises", "Chargement..."),
            "debt": self.create_stat_widget("Total des Dettes", "Chargement..."),
            "deposit": self.create_stat_widget("Total des Dépôts", "Chargement..."),
            "customers": self.create_stat_widget("Nombre de Clients", "Chargement..."),
        }

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

        title = QLabel(TranslationManager.tr("Activités Récentes"))
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;"
        )
        outer_layout.addWidget(title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(
            "QScrollArea { border: none; background-color: transparent; }"
        )

        self.activity_list = QFrame()
        self.activity_list.setStyleSheet("background-color: transparent;")
        self.activity_list_layout = QVBoxLayout(self.activity_list)
        self.activity_list_layout.setSpacing(5)

        placeholder = QLabel(
            TranslationManager.tr("Chargement des activités récentes...")
        )
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
            QLabel { font-size: 12px; padding: 2px; }
        """
        )

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        try:
            description = QLabel(
                f"{log['operation']} sur {log['table_name']} (ID: {log['record_id']})"
            )
            description.setStyleSheet("color: #333; font-size: 12px;")
            description.setWordWrap(True)

            timestamp_dt = datetime.fromisoformat(log["timestamp"])
            formatted_timestamp = timestamp_dt.strftime("%d/%m/%Y %H:%M")
            timestamp_label = QLabel(formatted_timestamp)
            timestamp_label.setStyleSheet("color: #888; font-size: 11px;")
            timestamp_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

            layout.addWidget(description, stretch=1)
            layout.addWidget(timestamp_label)

        except Exception as e:
            error_label = QLabel(
                TranslationManager.tr("Erreur lors du chargement de l'activité")
            )
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
        try:
            # Currency statistics
            currency_response = requests.get("http://127.0.0.1:8000/currencies/total")
            currency_total = currency_response.json().get("total_currencies", 0)
            self.update_stat_widget(
                self.stats_widgets["currency"],
                f"{self.format_french_number(currency_total)} {TranslationManager.tr('MRU')}",
            )

            # Debt statistics
            debt_response = requests.get("http://127.0.0.1:8000/debts/total")
            debt_total = debt_response.json().get("total_debts", 0)
            self.update_stat_widget(
                self.stats_widgets["debt"],
                f"{self.format_french_number(debt_total)} {TranslationManager.tr('MRU')}",
            )

            # Deposit statistics
            deposit_response = requests.get("http://127.0.0.1:8000/deposits/total")
            deposit_total = deposit_response.json().get("total_deposits", 0)
            self.update_stat_widget(
                self.stats_widgets["deposit"],
                f"{self.format_french_number(deposit_total)} {TranslationManager.tr('MRU')}",
            )

            # Customer count
            customer_response = requests.get("http://127.0.0.1:8000/customers/total")
            customer_count = customer_response.json().get("total_customers", 0)
            self.update_stat_widget(
                self.stats_widgets["customers"], str(customer_count)
            )

            # Recent activities
            response = requests.get("http://127.0.0.1:8000/audit_logs/recent")
            recent_logs = response.json() if response.status_code == 200 else []

            # Clear existing activities
            while self.activity_list_layout.count():
                item = self.activity_list_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            if recent_logs:
                for log in recent_logs:
                    self.activity_list_layout.addWidget(self.create_activity_item(log))
            else:
                no_activity = QLabel(TranslationManager.tr("Aucune activité récente"))
                no_activity.setStyleSheet("font-size: 12px; color: #666;")
                no_activity.setAlignment(Qt.AlignCenter)
                self.activity_list_layout.addWidget(no_activity)

            self.activity_list_layout.addStretch()

        except requests.RequestException as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                TranslationManager.tr(
                    "Une erreur est survenue lors du chargement des données."
                ),
            )

    def retranslate_ui(self):
        """Update UI elements on language change"""
        tr = TranslationManager.tr

        self.stats_widgets["currency"].findChild(QLabel, "title_label").setText(
            tr("Total des Devises")
        )
        self.stats_widgets["debt"].findChild(QLabel, "title_label").setText(
            tr("Total des Dettes")
        )
        self.stats_widgets["deposit"].findChild(QLabel, "title_label").setText(
            tr("Total des Dépôts")
        )
        self.stats_widgets["customers"].findChild(QLabel, "title_label").setText(
            tr("Nombre de Clients")
        )

        title_label = self.activity_frame.findChild(QLabel)
        if title_label:
            title_label.setText(tr("Activités Récentes"))

        placeholder = self.activity_list.findChild(QLabel)
        if placeholder:
            placeholder.setText(tr("Chargement des activités récentes..."))

    def showEvent(self, event):
        """Refresh data when the page becomes visible"""
        super().showEvent(event)
        self.load_data()
