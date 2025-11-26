#!/usr/bin/env python3
"""
Language Manager for PyGameMaker IDE
Handles language selection and translation loading
"""

from pathlib import Path
from PySide6.QtCore import QTranslator, QLocale, QCoreApplication
from PySide6.QtWidgets import QApplication
from utils.config import Config


class LanguageManager:
    """Manages application translations and language switching"""
    
    # Available languages: (code, display_name, flag_emoji)
    AVAILABLE_LANGUAGES = [
        ('en', 'English', '🇬🇧'),
        ('fr', 'Français', '🇫🇷'),
        ('es', 'Español', '🇪🇸'),
        ('de', 'Deutsch', '🇩🇪'),
        ('it', 'Italiano', '🇮🇹'),
        ('pt', 'Português', '🇵🇹'),
        ('ru', 'Русский', '🇷🇺'),
        ('zh', '中文', '🇨🇳'),
        ('ja', '日本語', '🇯🇵'),
    ]
    
    def __init__(self):
        self.current_language = Config.get('language', 'en')
        self.translator = QTranslator()
        self.translations_dir = Path(__file__).parent.parent / 'translations'
        
        # Ensure translations directory exists
        self.translations_dir.mkdir(exist_ok=True)
    
    def get_available_languages(self):
        """Get list of available languages"""
        return self.AVAILABLE_LANGUAGES
    
    def get_current_language(self):
        """Get current language code"""
        return self.current_language
    
    def get_current_language_name(self):
        """Get current language display name"""
        for code, name, flag in self.AVAILABLE_LANGUAGES:
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
        
        # Remove old translator
        app = QApplication.instance()
        print(f"   App instance: {app}")
        if app:
            app.removeTranslator(self.translator)
            print(f"   ✅ Removed old translator")
        
        # Load new translation
        if language_code != 'en':  # English is the default, no translation needed
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

                        # Trigger retranslation of all existing widgets
                        from PySide6.QtCore import QEvent
                        for widget in app.allWidgets():
                            app.sendEvent(widget, QEvent(QEvent.Type.LanguageChange))
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
            # English selected
            self.current_language = 'en'
            Config.set('language', 'en')
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
        
        translation_file = self.translations_dir / f"pygamemaker_{self.current_language}.qm"
        
        print(f"   📁 Translation file: {translation_file}")
        print(f"   📁 File exists: {translation_file.exists()}")
        
        if translation_file.exists():
            print(f"   📂 Loading translation file...")
            if self.translator.load(str(translation_file)):
                print(f"   ✅ Translation loaded successfully")
                app.installTranslator(self.translator)
                print(f"   ✅ Translator installed to app")
                return True
            else:
                print(f"   ❌ Failed to load translation file")
                return False
        else:
            print(f"   ❌ Translation file not found")
            return False

    def get_translation_file_path(self, language_code: str) -> Path:
        """Get path to translation file for a language"""
        return self.translations_dir / f"pygamemaker_{language_code}.qm"
    
    def is_translation_available(self, language_code: str) -> bool:
        """Check if translation file exists for a language"""
        if language_code == 'en':
            return True  # English is built-in
        return self.get_translation_file_path(language_code).exists()


# Global language manager instance
_language_manager = None

def get_language_manager():
    """Get the global language manager instance"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager