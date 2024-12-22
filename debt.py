from datetime import datetime

class Debt:
    def __init__(self,amount, debt_date, paid_debt, current_debt, customer_id, created_by, created_at, updated_by, updated_at):
        self._amount = amount  # Montant Total de la dette
        self._debt_date = self._format_date(debt_date)  # Date de la Dette
        self._paid_debt = paid_debt  # Dette Payée
        self._current_debt = current_debt  # Dette Actuelle
        self._customer_id = customer_id  # ID du client
        self._created_by = created_by  # Créé par
        self._created_at = self._format_date(created_at)  # Date de Création
        self._updated_by = updated_by  # Mis à jour par
        self._updated_at = self._format_date(updated_at)  # Date de Mise à jour

    def _format_date(self, date):
        """Formatte une date en 'YYYY-MM-DD' si elle est de type datetime."""
        if isinstance(date, datetime):
            return date.strftime("%Y-%m-%d")
        return date

    # Getters pour chaque attribut

    @property
    def amount(self):
        return self._amount

    @property
    def debt_date(self):
        return self._debt_date

    @property
    def paid_debt(self):
        return self._paid_debt

    @property
    def current_debt(self):
        return self._current_debt

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def created_by(self):
        return self._created_by

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_by(self):
        return self._updated_by

    @property
    def updated_at(self):
        return self._updated_at
