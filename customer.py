from datetime import datetime

class Customer:
    def __init__(self, name, identite, telephone, date_naiss):
        self._name = name  # Nom du client
        self._identite = identite  # Identité
        self._telephone = telephone  # Téléphone
        self._date_naiss = self._format_date(date_naiss)  # Date de Naissance

    def _format_date(self, date):
        """Formatte une date en 'YYYY-MM-DD' si elle est de type datetime."""
        if isinstance(date, datetime):
            return date.strftime("%Y-%m-%d")
        return date

    # Getters pour chaque attribut

    @property
    def name(self):
        return self._name

    @property
    def identite(self):
        return self._identite

    @property
    def telephone(self):
        return self._telephone

    @property
    def date_naiss(self):
        return self._date_naiss

  
