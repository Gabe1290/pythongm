#!/usr/bin/env python3
"""
Language Manager for PyGameMaker IDE
Handles language selection and translation loading

Languages are auto-discovered from .qm files in the translations/ folder.
To add a new language:
1. Create pygm2_XX.ts file with translations
2. Compile to pygm2_XX.qm using lrelease
3. Done - it appears automatically in the language menu
"""

from pathlib import Path
from PySide6.QtCore import QTranslator, QLocale, QCoreApplication
from PySide6.QtWidgets import QApplication
from utils.config import Config


class LanguageManager:
    """Manages application translations and language switching"""

    # Language metadata: code -> (display_name, flag_emoji)
    # This is a reference table - languages only appear in menu if .qm file exists
    # Qt's standard translations (for buttons like Yes/No) are loaded separately
    LANGUAGE_INFO = {
        'en': ('English', '🇬🇧'),
        'fr': ('Français', '🇫🇷'),
        'es': ('Español', '🇪🇸'),
        'de': ('Deutsch', '🇩🇪'),
        'it': ('Italiano', '🇮🇹'),
        'pt': ('Português', '🇵🇹'),
        'ru': ('Русский', '🇷🇺'),
        'uk': ('Українська', '🇺🇦'),
        'zh': ('中文', '🇨🇳'),
        'ja': ('日本語', '🇯🇵'),
        'ko': ('한국어', '🇰🇷'),
        'ar': ('العربية', '🇸🇦'),
        'hi': ('हिन्दी', '🇮🇳'),
        'tr': ('Türkçe', '🇹🇷'),
        'pl': ('Polski', '🇵🇱'),
        'nl': ('Nederlands', '🇳🇱'),
        'sv': ('Svenska', '🇸🇪'),
        'da': ('Dansk', '🇩🇰'),
        'no': ('Norsk', '🇳🇴'),
        'fi': ('Suomi', '🇫🇮'),
        'cs': ('Čeština', '🇨🇿'),
        'el': ('Ελληνικά', '🇬🇷'),
        'he': ('עברית', '🇮🇱'),
        'th': ('ไทย', '🇹🇭'),
        'vi': ('Tiếng Việt', '🇻🇳'),
        'id': ('Bahasa Indonesia', '🇮🇩'),
        'ms': ('Bahasa Melayu', '🇲🇾'),
        'ro': ('Română', '🇷🇴'),
        'hu': ('Magyar', '🇭🇺'),
        'bg': ('Български', '🇧🇬'),
        'hr': ('Hrvatski', '🇭🇷'),
        'sk': ('Slovenčina', '🇸🇰'),
        'sl': ('Slovenščina', '🇸🇮'),
        'sr': ('Српски', '🇷🇸'),
        'ca': ('Català', '🇪🇸'),
        'eu': ('Euskara', '🇪🇸'),
        'gl': ('Galego', '🇪🇸'),
    }

    def __init__(self):
        self.current_language = Config.get('language', 'en')
        self.translator = QTranslator()
        self.qt_translator = QTranslator()  # For Qt's built-in strings (Yes/No buttons, etc.)
        self.translations_dir = Path(__file__).parent.parent / 'translations'

        # Ensure translations directory exists
        self.translations_dir.mkdir(exist_ok=True)

        # Cache for discovered languages
        self._available_languages = None

    def _discover_languages(self):
        """Auto-discover available languages from .qm files in translations folder"""
        languages = [('en', 'English', '🇬🇧')]  # English is always available (built-in)

        # Find all .qm files
        found_codes = set()
        for qm_file in self.translations_dir.glob('*.qm'):
            # Extract language code from filename
            # Supports: pygm2_XX.qm, pygamemaker_XX.qm
            name = qm_file.stem  # e.g., "pygm2_fr" or "pygamemaker_es"
            if '_' in name:
                code = name.split('_', 1)[1]  # Get part after first underscore
                if code and code != 'en':  # Skip English (it's built-in)
                    found_codes.add(code)

        # Build language list with metadata
        for code in sorted(found_codes):
            if code in self.LANGUAGE_INFO:
                name, flag = self.LANGUAGE_INFO[code]
            else:
                # Unknown language - use code as name and generic flag
                name = code.upper()
                flag = '🌐'
            languages.append((code, name, flag))

        return languages

    def get_available_languages(self):
        """Get list of available languages (auto-discovered from .qm files)"""
        if self._available_languages is None:
            self._available_languages = self._discover_languages()
        return self._available_languages

    def refresh_available_languages(self):
        """Force re-discovery of available languages"""
        self._available_languages = None
        return self.get_available_languages()

    def get_current_language(self):
        """Get current language code"""
        return self.current_language

    def get_current_language_name(self):
        """Get current language display name"""
        for code, name, flag in self.get_available_languages():
            if code == self.current_language:
                return f"{flag} {name}"
        return "🇬🇧 English"

    def set_language(self, language_code: str):
        """Set the application language"""
        print(f"🌐 set_language called with: {language_code}")
        print(f"   Current language: {self.current_language}")

        if language_code == self.current_language:
            print(f"   ✅ Already set to {language_code}")
            return True  # Already set

        # Remove old translators
        app = QApplication.instance()
        print(f"   App instance: {app}")
        if app:
            app.removeTranslator(self.translator)
            app.removeTranslator(self.qt_translator)
            print(f"   ✅ Removed old translators")

        # Load new translation
        if language_code != 'en':  # English is the default, no translation needed
            # Try pygm2 first (newer, more complete translations), then fall back to pygamemaker
            translation_file = self.translations_dir / f"pygm2_{language_code}.qm"
            if not translation_file.exists():
                translation_file = self.translations_dir / f"pygamemaker_{language_code}.qm"

            print(f"   📁 Translation file: {translation_file}")
            print(f"   📁 File exists: {translation_file.exists()}")

            if translation_file.exists():
                print(f"   📂 Loading translation file...")
                if self.translator.load(str(translation_file)):
                    print(f"   ✅ Translation loaded successfully")
                    if app:
                        app.installTranslator(self.translator)
                        print(f"   ✅ Translator installed to app")

                        # Load Qt's built-in translations for standard buttons (Yes, No, OK, Cancel, etc.)
                        from PySide6.QtCore import QLibraryInfo
                        qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
                        if self.qt_translator.load(f"qtbase_{language_code}", qt_translations_path):
                            app.installTranslator(self.qt_translator)
                            print(f"   ✅ Qt base translator installed for {language_code}")
                        else:
                            print(f"   ⚠️ Qt base translations not found for {language_code}")

                        # Trigger retranslation of all existing widgets
                        from PySide6.QtCore import QEvent
                        from shiboken6 import isValid
                        for widget in app.allWidgets():
                            # Check if widget is still valid (not deleted)
                            if isValid(widget):
                                try:
                                    app.sendEvent(widget, QEvent(QEvent.Type.LanguageChange))
                                except RuntimeError:
                                    pass  # Widget was deleted during iteration
                        print(f"   🔄 Sent LanguageChange event to all widgets")

                    self.current_language = language_code
                    Config.set('language', language_code)
                    print(f"   ✅ Language set to: {language_code}")
                    return True
                else:
                    print(f"   ❌ Failed to load translation file: {translation_file}")
                    return False
            else:
                print(f"   ❌ Translation file not found: {translation_file}")
                print(f"Using English as fallback")
                # Still set the language code even if file doesn't exist
                self.current_language = language_code
                Config.set('language', language_code)
                return False
        else:
            # English selected - need to trigger retranslation to clear translations
            self.current_language = 'en'
            Config.set('language', 'en')

            # Trigger retranslation of all existing widgets so they revert to English
            if app:
                from PySide6.QtCore import QEvent
                from shiboken6 import isValid
                for widget in app.allWidgets():
                    # Check if widget is still valid (not deleted)
                    if isValid(widget):
                        try:
                            app.sendEvent(widget, QEvent(QEvent.Type.LanguageChange))
                        except RuntimeError:
                            pass  # Widget was deleted during iteration
                print(f"   🔄 Sent LanguageChange event to all widgets")

            print(f"   ✅ Set to English")
            return True

    def load_current_language(self):
        """Force load the current language translator (used at startup)"""
        print(f"🌐 load_current_language called, current: {self.current_language}")

        if self.current_language == 'en':
            print(f"   ✅ Using English (built-in)")
            return True

        # Force load the translator for current language
        app = QApplication.instance()
        if not app:
            print(f"   ❌ No app instance")
            return False

        # Try pygm2 first (newer, more complete translations), then fall back to pygamemaker
        translation_file = self.translations_dir / f"pygm2_{self.current_language}.qm"
        if not translation_file.exists():
            translation_file = self.translations_dir / f"pygamemaker_{self.current_language}.qm"

        print(f"   📁 Translation file: {translation_file}")
        print(f"   📁 File exists: {translation_file.exists()}")

        if translation_file.exists():
            print(f"   📂 Loading translation file...")
            if self.translator.load(str(translation_file)):
                print(f"   ✅ Translation loaded successfully")
                app.installTranslator(self.translator)
                print(f"   ✅ Translator installed to app")

                # Load Qt's built-in translations for standard buttons (Yes, No, OK, Cancel, etc.)
                from PySide6.QtCore import QLibraryInfo
                qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
                if self.qt_translator.load(f"qtbase_{self.current_language}", qt_translations_path):
                    app.installTranslator(self.qt_translator)
                    print(f"   ✅ Qt base translator installed for {self.current_language}")
                else:
                    print(f"   ⚠️ Qt base translations not found for {self.current_language}")

                return True
            else:
                print(f"   ❌ Failed to load translation file")
                return False
        else:
            print(f"   ❌ Translation file not found")
            return False

    def get_translation_file_path(self, language_code: str) -> Path:
        """Get path to translation file for a language"""
        # Try pygm2 first, then fall back to pygamemaker
        pygm2_path = self.translations_dir / f"pygm2_{language_code}.qm"
        if pygm2_path.exists():
            return pygm2_path
        return self.translations_dir / f"pygamemaker_{language_code}.qm"

    def is_translation_available(self, language_code: str) -> bool:
        """Check if translation file exists for a language"""
        if language_code == 'en':
            return True  # English is built-in
        # Check both naming conventions
        pygm2_path = self.translations_dir / f"pygm2_{language_code}.qm"
        pygamemaker_path = self.translations_dir / f"pygamemaker_{language_code}.qm"
        return pygm2_path.exists() or pygamemaker_path.exists()


# Global language manager instance
_language_manager = None

def get_language_manager():
    """Get the global language manager instance"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager
