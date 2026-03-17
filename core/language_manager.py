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

import sys
from pathlib import Path
from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QApplication
from utils.config import Config

from core.logger import get_logger
logger = get_logger(__name__)


class LanguageManager:
    """Manages application translations and language switching"""

    # Translation file groups - these are loaded in order
    # Each group is a separate .qm file: pygm2_XX_group.qm
    TRANSLATION_GROUPS = ['core', 'editors', 'actions', 'dialogs', 'blockly', 'misc']

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
        self.translators = []  # List of QTranslator instances for split files
        self.qt_translator = QTranslator()  # For Qt's built-in strings (Yes/No buttons, etc.)
        # Use _MEIPASS base when running from PyInstaller bundle
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).parent.parent
        self.translations_dir = base / 'translations'
        self.flags_dir = base / 'resources' / 'flags'

        # Note: Don't create translations directory - it should exist in the package
        # Creating it would leave empty dirs in temp extraction folder

        # Cache for discovered languages
        self._available_languages = None

    def get_flag_icon_path(self, language_code: str) -> Path:
        """Get the path to the flag icon for a language code"""
        flag_path = self.flags_dir / f"{language_code}.png"
        if flag_path.exists():
            return flag_path
        # Fallback to globe icon for unknown languages
        globe_path = self.flags_dir / "globe.png"
        if globe_path.exists():
            return globe_path
        return None

    def _discover_languages(self):
        """Auto-discover available languages from .qm files in translations folder"""
        languages = [('en', 'English', '🇬🇧')]  # English is always available (built-in)

        # Find all .qm files
        found_codes = set()
        for qm_file in self.translations_dir.glob('*.qm'):
            # Extract language code from filename
            # Supports: pygm2_XX.qm, pygm2_XX_group.qm, pygamemaker_XX.qm
            name = qm_file.stem  # e.g., "pygm2_fr", "pygm2_fr_core", "pygamemaker_es"
            parts = name.split('_')
            if len(parts) >= 2:
                code = parts[1]  # Language code is always second part
                if code and code != 'en' and len(code) == 2:  # Skip English, only 2-char codes
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

    def _get_translation_files(self, language_code: str) -> list:
        """
        Get list of translation files for a language.
        Returns split files if available, otherwise falls back to monolithic file.
        """
        files = []

        # First, check for split files (pygm2_XX_group.qm)
        for group in self.TRANSLATION_GROUPS:
            split_file = self.translations_dir / f"pygm2_{language_code}_{group}.qm"
            if split_file.exists():
                files.append(split_file)

        # If split files found, use them
        if files:
            return files

        # Fall back to monolithic file (pygm2_XX.qm or pygamemaker_XX.qm)
        monolithic = self.translations_dir / f"pygm2_{language_code}.qm"
        if monolithic.exists():
            return [monolithic]

        legacy = self.translations_dir / f"pygamemaker_{language_code}.qm"
        if legacy.exists():
            return [legacy]

        return []

    def _remove_all_translators(self, app):
        """Remove all installed translators from the app."""
        for translator in self.translators:
            app.removeTranslator(translator)
        self.translators.clear()
        app.removeTranslator(self.qt_translator)

    def set_language(self, language_code: str):
        """Set the application language"""
        logger.debug(f"🌐 set_language called with: {language_code}")
        logger.debug(f"   Current language: {self.current_language}")

        if language_code == self.current_language:
            logger.debug(f"   ✅ Already set to {language_code}")
            return True  # Already set

        # Remove old translators
        app = QApplication.instance()
        logger.debug(f"   App instance: {app}")
        if app:
            self._remove_all_translators(app)
            logger.debug("   ✅ Removed old translators")

        # Load new translation
        if language_code != 'en':  # English is the default, no translation needed
            translation_files = self._get_translation_files(language_code)

            if translation_files:
                logger.debug(f"   📁 Found {len(translation_files)} translation file(s)")
                loaded_count = 0

                for tf in translation_files:
                    logger.debug(f"   📂 Loading {tf.name}...")
                    translator = QTranslator()
                    if translator.load(str(tf)):
                        self.translators.append(translator)
                        if app:
                            app.installTranslator(translator)
                        loaded_count += 1
                        logger.debug(f"   ✅ Loaded {tf.name}")
                    else:
                        logger.warning(f"   ⚠️ Failed to load {tf.name}")

                if loaded_count > 0:
                    logger.debug(f"   ✅ {loaded_count} translator(s) installed")

                    if app:
                        # Load Qt's built-in translations for standard buttons (Yes, No, OK, Cancel, etc.)
                        from PySide6.QtCore import QLibraryInfo
                        qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
                        if self.qt_translator.load(f"qtbase_{language_code}", qt_translations_path):
                            app.installTranslator(self.qt_translator)
                            logger.debug(f"   ✅ Qt base translator installed for {language_code}")
                        else:
                            logger.warning(f"   ⚠️ Qt base translations not found for {language_code}")

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
                        logger.debug("   🔄 Sent LanguageChange event to all widgets")

                    self.current_language = language_code
                    Config.set('language', language_code)
                    logger.info(f"   ✅ Language set to: {language_code}")
                    return True
                else:
                    logger.error("   ❌ Failed to load any translation files")
                    return False
            else:
                logger.warning(f"   ❌ No translation files found for {language_code}")
                logger.info("Using English as fallback")
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
                logger.debug("   🔄 Sent LanguageChange event to all widgets")

            logger.info("   ✅ Set to English")
            return True

    def load_current_language(self):
        """Force load the current language translator (used at startup)"""
        logger.debug(f"🌐 load_current_language called, current: {self.current_language}")

        if self.current_language == 'en':
            logger.debug("   ✅ Using English (built-in)")
            return True

        # Force load the translator for current language
        app = QApplication.instance()
        if not app:
            logger.error("   ❌ No app instance")
            return False

        translation_files = self._get_translation_files(self.current_language)

        if not translation_files:
            logger.warning(f"   ❌ No translation files found for {self.current_language}")
            return False

        logger.debug(f"   📁 Found {len(translation_files)} translation file(s)")
        loaded_count = 0

        for tf in translation_files:
            logger.debug(f"   📂 Loading {tf.name}...")
            translator = QTranslator()
            if translator.load(str(tf)):
                self.translators.append(translator)
                app.installTranslator(translator)
                loaded_count += 1
                logger.debug(f"   ✅ Loaded {tf.name}")
            else:
                logger.warning(f"   ⚠️ Failed to load {tf.name}")

        if loaded_count > 0:
            logger.debug(f"   ✅ {loaded_count} translator(s) installed")

            # Load Qt's built-in translations for standard buttons (Yes, No, OK, Cancel, etc.)
            from PySide6.QtCore import QLibraryInfo
            qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
            if self.qt_translator.load(f"qtbase_{self.current_language}", qt_translations_path):
                app.installTranslator(self.qt_translator)
                logger.debug(f"   ✅ Qt base translator installed for {self.current_language}")
            else:
                logger.warning(f"   ⚠️ Qt base translations not found for {self.current_language}")

            return True
        else:
            logger.error("   ❌ Failed to load any translation files")
            return False

    def get_translation_file_path(self, language_code: str) -> Path:
        """Get path to translation file for a language (returns first available)"""
        files = self._get_translation_files(language_code)
        if files:
            return files[0]
        return self.translations_dir / f"pygm2_{language_code}.qm"

    def get_translation_file_paths(self, language_code: str) -> list:
        """Get all translation file paths for a language"""
        return self._get_translation_files(language_code)

    def is_translation_available(self, language_code: str) -> bool:
        """Check if translation file exists for a language"""
        if language_code == 'en':
            return True  # English is built-in
        return len(self._get_translation_files(language_code)) > 0


# Global language manager instance
_language_manager = None

def get_language_manager():
    """Get the global language manager instance"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager
