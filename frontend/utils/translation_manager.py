from PyQt5.QtCore import QTranslator, QCoreApplication, pyqtSignal
from pathlib import Path


class TranslationManager:
    _instance = None

    def __new__(cls, app=None):
        if cls._instance is None:
            cls._instance = super(TranslationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, app=None):
        if self._initialized:
            return

        self.app = app  # Ensure this is the QApplication instance
        self.translator = QTranslator()
        self.current_language = "fr"  # Default language
        self.translations_dir = Path("translations")
        self._initialized = True

        # Initialize translation
        self.load_language(self.current_language)

    def load_language(self, language_code):
        self.clear_translations()
        if language_code == "fr":
            return True
        # Remove previous translation
        self.app.removeTranslator(self.translator)

        # Recreate translator
        self.translator = QTranslator()

        # Load new translation file
        translation_file = self.translations_dir / f"app_{language_code}.qm"
        print(f"Attempting to load translation file: {translation_file}")
        print(f"File exists: {translation_file.exists()}")

        if self.translator.load(str(translation_file)):
            result = self.app.installTranslator(self.translator)
            print(f"Translator installation result: {result}")

            self.current_language = language_code

            return True

        print(f"Failed to load translation file: {translation_file}")
        return False

    @staticmethod
    def tr(text):
        """Translate text using the current translation"""
        return QCoreApplication.translate("TranslationManager", text)

    def clear_translations(self):
        """Clear any loaded translations, falling back to the original strings."""
        self.app.removeTranslator(self.translator)
        self.current_language = "fr"  # Reset to original language
