from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import QObject, pyqtSignal


from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import pyqtSignal


class LanguageSwitcher(QComboBox):
    # Signal for language change
    language_changed = pyqtSignal(str)

    def __init__(self, translation_manager, parent=None):
        super().__init__(parent)
        self.translation_manager = translation_manager
        self.lang_code = translation_manager.current_language
        self.languages = {"English": "en", "Français": "fr", "العربية": "ar"}

        # Add language options to combo box
        for lang_name in self.languages.keys():
            self.addItem(lang_name)

        # Set initial selection
        self.update_current_language()

        # Connect signal
        self.currentTextChanged.connect(self.change_language)

    def change_language(self, lang_name):
        """Handle language change when user selects a new language"""
        # Get the language code for the selected language name
        self.lang_code = self.languages[lang_name]

        # Load the new language using translation manager
        if self.translation_manager.load_language(self.lang_code):
            # Emit signal that language has changed
            self.language_changed.emit(self.lang_code)

    def update_current_language(self):
        """Update the combo box selection to match current language"""
        # Find language name for current language code
        current_lang_name = next(
            (name for name, code in self.languages.items() if code == self.lang_code),
            "Français",  # Default to French if current language not found
        )

        # Set the combo box selection
        self.setCurrentText(current_lang_name)
