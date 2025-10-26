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
from PySide6.QtGui import QIcon

from core.ide_window import PyGameMakerIDE
from utils.config import Config, load_config, save_config


def setup_application():
    app = QApplication(sys.argv)
    
    app.setApplicationName("PyGameMaker")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PyGameMaker")
    app.setOrganizationDomain("pygamemaker.org")
    
    app.setStyle("Fusion")
    
    icon_path = Path(__file__).parent / "resources" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Initialize language manager and load saved language
    try:
        from core.language_manager import get_language_manager
        language_manager = get_language_manager()
        
        # Use the new method that forces loading
        language_manager.load_current_language()
        
        print(f"🌐 Language set to: {language_manager.get_current_language_name()}")
    except Exception as e:
        print(f"⚠️ Could not initialize language manager: {e}")
        import traceback
        traceback.print_exc()
    
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
        
        load_config()
        
        ide = PyGameMakerIDE()
        ide.show()
        
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
