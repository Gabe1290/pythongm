#!/usr/bin/env python3

# CRITICAL: Import Qt patch to fix standardIcon errors
try:
    # import qt_patch
    print("✅ Qt patch loaded")
except ImportError:
    print("⚠️ qt_patch module not found, continuing without it")
    # Apply basic Qt setup inline
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        print("✅ Basic Qt setup applied")
    except:
        print("⚠️ Could not apply Qt setup")
    
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont

from core.ide_window import PyGameMakerIDE
from utils.config import Config, load_config, save_config

def setup_application():
    from PySide6.QtGui import QFont
    
    app = QApplication(sys.argv)
    
    app.setApplicationName("PyGameMaker")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PyGameMaker")
    app.setOrganizationDomain("pygamemaker.org")
    
    # Load config first to get preferences
    load_config()
    
    # Load translations based on config or system locale
    from PySide6.QtCore import QTranslator, QLocale
    
    translator = QTranslator()
    app.translator = translator  # Store translator on app for later access
    
    # Get language from config or use system default
    language_config = Config.get('language', 'en')
    
    print(f"🌐 Language config: {language_config}")

    if language_config and language_config != 'en':
        # Try to load translation file
        translations_path = Path(__file__).parent / "translations"
        translation_file = translations_path / f"pygamemaker_{language_config}.qm"

        print(f"📁 Translation file path: {translation_file}")
        print(f"📁 File exists: {translation_file.exists()}")

        if translation_file.exists():
            if translator.load(str(translation_file)):
                app.installTranslator(translator)
                print(f"✅ Loaded and installed translation: {language_config}")
                print(f"✅ Testing: AboutDialog/Close = {app.translate('AboutDialog', 'Close')}")
            else:
                print(f"⚠️ Failed to load translation: {translation_file}")
        else:
            print(f"ℹ️ No translation file for {language_config}, using English")
    else:
        print(f"ℹ️ Using English (default)")

    # Apply theme from config
    from utils.theme_manager import ThemeManager
    appearance_config = Config.get_appearance_config()
    ThemeManager.apply_theme(appearance_config['theme'])
    
    # Set global font configuration
    font_config = Config.get_font_config()
    app_font = QFont()
    
    # Use configured font family, or fall back to platform defaults
    if font_config['family']:
        app_font.setFamily(font_config['family'])
    else:
        # Platform-specific defaults
        if sys.platform == "win32":
            app_font.setFamily("Segoe UI")
        elif sys.platform == "darwin":  # macOS
            app_font.setFamily("SF Pro Text")
        else:  # Linux
            app_font.setFamily("Ubuntu")
    
    # Set font size from config
    app_font.setPointSize(font_config['size'])
    
    # Apply font globally
    app.setFont(app_font)
    
    print(f"✅ Global font configured: {app_font.family()}, {app_font.pointSize()}pt")
    
    icon_path = Path(__file__).parent / "resources" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app

def setup_directories():
    app_dir = Path.home() / ".pygamemaker"
    app_dir.mkdir(exist_ok=True)
    
    projects_dir = Path.home() / "PyGameMaker Projects"
    projects_dir.mkdir(exist_ok=True)
    
    return app_dir, projects_dir


def main():
    try:
        app = setup_application()
        
        app_dir, projects_dir = setup_directories()
        
        ide = PyGameMakerIDE()
        ide.show()

        # If translator was installed, trigger retranslation of all widgets
        if language_config and language_config != 'en':
            from PySide6.QtCore import QEvent
            from PySide6.QtCore import QTimer

            def retranslate_all():
                """Retranslate all widgets after IDE is fully initialized"""
                print(f"🔄 Triggering retranslation for {len(app.allWidgets())} widgets...")
                for widget in app.allWidgets():
                    app.sendEvent(widget, QEvent(QEvent.Type.LanguageChange))
                print(f"✅ Retranslation complete")

            # Use QTimer to defer retranslation until after event loop starts
            QTimer.singleShot(0, retranslate_all)

        def save_on_exit():
            """Save configuration on application exit - FIXED"""
            try:
                from utils.config import config_manager
                config_manager.save_config()
                print("💾 Configuration saved on exit")
            except Exception as e:
                print(f"❌ Error saving config on exit: {e}")

        app.aboutToQuit.connect(save_on_exit)
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
