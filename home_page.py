import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class HomePage(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard - Employés")
        self.setGeometry(100, 100, 900, 600)

        # Layout principal
        main_layout = QVBoxLayout()

        # Section des statistiques des employés
        stats_frame = QFrame()
        stats_layout = QVBoxLayout()

        stats_title = QLabel("<b>Statistiques des Employés</b>")
        stats_title.setAlignment(Qt.AlignCenter)
        stats_title.setFont(QFont("Arial", 18, QFont.Bold))
        stats_layout.addWidget(stats_title)

        # Exemple de statistiques
        stats_data = [
            ("Total d'employés :", "120"),
            ("Employés actifs :", "100"),
            ("Employés en congé :", "15"),
            ("Nouvelles recrues :", "5")
        ]

        # Ajouter les statistiques par paires
        for i in range(0, len(stats_data), 2):
            stat_pair_layout = QHBoxLayout()  # Créer un layout horizontal pour chaque paire
            for j in range(2):
                if i + j < len(stats_data):  # Vérifier que l'index est dans les limites
                    label, value = stats_data[i + j]
                    stat_label = QLabel(f"{label} <b>{value}</b>")
                    stat_label.setAlignment(Qt.AlignCenter)
                    stat_label.setFont(QFont("Arial", 14))
                    stat_label.setStyleSheet("padding: 10px;")  # Ajout d'un peu d'espace autour du texte
                    stat_pair_layout.addWidget(stat_label)  # Ajouter la statistique au layout horizontal
            stats_layout.addLayout(stat_pair_layout)  # Ajouter le layout horizontal au layout principal

        stats_frame.setLayout(stats_layout)
        stats_frame.setFrameShape(QFrame.Box)
        stats_frame.setStyleSheet("""
            QFrame { 
                background-color: #e8f5e9;  /* Couleur de fond légère */
                border: 1px solid #4caf50;  /* Couleur de bordure */
                border-radius: 8px;
                padding: 10px;
            }
        """)

        # Section de la liste des employés récents
        recent_employees_frame = QFrame()
        recent_employees_layout = QVBoxLayout()

        recent_title = QLabel("<b>Liste des Employés Récents</b>")
        recent_title.setAlignment(Qt.AlignCenter)
        recent_title.setFont(QFont("Arial", 18, QFont.Bold))
        recent_employees_layout.addWidget(recent_title)

        # Exemple de liste d'employés récents
        recent_employees = [
            ("Alice Dupont", "Ressources Humaines"),
            ("Bob Martin", "Développement"),
            ("Charlie Petit", "Marketing")
        ]

        for name, department in recent_employees:
            employee_label = QLabel(f"<b>{name}</b> - {department}")
            employee_label.setAlignment(Qt.AlignLeft)
            employee_label.setFont(QFont("Arial", 14))
            employee_label.setStyleSheet("padding: 8px; background-color: #f9fbe7; border-radius: 5px;")  # Style amélioré pour les employés
            recent_employees_layout.addWidget(employee_label)

        recent_employees_frame.setLayout(recent_employees_layout)
        recent_employees_frame.setFrameShape(QFrame.Box)
        recent_employees_frame.setStyleSheet("""
            QFrame { 
                background-color: #f8f9fa;  /* Couleur de fond plus claire */
                border: 1px solid #ced4da;  /* Bordure légère */
                border-radius: 8px;
                padding: 10px;
            }
        """)

        # Ajout des sections au layout principal
        main_layout.addWidget(stats_frame)
        main_layout.addWidget(recent_employees_frame)

        # Définition du widget central
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


