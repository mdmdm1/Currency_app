from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QDateEdit,
    QPushButton,
    QLabel,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QDate
import cx_Oracle
from PyQt5.QtGui import QIcon


# Connexion à la base de données Oracle
def connect_to_db():
    dsn = cx_Oracle.makedsn("localhost", "1521", service_name="MANAGEMENT3")
    return cx_Oracle.connect(user="admin", password="2024", dsn=dsn)


class AddDebtDialog(QDialog):
    def __init__(self, parent=None):
        super(AddDebtDialog, self).__init__(parent)
        self.setWindowTitle("Ajouter une dette")
        self.setWindowIcon(QIcon("icon.jpg"))
        self.setGeometry(250, 250, 400, 400)  # Dimensions ajustées pour plus d'espace

        # Initialisation des champs de saisie
        self.nom_personne_input = QLineEdit()
        self.montant_input = QLineEdit()
        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(
            True
        )  # Afficher un popup de calendrier lors du clic
        self.date_input.setDate(QDate.currentDate())  # Date par défaut à aujourd'hui
        self.date_input.setDisplayFormat("yyyy-MM-dd")  # Format de la date

        # Nouveaux champs
        self.identite_input = QLineEdit()  # Nouveau champ pour l'identité
        self.telephone_input = QLineEdit()  # Nouveau champ pour le téléphone
        self.date_naissance_input = QDateEdit(
            self
        )  # Nouveau champ pour la date de naissance
        self.date_naissance_input.setCalendarPopup(True)
        self.date_naissance_input.setDisplayFormat("yyyy-MM-dd")  # Format de la date

        # Configuration de la mise en page principale
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Mise en page pour chaque ligne
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)

        form_layout.addLayout(
            self._create_row("Nom de la personne:", self.nom_personne_input)
        )
        form_layout.addLayout(self._create_row("Montant:", self.montant_input))
        form_layout.addLayout(self._create_row("Date de la dette:", self.date_input))
        form_layout.addLayout(
            self._create_row("Identité:", self.identite_input)
        )  # Ajouter champ identité
        form_layout.addLayout(
            self._create_row("Téléphone:", self.telephone_input)
        )  # Ajouter champ téléphone
        form_layout.addLayout(
            self._create_row("Date de naissance:", self.date_naissance_input)
        )  # Ajouter champ date de naissance

        # Création de la mise en page pour les boutons
        buttons_layout = QHBoxLayout()

        # Bouton Soumettre
        self.submit_button = QPushButton("Ajouter")
        self.submit_button.setStyleSheet(self._get_button_style())
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setMinimumHeight(40)

        # Bouton Annuler
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setStyleSheet(self._get_button_style())
        self.cancel_button.clicked.connect(
            self.reject
        )  # Fermer la boîte de dialogue sans accepter

        # Ajout des boutons à la mise en page des boutons
        buttons_layout.addWidget(self.submit_button)
        buttons_layout.addWidget(self.cancel_button)

        # Création d'un widget pour la mise en page des boutons
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        # Ajout du widget contenant la mise en page des boutons à la mise en page principale
        main_layout.addLayout(form_layout)
        main_layout.addWidget(buttons_widget, alignment=Qt.AlignCenter)
        # Centrer la boîte de dialogue sur l'écran
        self.center_on_screen()

    def center_on_screen(self):
        # Obtenir la géométrie de l'écran
        screen_rect = QApplication.desktop().screenGeometry()
        # Obtenir la géométrie de la boîte de dialogue
        dialog_rect = self.geometry()
        # Calculer la position pour centrer la boîte de dialogue
        x = (screen_rect.width() - dialog_rect.width()) // 2
        y = (screen_rect.height() - dialog_rect.height()) // 2
        # Déplacer la boîte de dialogue à la position calculée
        self.move(x, y)

    def on_submit(self):
        if self.validate_inputs():
            self.accept()

    def validate_inputs(self):
        nom = self.nom_personne_input.text()
        montant_text = self.montant_input.text()

        # Vérifier si le nom contient uniquement des lettres
        if not nom.replace(" ", "").isalpha():
            QMessageBox.warning(
                self,
                "Erreur de validation",
                "Le champ nom doit contenir uniquement des lettres.",
            )
            return False

        # Vérifier si le montant est un nombre valide
        try:
            montant = float(montant_text)
            self.montant_input.setText(f"{montant:.2f}")
        except ValueError:
            QMessageBox.warning(
                self,
                "Erreur de validation",
                "Le champ montant doit contenir un nombre valide.",
            )
            return False

        return True

    def get_values(self):
        """Récupérer les valeurs saisies par l'utilisateur."""
        nom = self.nom_personne_input.text()
        montant = self.montant_input.text()
        date_dette = self.date_input.date().toString(
            "yyyy-MM-dd"
        )  # Utiliser la date du champ d'entrée
        identity = self.identite_input.text()  # Récupérer l'identité
        telephone = self.telephone_input.text()  # Récupérer le téléphone
        date_naissance = self.date_naissance_input.date().toString(
            "yyyy-MM-dd"
        )  # Récupérer la date de naissance
        return nom, montant, date_dette, identity, telephone, date_naissance

    def _create_row(self, label_text, input_widget):
        # Créer une mise en page horizontale pour chaque ligne
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)

        # Créer l'étiquette
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 16px; padding-right: 10px;")
        label.setMinimumWidth(120)

        # Définir les styles du widget d'entrée
        input_widget.setAlignment(Qt.AlignRight)
        input_widget.setStyleSheet(self._get_line_edit_style())
        input_widget.setMinimumHeight(30)

        # Ajouter l'étiquette et le widget d'entrée à la mise en page horizontale
        row_layout.addWidget(label, alignment=Qt.AlignLeft)  # Étiquette à gauche
        row_layout.addWidget(
            input_widget, alignment=Qt.AlignRight
        )  # Champ d'entrée à droite

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
