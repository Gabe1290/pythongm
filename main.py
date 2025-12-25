#!/usr/bin/env python3
"""
PyGameMaker IDE - A GameMaker-inspired IDE for creating 2D games with Python

Copyright (C) 2024-2025 Gabriel Thullen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# CRITICAL: Set QtWebEngine paths BEFORE importing Qt
# This is needed for Nuitka onefile builds where resources are extracted to temp dir
import sys
import os
from pathlib import Path

def setup_qtwebengine_paths():
    """Configure QtWebEngine resource paths for both development and packaged builds."""
    # Check if running from Nuitka compiled executable
    # Nuitka sets __compiled__ at module level, or we can check if running from /tmp
    is_nuitka = "__compiled__" in globals() or "__compiled__" in dir(__builtins__) if hasattr(__builtins__, '__dict__') else False

    # Also detect by checking if __file__ is in temp directory (onefile extraction)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.environ.get('TEMP', '')
    is_onefile_extracted = current_dir.startswith('/tmp/') or (temp_dir and current_dir.startswith(temp_dir))

    if is_nuitka or is_onefile_extracted or hasattr(sys, 'frozen'):
        # Get the directory where the executable's resources are extracted
        if hasattr(sys, '_MEIPASS'):  # PyInstaller
            base_path = sys._MEIPASS
        else:  # Nuitka or other
            base_path = current_dir

        # Set environment variables for QtWebEngine
        os.environ['QTWEBENGINE_RESOURCES_PATH'] = base_path
        os.environ['QTWEBENGINEPROCESS_PATH'] = os.path.join(base_path, 'QtWebEngineProcess')

        # Also set for locales
        locales_path = os.path.join(base_path, 'qtwebengine_locales')
        if os.path.exists(locales_path):
            os.environ['QTWEBENGINE_LOCALES_PATH'] = locales_path

        print("🔧 QtWebEngine paths configured for packaged app:")
        print(f"   Resources: {base_path}")
    else:
        # Running from source - find PySide6's QtWebEngineProcess
        try:
            import PySide6
            pyside6_dir = os.path.dirname(PySide6.__file__)

            # QtWebEngineProcess is in Qt/libexec on Linux, Qt/bin on Windows
            if sys.platform == 'win32':
                libexec_path = os.path.join(pyside6_dir, 'Qt', 'bin')
                process_name = 'QtWebEngineProcess.exe'
            else:
                libexec_path = os.path.join(pyside6_dir, 'Qt', 'libexec')
                process_name = 'QtWebEngineProcess'

            process_path = os.path.join(libexec_path, process_name)

            if os.path.exists(process_path):
                os.environ['QTWEBENGINEPROCESS_PATH'] = process_path

                # Set resources path to Qt directory
                qt_resources = os.path.join(pyside6_dir, 'Qt', 'resources')
                if os.path.exists(qt_resources):
                    os.environ['QTWEBENGINE_RESOURCES_PATH'] = qt_resources

                # Set locales path
                locales_path = os.path.join(pyside6_dir, 'Qt', 'translations')
                if os.path.exists(locales_path):
                    os.environ['QTWEBENGINE_LOCALES_PATH'] = locales_path

                print("🔧 QtWebEngine paths configured for development:")
                print(f"   Process: {process_path}")
            else:
                print(f"⚠️ QtWebEngineProcess not found at: {process_path}")
        except ImportError:
            print("⚠️ PySide6 not found, skipping QtWebEngine path setup")

# Call before any Qt imports
setup_qtwebengine_paths()

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
    except Exception:
        print("⚠️ Could not apply Qt setup")
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from core.ide_window import PyGameMakerIDE
from utils.config import Config, load_config

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
    from PySide6.QtCore import QTranslator

    translator = QTranslator()
    app.translator = translator  # Store translator on app for later access

    # Get language from config or use system default
    language_config = Config.get('language', 'en')

    print(f"🌐 Language config: {language_config}")

    if language_config and language_config != 'en':
        # Try to load translation file
        # Try pygm2 first (newer, more complete translations), then fall back to pygamemaker
        translations_path = Path(__file__).parent / "translations"
        translation_file = translations_path / f"pygm2_{language_config}.qm"
        if not translation_file.exists():
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
        print("ℹ️ Using English (default)")

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
        language_config = Config.get('language', 'en')
        if language_config and language_config != 'en':
            from PySide6.QtCore import QEvent
            from PySide6.QtCore import QTimer

            def retranslate_all():
                """Retranslate all widgets after IDE is fully initialized"""
                import shiboken6
                widgets = app.allWidgets()
                print(f"🔄 Triggering retranslation for {len(widgets)} widgets...")
                for widget in widgets:
                    # Check if widget is still valid (not deleted by C++)
                    try:
                        if shiboken6.isValid(widget):
                            app.sendEvent(widget, QEvent(QEvent.Type.LanguageChange))
                    except RuntimeError:
                        # Widget was deleted during iteration, skip it
                        pass
                print("✅ Retranslation complete")

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
