#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                               QSplitter, QMessageBox, QDialog, QFileDialog, QInputDialog,
                               QProgressBar, QLabel, QPushButton, QStyle, QTabWidget,
                               QToolBar, QApplication)

from PySide6.QtCore import Qt, QTimer, QSize, QThread
from PySide6.QtGui import QAction

from widgets.asset_tree.asset_tree_widget import AssetTreeWidget
# from widgets.properties_panel import PropertiesPanel
from widgets.enhanced_properties_panel import EnhancedPropertiesPanel
from core.project_manager import ProjectManager
from core.asset_manager import AssetManager
from core.ide_exporters import IDEExporters
from dialogs.project_dialogs import NewProjectDialog, ProjectSettingsDialog
from dialogs.import_dialogs import ImportAssetDialog
from dialogs.blockly_config_dialog import BlocklyConfigDialog
from dialogs.thymio_config_dialog import ThymioConfigDialog
from utils.config import Config
from editors.room_editor import RoomEditor
from editors.object_editor import ObjectEditor
from editors.sprite_editor import SpriteEditor
from runtime.game_runner import GameRunner

from core.logger import get_logger
logger = get_logger(__name__)


class ExportThread(QThread):
    """Run an exporter's ``export_project`` on a background thread.

    All five platform exports (exe, linux, macOS, android, ios) drive the
    same exporter contract, so they share one thread class.
    """

    def __init__(self, exporter, project_path, output_path, settings):
        super().__init__()
        self.exporter = exporter
        self.project_path = project_path
        self.output_path = output_path
        self.settings = settings

    def run(self):
        self.exporter.export_project(
            self.project_path,
            self.output_path,
            self.settings,
        )


class PyGameMakerIDE(QMainWindow):

    def __init__(self):
        super().__init__()

        # Create managers in the right order
        self.asset_manager = AssetManager()  # CREATE ASSET MANAGER FIRST
        self.project_manager = ProjectManager()  # CREATE PROJECT MANAGER SECOND

        # Connect them together - THIS IS CRITICAL
        try:
            self.project_manager.set_asset_manager(self.asset_manager)
        except Exception as e:
            logger.error(f"ERROR in set_asset_manager: {e}")
            import traceback
            traceback.print_exc()

        # Load auto-save settings from config. The Preferences dialog writes
        # these under the editor config as auto_save_interval in MINUTES; the
        # old code read a never-written top-level key (default 30) as seconds,
        # so the user's interval choice never took effect.
        from utils.config import Config
        editor_cfg = Config.get_editor_config()
        auto_save_enabled = editor_cfg.get('auto_save_enabled', True)
        auto_save_interval = editor_cfg.get('auto_save_interval', 5) * 60 * 1000  # minutes -> ms
        self.project_manager.set_auto_save(auto_save_enabled, auto_save_interval)

        self.current_project_path = None
        self.current_project_data = None

        # Global preferred window mode for new editor opens. Read here so
        # create_toolbar (called from setup_ui) can label its toggle button
        # correctly. The detached-windows registry is initialized later in
        # create_center_panel_with_editors but stays consistent with this.
        self.window_mode = Config.get('window_mode', 'tabbed')
        if self.window_mode not in ('tabbed', 'floating'):
            self.window_mode = 'tabbed'

        # Initialize export helper module
        self.exporters = IDEExporters(self)

        # Add game runner
        self.game_runner = None  # Will be initialized when project is loaded

        self.setup_ui()
        self.setup_connections()
        self.restore_geometry()

        # One-time cleanup of pre-rc.12 in-place sample paths that may
        # be sitting in the user's recent_projects from older sessions.
        # See _strip_samples_from_recent_projects() for why.
        self._strip_samples_from_recent_projects()

        self.update_window_title()
        self.update_ui_state()

    def setup_ui(self):
        self.setWindowTitle("PyGameMaker IDE")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)

        try:
            self.create_menu_bar()

            # Set initial auto-save checkbox state from config
            from utils.config import Config
            auto_save_enabled = Config.get('auto_save_enabled', True)
            if hasattr(self, 'auto_save_action'):
                self.auto_save_action.setChecked(auto_save_enabled)

        except Exception as e:
            logger.error(f"ERROR in create_menu_bar: {e}")
            import traceback
            traceback.print_exc()
            raise

        try:
            self.create_toolbar()
        except Exception as e:
            logger.error(f"ERROR in create_toolbar: {e}")
            import traceback
            traceback.print_exc()
            raise

        try:
            self.create_main_widget()
        except Exception as e:
            logger.error(f"ERROR in create_main_widget: {e}")
            import traceback
            traceback.print_exc()
            raise

        try:
            self.create_status_bar()
        except Exception as e:
            logger.error(f"ERROR in create_status_bar: {e}")
            import traceback
            traceback.print_exc()
            raise

        # Connect the rename signal
        self.asset_tree.asset_renamed.connect(self.on_asset_renamed)

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu(self.tr("&File"))
        # Store references so the toolbar can reuse the same QAction
        # instances. Qt then shares enable/disable state automatically.
        self.new_project_action = self.create_action(self.tr("&New Project..."), "Ctrl+N", self.new_project)
        self.open_project_action = self.create_action(self.tr("&Open Project..."), "Ctrl+O", self.open_project)
        self.save_project_action = self.create_action(self.tr("&Save Project"), "Ctrl+S", self.save_project)
        self.save_project_as_action = self.create_action(self.tr("Save Project &As..."), "Ctrl+Shift+S", self.save_project_as)
        file_menu.addAction(self.new_project_action)
        file_menu.addAction(self.open_project_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_project_action)
        file_menu.addAction(self.save_project_as_action)
        file_menu.addSeparator()

        self.recent_projects_menu = file_menu.addMenu(self.tr("Recent Projects"))
        self.update_recent_projects_menu(self.recent_projects_menu)

        file_menu.addSeparator()
        # Export menu items
        # Store references to export actions
        self.export_html5_action = self.create_action(self.tr("Export as HTML5..."), None, self.export_html5)
        self.export_zip_action = self.create_action(self.tr("Export as &Zip..."), None, self.export_project_zip)
        self.export_kivy_action = self.create_action(self.tr("Export to Kivy..."), None, self.export_kivy)
        self.export_aseba_action = self.create_action(self.tr("Export &Aseba (Thymio) code..."), None, self.export_aseba_code)
        self.export_project_action = self.create_action(self.tr("Export Project..."), "Ctrl+E", self.export_project)

        file_menu.addAction(self.export_html5_action)
        file_menu.addAction(self.export_zip_action)
        file_menu.addAction(self.export_kivy_action)
        file_menu.addAction(self.export_aseba_action)
        file_menu.addAction(self.export_project_action)

        file_menu.addAction(self.create_action(self.tr("Open &Zip Project..."), None, self.open_project_zip))
        # Import-as-new-project actions: stored on self so update_ui_state can keep
        # them enabled regardless of whether a project is currently loaded.
        self.import_roberta_action = self.create_action(self.tr("Import Open &Roberta XML..."), None, self.import_roberta_xml)
        self.import_gmk_action = self.create_action(self.tr("Import &GameMaker .gmk File..."), None, self.import_gmk_file)
        file_menu.addAction(self.import_roberta_action)
        file_menu.addAction(self.import_gmk_action)
        file_menu.addSeparator()

        # Auto-save as zip toggle
        self.auto_save_zip_action = QAction(self.tr("Auto-Save to Zip"), self)
        self.auto_save_zip_action.setCheckable(True)
        self.auto_save_zip_action.setChecked(False)
        self.auto_save_zip_action.triggered.connect(self.toggle_auto_save_zip)
        file_menu.addAction(self.auto_save_zip_action)

        # Auto-save toggle (NEW)
        self.auto_save_action = QAction(self.tr("Enable Auto-Save"), self)
        self.auto_save_action.setCheckable(True)
        self.auto_save_action.setChecked(True)  # Enabled by default
        self.auto_save_action.triggered.connect(self.toggle_auto_save)
        file_menu.addAction(self.auto_save_action)

        # Auto-save settings
        auto_save_settings_action = QAction(self.tr("Auto-Save Settings..."), self)
        auto_save_settings_action.triggered.connect(self.show_auto_save_settings)
        file_menu.addAction(auto_save_settings_action)

        file_menu.addSeparator()
        file_menu.addAction(self.create_action(self.tr("Project &Settings..."), None, self.project_settings))
        file_menu.addSeparator()
        file_menu.addAction(self.create_action(self.tr("E&xit"), "Ctrl+Q", self.close))

        edit_menu = menubar.addMenu(self.tr("&Edit"))
        edit_menu.addAction(self.create_action(self.tr("&Undo"), "Ctrl+Z", self.undo))
        edit_menu.addAction(self.create_action(self.tr("&Redo"), "Ctrl+Y", self.redo))
        edit_menu.addSeparator()
        edit_menu.addAction(self.create_action(self.tr("Cu&t"), "Ctrl+X", self.cut))
        edit_menu.addAction(self.create_action(self.tr("&Copy"), "Ctrl+C", self.copy))
        edit_menu.addAction(self.create_action(self.tr("&Paste"), "Ctrl+V", self.paste))
        edit_menu.addAction(self.create_action(self.tr("&Duplicate"), "Ctrl+D", self.duplicate))

        # Store references to all asset actions and enable them
        self.import_sprite_action = self.create_action(self.tr("Import &Sprite..."), None, self.import_sprite)
        self.import_sound_action = self.create_action(self.tr("Import &Sound..."), None, self.import_sound)
        self.import_background_action = self.create_action(self.tr("Import &Background..."), None, self.import_background)
        self.create_object_action = self.create_action(self.tr("Create &Object..."), None, self.create_object)
        self.create_room_action = self.create_action(self.tr("Create &Room..."), None, self.create_room)
        self.create_room_action.setShortcut("Ctrl+R")
        self.create_script_action = self.create_action(self.tr("Create S&cript..."), None, self.create_script)
        self.create_font_action = self.create_action(self.tr("Create &Font..."), None, self.create_font)

        # Enable all asset actions regardless of project state
        asset_actions = [
            self.import_sprite_action, self.import_sound_action, self.import_background_action,
            self.create_object_action, self.create_room_action, self.create_script_action, self.create_font_action
        ]
        for action in asset_actions:
            action.setEnabled(True)

        # Add to menu
        assets_menu = menubar.addMenu(self.tr("&Assets"))
        assets_menu.addAction(self.import_sprite_action)
        assets_menu.addAction(self.import_sound_action)
        assets_menu.addAction(self.import_background_action)
        assets_menu.addSeparator()
        assets_menu.addAction(self.create_object_action)
        assets_menu.addAction(self.create_room_action)
        assets_menu.addAction(self.create_script_action)
        assets_menu.addAction(self.create_font_action)
        assets_menu.addSeparator()

        # Import resource packages (NEW)
        import_object_action = self.create_action(self.tr("Import Object Package..."), None, self.import_object_package)
        import_room_action = self.create_action(self.tr("Import Room Package..."), None, self.import_room_package)
        assets_menu.addAction(import_object_action)
        assets_menu.addAction(import_room_action)

        self.build_menu = menubar.addMenu(self.tr("&Build"))
        # Store references to build actions
        self.test_game_action = self.create_action(self.tr("&Test Game"), "F5", self.test_game)
        self.debug_game_action = self.create_action(self.tr("&Debug Game"), "F6", self.debug_game)
        self.export_game_action = self.create_action(self.tr("&Export Game..."), None, self.export_game)

        self.build_menu.addAction(self.test_game_action)
        self.build_menu.addAction(self.debug_game_action)
        self.build_menu.addSeparator()
        self.build_menu.addAction(self.export_game_action)

        tools_menu = menubar.addMenu(self.tr("&Tools"))
        # On macOS, Qt auto-promotes actions to the App menu via text heuristics
        # ("Preferences", "Settings", "Config", "Setup" all match PreferencesRole).
        # Pin the real Preferences to PreferencesRole and force NoRole on the
        # Configure ... actions so the App-menu Preferences slot doesn't get
        # hijacked by "Configure Thymio Blocks..." etc.
        preferences_action = self.create_action(self.tr("&Preferences..."), None, self.preferences)
        preferences_action.setMenuRole(QAction.PreferencesRole)
        tools_menu.addAction(preferences_action)
        configure_blockly_action = self.create_action(self.tr("Configure &Action Blocks..."), None, self.configure_blockly)
        configure_blockly_action.setMenuRole(QAction.NoRole)
        tools_menu.addAction(configure_blockly_action)
        configure_thymio_action = self.create_action(self.tr("Configure &Thymio Blocks..."), None, self.configure_thymio)
        configure_thymio_action.setMenuRole(QAction.NoRole)
        tools_menu.addAction(configure_thymio_action)
        tools_menu.addSeparator()
        # Project-scoped tools: stored on self so update_ui_state() can
        # disable them when no project is open. Without the stored
        # reference, these used to be clickable from the menu and would
        # only show a "Please open a project first" dialog after the fact.
        self.validate_project_action = self.create_action(
            self.tr("&Validate Project"), None, self.validate_project)
        self.migrate_project_action = self.create_action(
            self.tr("&Migrate to Modular Structure"), None, self.migrate_project_structure)
        tools_menu.addAction(self.validate_project_action)
        tools_menu.addAction(self.migrate_project_action)
        tools_menu.addSeparator()

        # Language submenu
        language_menu = tools_menu.addMenu(self.tr("🌐 &Language"))
        self.create_language_menu(language_menu)

        # Thymio submenu
        tools_menu.addSeparator()
        thymio_menu = tools_menu.addMenu(self.tr("🤖 &Thymio Programming"))

        # Show Thymio Tab checkbox
        self.show_thymio_tab_action = QAction(self.tr("Show Thymio Tab in Object Editor"), self)
        self.show_thymio_tab_action.setCheckable(True)
        self.show_thymio_tab_action.setChecked(Config.get('show_thymio_tab', False))
        self.show_thymio_tab_action.triggered.connect(self.toggle_thymio_tab)
        thymio_menu.addAction(self.show_thymio_tab_action)
        thymio_menu.addSeparator()

        thymio_menu.addAction(self.create_action(self.tr("Open &Playground..."), None, self.show_thymio_playground))
        thymio_menu.addSeparator()
        # Add Event/Action target the currently active object editor, which
        # can only exist when a project is open. Stored on self so
        # update_ui_state() can disable them in that case.
        self.thymio_add_event_action = self.create_action(
            self.tr("Add &Event..."), None, self.show_thymio_event_selector)
        self.thymio_add_action_action = self.create_action(
            self.tr("Add &Action..."), None, self.show_thymio_action_selector)
        thymio_menu.addAction(self.thymio_add_event_action)
        thymio_menu.addAction(self.thymio_add_action_action)
        thymio_menu.addSeparator()
        self.thymio_import_roberta_action = self.create_action(self.tr("Import Open &Roberta XML..."), None, self.import_roberta_xml)
        thymio_menu.addAction(self.thymio_import_roberta_action)

        help_menu = menubar.addMenu(self.tr("&Help"))
        help_menu.addAction(self.create_action(self.tr("&Documentation"), "F1", self.show_documentation))
        help_menu.addAction(self.create_action(self.tr("&Online Documentation"), None, self.show_online_documentation))
        help_menu.addAction(self.create_action(self.tr("&Tutorials"), None, self.show_tutorials))
        help_menu.addSeparator()
        help_menu.addAction(self.create_action(self.tr("&About PyGameMaker"), None, self.about))

    def create_language_menu(self, menu):
        """Create language selection submenu"""
        from core.language_manager import get_language_manager
        from PySide6.QtGui import QActionGroup, QIcon

        language_manager = get_language_manager()
        current_lang = language_manager.get_current_language()

        # Create action group for radio buttons
        self.language_action_group = QActionGroup(self)
        self.language_action_group.setExclusive(True)

        # Hotkey mapping: language code -> hotkey character
        # Each hotkey should be unique and present in the language name
        # Uses & before the letter to create underlined hotkey (e.g., "&English" -> E)
        language_hotkeys = {
            'en': 'E',  # English
            'fr': 'F',  # Français
            'es': 'S',  # eSpañol (E taken by English)
            'de': 'D',  # Deutsch
            'it': 'I',  # Italiano
            'pt': 'P',  # Português
            'ru': 'R',  # Русский (use R for Russian)
            'uk': 'U',  # Українська (use U for Ukrainian)
            'sl': 'L',  # SLovenščina (S taken by Spanish)
        }

        def add_hotkey_to_name(name, code):
            """Insert & before the hotkey character in the language name"""
            hotkey = language_hotkeys.get(code)
            if not hotkey:
                return name
            # Find the hotkey character (case-insensitive)
            idx = name.lower().find(hotkey.lower())
            if idx >= 0:
                return name[:idx] + '&' + name[idx:]
            return name

        # Separate languages into available and unavailable
        available_languages = []
        unavailable_languages = []

        for code, name, flag in language_manager.get_available_languages():
            if language_manager.is_translation_available(code) or code == 'en':
                available_languages.append((code, name, flag))
            else:
                unavailable_languages.append((code, name, flag))

        # Add available languages first
        for code, name, flag in available_languages:
            # Add hotkey to name
            display_name = add_hotkey_to_name(name, code)
            # Try to load flag icon, fall back to emoji text
            flag_path = language_manager.get_flag_icon_path(code)
            if flag_path and flag_path.exists():
                action = menu.addAction(QIcon(str(flag_path)), display_name)
            else:
                action = menu.addAction(f"{flag} {display_name}")
            action.setCheckable(True)
            action.setData(code)

            action.blockSignals(True)
            action.setChecked(code == current_lang)
            action.blockSignals(False)

            action.triggered.connect(lambda checked, lang=code: self.change_language(lang))
            self.language_action_group.addAction(action)

        # Add separator if there are unavailable languages
        if unavailable_languages:
            menu.addSeparator()

            # Add unavailable languages
            for code, name, flag in unavailable_languages:
                # Add hotkey to name (even for unavailable, for consistency)
                display_name = add_hotkey_to_name(name, code)
                flag_path = language_manager.get_flag_icon_path(code)
                if flag_path and flag_path.exists():
                    action = menu.addAction(QIcon(str(flag_path)), f"{display_name} (translation not available)")
                else:
                    action = menu.addAction(f"{flag} {display_name} (translation not available)")
                action.setCheckable(True)
                action.setData(code)

                action.blockSignals(True)
                action.setChecked(code == current_lang)
                action.blockSignals(False)

                action.triggered.connect(lambda checked, lang=code: self.change_language(lang))
                self.language_action_group.addAction(action)

    def change_language(self, language_code: str):
        """Change the application language"""
        from core.language_manager import get_language_manager
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtCore import QCoreApplication

        language_manager = get_language_manager()

        # Get language name for display
        lang_name = ""
        for code, name, flag in language_manager.get_available_languages():
            if code == language_code:
                lang_name = name
                break

        # Set the language
        success = language_manager.set_language(language_code)

        # Process events to ensure translation changes are fully applied
        # This is critical when switching TO English - the translator removal must be processed
        QCoreApplication.processEvents()

        if success or language_code == 'en':
            # Save config to ensure language setting is persisted
            from utils.config import Config
            Config.save()

            # Inform user to restart manually
            if language_code == 'en':
                title = "Language Changed"
                message = (
                    f"Language changed to {lang_name}.\n\n"
                    "Please close and restart the IDE for the change to take effect.")
            else:
                title = QCoreApplication.translate("PyGameMakerIDE", "Language Changed")
                message = QCoreApplication.translate("PyGameMakerIDE",
                    "Language changed to {0}.\n\n"
                    "Please close and restart the IDE for the change to take effect.").format(lang_name)

            QMessageBox.information(self, title, message)
        else:
            # Translation file not found
            # Use QCoreApplication.translate() for consistency
            title = QCoreApplication.translate("PyGameMakerIDE", "Translation Not Available")
            message = QCoreApplication.translate("PyGameMakerIDE",
                "Translation file for {0} is not available.\n\n"
                "The language has been set, but the interface will remain in English until "
                "a translation file is provided.\n\n"
                "Expected file: translations/pygamemaker_{1}.qm").format(lang_name, language_code)

            QMessageBox.warning(self, title, message)

    def export_html5(self):
        """Export project as HTML5 - delegated to exporters module"""
        self.exporters.export_html5()
    def export_kivy(self):
        """Quick export to Kivy - delegated to exporters module"""
        self.exporters.export_kivy()

    def export_project(self):
        """Open export project dialog - delegated to exporters module"""
        self.exporters.export_project()

    def export_project_zip(self):
        """Export current project as a .zip file - delegated to exporters module"""
        self.exporters.export_project_zip()

    def open_project_zip(self):
        """Open a project from a .zip file - delegated to exporters module"""
        self.exporters.open_project_zip()

    def toggle_auto_save_zip(self):
        """Toggle auto-save to zip mode"""
        enabled = self.auto_save_zip_action.isChecked()

        if self.project_manager:
            self.project_manager.set_auto_save_as_zip(enabled)

            if enabled:
                # Check if project is from zip
                if self.project_manager.is_project_from_zip():
                    QMessageBox.information(
                        self,
                        self.tr("Auto-Save to Zip Enabled"),
                        self.tr("The project will now automatically save to the original zip file.")
                    )
                else:
                    # Offer to export current project as zip
                    reply = QMessageBox.question(
                        self,
                        self.tr("Export as Zip?"),
                        self.tr("Would you like to export the current project as a zip file now?\n\n"
                            "This will allow auto-save to work with the zip file."),
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if reply == QMessageBox.Yes:
                        self.export_project_zip()
            else:
                self.update_status(self.tr("Auto-save to zip disabled"))

    def toggle_auto_save(self):
        """Toggle auto-save on/of"""
        enabled = self.auto_save_action.isChecked()

        if self.project_manager:
            # Get current interval from project manager or default to 30 seconds
            current_interval = getattr(self.project_manager, 'auto_save_interval', 30000)
            self.project_manager.set_auto_save(enabled, current_interval)

            if enabled:
                self.update_status(self.tr("Auto-save enabled"))
                QMessageBox.information(
                    self,
                    self.tr("Auto-Save Enabled"),
                    self.tr("Your project will be automatically saved every {0} seconds.").format(current_interval // 1000)
                )
            else:
                self.update_status(self.tr("Auto-save disabled"))
                QMessageBox.information(
                    self,
                    self.tr("Auto-Save Disabled"),
                    self.tr("Remember to save your project manually (Ctrl+S).")
                )

    def show_auto_save_settings(self):
        """Show auto-save settings dialog"""
        from dialogs.auto_save_dialog import AutoSaveSettingsDialog

        # Get current settings
        if self.project_manager:
            current_enabled = self.project_manager.auto_save_enabled
            current_interval = self.project_manager.auto_save_interval // 1000  # Convert to seconds
        else:
            current_enabled = True
            current_interval = 30

        # Show dialog
        dialog = AutoSaveSettingsDialog(current_enabled, current_interval, self)
        if dialog.exec():
            enabled, interval_seconds = dialog.get_settings()

            # Apply settings
            if self.project_manager:
                self.project_manager.set_auto_save(enabled, interval_seconds * 1000)

                # Update menu checkbox
                self.auto_save_action.setChecked(enabled)

                # Save to config
                from utils.config import Config
                Config.set('auto_save_enabled', enabled)
                Config.set('auto_save_interval', interval_seconds)

                self.update_status(self.tr("Auto-save settings updated"))

    def import_object_package(self):
        """Import an object package"""
        if not self.current_project_path:
            QMessageBox.information(self, self.tr("No Project"), self.tr("Please open a project first"))
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import Object Package"),
            str(Path.home()),
            self.tr("GameMaker Objects (*.gmobj)")
        )

        if file_path:
            from utils.resource_packager import ResourcePackager

            self.update_status(self.tr("Importing object..."))

            object_name = ResourcePackager.import_object(
                Path(file_path),
                self.current_project_path
            )

            if object_name:
                # Reload project to show new object
                self.load_project(self.current_project_path)

                QMessageBox.information(
                    self,
                    self.tr("Import Successful"),
                    self.tr("Object '{0}' imported successfully!").format(object_name)
                )
                self.update_status(self.tr("Object imported: {0}").format(object_name))
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Import Failed"),
                    self.tr("Failed to import object package")
                )
                self.update_status(self.tr("Import failed"))

    def import_room_package(self):
        """Import a room package"""
        if not self.current_project_path:
            QMessageBox.information(self, self.tr("No Project"), self.tr("Please open a project first"))
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import Room Package"),
            str(Path.home()),
            self.tr("GameMaker Rooms (*.gmroom)")
        )

        if file_path:
            from utils.resource_packager import ResourcePackager

            self.update_status(self.tr("Importing room..."))

            room_name = ResourcePackager.import_room(
                Path(file_path),
                self.current_project_path
            )

            if room_name:
                # Reload project to show new room
                self.load_project(self.current_project_path)

                QMessageBox.information(
                    self,
                    self.tr("Import Successful"),
                    self.tr("Room '{0}' imported successfully!").format(room_name)
                )
                self.update_status(self.tr("Room imported: {0}").format(room_name))
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Import Failed"),
                    self.tr("Failed to import room package")
                )
                self.update_status(self.tr("Import failed"))

    def import_roberta_xml(self):
        """Import an Open Roberta Lab XML program as a new project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import Open Roberta XML"),
            str(Path.home()),
            self.tr("Open Roberta XML (*.xml)")
        )

        if not file_path:
            return

        # Ask user where to save the new project
        output_dir = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Output Directory for Imported Project"),
            str(Path.home())
        )

        if not output_dir:
            return

        from importers.roberta_importer import import_roberta_detailed, RobertaImportError

        self.update_status(self.tr("Importing Open Roberta program..."))

        try:
            result = import_roberta_detailed(file_path, output_dir)

            # Show warnings if any
            warning_text = ""
            if result.warnings:
                warning_text = self.tr("\n\nWarnings:\n") + "\n".join(
                    f"  - {w}" for w in result.warnings[:20])

            QMessageBox.information(
                self,
                self.tr("Import Successful"),
                self.tr("Project '{0}' imported successfully!\n"
                         "Events: {1}, Actions: {2}{3}").format(
                    result.project_name,
                    result.events_imported,
                    result.actions_imported,
                    warning_text)
            )
            self.update_status(self.tr("Roberta import complete: {0}").format(result.project_name))

            # Open the newly imported project
            project_file = Path(output_dir) / "project.json"
            if project_file.exists():
                self.load_project(Path(output_dir))

        except RobertaImportError as exc:
            QMessageBox.warning(
                self,
                self.tr("Import Failed"),
                self.tr("Failed to import Open Roberta XML:\n{0}").format(str(exc))
            )
            self.update_status(self.tr("Roberta import failed"))

    def import_gmk_file(self):
        """Import a legacy GameMaker 8.0/8.1 .gmk file as a new project."""
        gmk_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import GameMaker File"),
            str(Path.home()),
            self.tr("GameMaker Files (*.gmk)")
        )
        if not gmk_path:
            return

        gmk_file = Path(gmk_path)
        # Default output: a sibling folder named after the .gmk stem.
        # Picks a non-clashing sibling if one already exists, so grading multiple
        # submissions in the same folder doesn't silently overwrite anything.
        default_parent = gmk_file.parent
        candidate = default_parent / gmk_file.stem
        suffix = 2
        while candidate.exists() and any(candidate.iterdir()):
            candidate = default_parent / f"{gmk_file.stem}_{suffix}"
            suffix += 1
        output_dir = candidate

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.warning(
                self,
                self.tr("Import Failed"),
                self.tr("Could not create output folder:\n{0}").format(str(exc))
            )
            return

        from importers.gmk_importer import import_gmk_detailed

        self.update_status(self.tr("Importing GameMaker file..."))
        result = import_gmk_detailed(str(gmk_file), str(output_dir))

        if not result.success:
            warning_text = "\n".join(f"  - {w}" for w in result.warnings[:20]) or self.tr("(no details)")
            QMessageBox.warning(
                self,
                self.tr("Import Failed"),
                self.tr("Failed to import {0}:\n\n{1}").format(gmk_file.name, warning_text)
            )
            self.update_status(self.tr("GMK import failed"))
            return

        stats_text = ", ".join(f"{k}: {v}" for k, v in result.stats.items() if v > 0) or self.tr("(empty project)")
        warning_text = ""
        if result.warnings:
            shown = "\n".join(f"  - {w}" for w in result.warnings[:20])
            extra = self.tr("\n  ...and {0} more").format(len(result.warnings) - 20) if len(result.warnings) > 20 else ""
            warning_text = self.tr("\n\nWarnings:\n") + shown + extra

        QMessageBox.information(
            self,
            self.tr("Import Successful"),
            self.tr("Imported '{0}' to:\n{1}\n\n{2}{3}").format(
                gmk_file.name, str(output_dir), stats_text, warning_text)
        )
        self.update_status(self.tr("GMK import complete: {0}").format(gmk_file.stem))

        if (output_dir / "project.json").exists():
            self.load_project(output_dir)

    def create_toolbar(self):
        toolbar = self.addToolBar(self.tr("Main"))
        toolbar.setObjectName("MainToolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        # Reuse the QAction instances from the menus so a single Qt object
        # drives both menu and toolbar — enable/disable state from
        # update_ui_state() then applies to the toolbar automatically.
        # Apply icons here (the menu definitions stayed iconless).
        style = self.style()

        def _icon(icon_name: str):
            try:
                pixmap_enum = getattr(QStyle.StandardPixmap, icon_name, None)
                if pixmap_enum is not None:
                    icon = style.standardIcon(pixmap_enum)
                    if not icon.isNull():
                        return icon
            except Exception:
                pass
            return None

        def _attach(action, icon_name, tooltip):
            """Set the toolbar icon + tooltip on a shared menu action.

            ``tooltip`` is the descriptive hover text the user sees on the
            toolbar (e.g., "New Project (Ctrl+N)"). Setting it via
            setToolTip on the QAction also improves the menu hover tooltip,
            which is fine — descriptive tooltips help in both contexts.
            """
            icon = _icon(icon_name)
            if icon is not None:
                action.setIcon(icon)
            action.setToolTip(tooltip)
            toolbar.addAction(action)

        # Project group ------------------------------------------------
        _attach(self.new_project_action,  "SP_FileIcon",        self.tr("New Project (Ctrl+N)"))
        _attach(self.open_project_action, "SP_DialogOpenButton", self.tr("Open Project (Ctrl+O)"))
        _attach(self.save_project_action, "SP_DialogSaveButton", self.tr("Save Project (Ctrl+S)"))

        toolbar.addSeparator()

        # Build group --------------------------------------------------
        _attach(self.test_game_action,   "SP_MediaPlay",         self.tr("Test Game (F5)"))
        _attach(self.debug_game_action,  "SP_ComputerIcon",      self.tr("Debug Game (F6)"))
        _attach(self.export_game_action, "SP_DialogApplyButton", self.tr("Export Game…"))

        toolbar.addSeparator()

        # Asset import group -------------------------------------------
        _attach(self.import_sprite_action, "SP_FileIcon",     self.tr("Import Sprite…"))
        _attach(self.import_sound_action,  "SP_MediaVolume",  self.tr("Import Sound…"))

        toolbar.addSeparator()

        # Thymio quick-add (new QAction — no corresponding menu item with
        # the same exact semantics, since the menu has Add Event/Action
        # split into two entries; the toolbar exposes the most common one)
        self.thymio_toolbar_action = self.create_action(
            self.tr("Thymio"), None, self.show_thymio_event_selector, "SP_DriveNetIcon"
        )
        self.thymio_toolbar_action.setToolTip(self.tr("Add Thymio Event"))
        toolbar.addAction(self.thymio_toolbar_action)

        toolbar.addSeparator()

        # Window-mode toggle — doubles as the recovery affordance when a
        # floating editor has been dragged off-screen (clicking "Tabbed"
        # snaps every detached window back into the tab strip).
        self.window_mode_action = self.create_action(
            self.tr("Tabbed"), None, self.toggle_window_mode, None
        )
        self.window_mode_action.setToolTip(
            self.tr("Toggle between Tabbed and Floating editor layouts")
        )
        self._update_window_mode_action_label()
        toolbar.addAction(self.window_mode_action)

        toolbar.update()

    def create_main_widget(self):
        """Modified to include editor tabs in center"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Asset tree (unchanged)
        try:
            self.asset_tree = AssetTreeWidget(self)
        except Exception as e:
            logger.error(f"Failed to create AssetTreeWidget: {e}")
            import traceback
            traceback.print_exc()
        self.asset_tree.setMinimumWidth(200)
        self.asset_tree.setMaximumWidth(300)

        # Center panel - NEW: Tabbed editors
        center_panel = self.create_center_panel_with_editors()

        # Right panel - Properties panel
        from PySide6.QtWidgets import QStackedWidget

        self.right_panel_stack = QStackedWidget()
        self.right_panel_stack.setMinimumWidth(250)

        # Properties panel (index 0)
        self.properties_panel = EnhancedPropertiesPanel()
        self.right_panel_stack.addWidget(self.properties_panel)

        # Start with properties panel visible
        self.right_panel_stack.setCurrentIndex(0)

        # Add panels to main splitter
        self.main_splitter.addWidget(self.asset_tree)
        self.main_splitter.addWidget(center_panel)
        self.main_splitter.addWidget(self.right_panel_stack)

        # Set proportions: asset tree, editors, properties
        self.main_splitter.setSizes([250, 800, 300])
        self.main_splitter.setCollapsible(0, False)
        self.main_splitter.setCollapsible(1, False)
        self.main_splitter.setCollapsible(2, True)  # Allow right panel to collapse

        # Store default sizes for restoring right panel
        self._default_splitter_sizes = [250, 800, 300]

        layout.addWidget(self.main_splitter)

    def create_center_panel_with_editors(self):
        """Create center panel with tabbed editors"""
        from widgets.welcome_tab import WelcomeTab

        center_widget = QWidget()
        layout = QVBoxLayout(center_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget for editors
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        self.editor_tabs.currentChanged.connect(self.on_tab_changed)

        # Store reference to open editors
        self.open_editors = {}  # name -> editor_widget
        # Asset name -> DetachedEditorWindow for editors floated out of the
        # tab strip. Editors in this dict still appear in self.open_editors
        # but are NOT in self.editor_tabs.
        self.detached_editor_windows = {}

        # Welcome tab (default)
        self.welcome_tab = WelcomeTab(self)
        self.editor_tabs.addTab(self.welcome_tab, self.tr("Welcome"))

        layout.addWidget(self.editor_tabs)
        return center_widget

    def close_editor_tab(self, index):
            """Close an editor tab"""
            tab_text = self.editor_tabs.tabText(index).replace('*', '')  # Remove modification indicator

            if tab_text != "Welcome":
                # Check if editor has unsaved changes
                editor_widget = self.editor_tabs.widget(index)
                if hasattr(editor_widget, 'is_modified') and editor_widget.is_modified:
                    from PySide6.QtWidgets import QMessageBox
                    reply = QMessageBox.question(
                        self, self.tr('Unsaved Changes'),
                        self.tr('"{0}" has unsaved changes. Save before closing?').format(tab_text),
                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                    )

                    if reply == QMessageBox.Cancel:
                        return
                    elif reply == QMessageBox.Save:
                        if hasattr(editor_widget, 'save'):
                            if not editor_widget.save():
                                return  # Save failed, don't close

                # Disconnect editor signals before closing to prevent memory leaks
                if editor_widget:
                    # Try to disconnect common editor signals
                    if hasattr(editor_widget, 'save_requested'):
                        self.safe_disconnect_signal(editor_widget.save_requested, self.on_editor_save_requested)
                    if hasattr(editor_widget, 'close_requested'):
                        self.safe_disconnect_signal(editor_widget.close_requested, self.on_editor_close_requested)
                    if hasattr(editor_widget, 'data_modified'):
                        self.safe_disconnect_signal(editor_widget.data_modified, self.on_editor_data_modified)
                    if hasattr(editor_widget, 'float_requested'):
                        self.safe_disconnect_signal(editor_widget.float_requested, self.float_editor)
                    if hasattr(editor_widget, 'reattach_requested'):
                        self.safe_disconnect_signal(editor_widget.reattach_requested, self.reattach_editor)

                    # Disconnect editor-specific signals
                    if hasattr(editor_widget, 'room_editor_activated'):
                        self.safe_disconnect_signal(editor_widget.room_editor_activated, self.on_room_editor_activated)
                    if hasattr(editor_widget, 'object_editor_activated'):
                        self.safe_disconnect_signal(editor_widget.object_editor_activated, self.on_object_editor_activated)

                # Remove from open editors dict if it exists
                if tab_text in self.open_editors:
                    del self.open_editors[tab_text]

                # Remove tab and schedule widget for deletion to free memory
                self.editor_tabs.removeTab(index)
                if editor_widget:
                    editor_widget.deleteLater()

                # Show welcome tab if no editors left
                if self.editor_tabs.count() == 0:
                    self.editor_tabs.addTab(self.welcome_tab, self.tr("Welcome"))

    def on_tab_changed(self, index):
        """Handle tab change"""
        widget = self.editor_tabs.widget(index)

        if not widget:
            return

        # Update properties panel visibility and context based on current editor type
        if hasattr(widget, '__class__'):
            editor_class = widget.__class__.__name__

            if editor_class == 'RoomEditor':
                # Room editor is active - restore right panel with room properties
                self._restore_right_panel()

                try:
                    room_name = widget.asset_name
                    room_data = widget.get_data() if hasattr(widget, 'get_data') else widget.current_room_properties

                    self.properties_panel.set_room_editor_context(widget, room_name, room_data)

                except Exception as e:
                    logger.error(f"Error setting room editor context: {e}")

            elif editor_class == 'ObjectEditor':
                # Object editor is active - COLLAPSE right panel (object editor has its own properties)
                self._collapse_right_panel()

                # Clear the context since we're not using the external properties panel
                self.clear_properties_contexts()

            else:
                # Other editor type - restore right panel and clear contexts
                self._restore_right_panel()
                self.clear_properties_contexts()

        else:
            # Welcome tab or other non-editor - restore right panel
            self._restore_right_panel()
            self.clear_properties_contexts()

    def clear_properties_contexts(self):
        """Clear all properties panel contexts"""
        if hasattr(self, 'properties_panel'):
            # Clear the current editor references
            if hasattr(self.properties_panel, 'current_object_editor'):
                self.properties_panel.current_object_editor = None
            if hasattr(self.properties_panel, 'current_room_editor'):
                self.properties_panel.current_room_editor = None

            if hasattr(self.properties_panel, 'clear_room_context'):
                self.properties_panel.clear_room_context()
            if hasattr(self.properties_panel, 'clear_object_context'):
                self.properties_panel.clear_object_context()

    def _collapse_right_panel(self):
        """Collapse the right panel to give more space to the center editor"""
        if hasattr(self, 'main_splitter') and hasattr(self, 'right_panel_stack'):
            # Store current sizes before collapsing (only if right panel is visible)
            current_sizes = self.main_splitter.sizes()
            if current_sizes[2] > 0:
                self._last_splitter_sizes = current_sizes

            # Hide the right panel and redistribute space to center
            self.right_panel_stack.hide()
            # Set right panel size to 0, add its space to center
            new_sizes = [current_sizes[0], current_sizes[1] + current_sizes[2], 0]
            self.main_splitter.setSizes(new_sizes)

    def _restore_right_panel(self):
        """Restore the right panel to its previous size"""
        if hasattr(self, 'main_splitter') and hasattr(self, 'right_panel_stack'):
            # Show the right panel
            self.right_panel_stack.show()
            if hasattr(self, 'properties_panel'):
                self.properties_panel.show()

            # Restore previous sizes or use defaults
            if hasattr(self, '_last_splitter_sizes'):
                self.main_splitter.setSizes(self._last_splitter_sizes)
            elif hasattr(self, '_default_splitter_sizes'):
                self.main_splitter.setSizes(self._default_splitter_sizes)

    def create_status_bar(self):
        self.status_bar = self.statusBar()

        self.status_label = QLabel(self.tr("Ready"))
        self.status_bar.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.project_label = QLabel(self.tr("No project loaded"))
        self.status_bar.addPermanentWidget(self.project_label)

    def setup_connections(self):
        self.asset_tree.asset_selected.connect(self.on_asset_selected, Qt.ConnectionType.UniqueConnection)
        self.asset_tree.asset_imported.connect(self.on_asset_imported, Qt.ConnectionType.UniqueConnection)
        # Connect the double-click signal
        self.asset_tree.asset_double_clicked.connect(self.on_asset_double_clicked, Qt.ConnectionType.UniqueConnection)
        # Connect asset deletion signal to update open editors
        self.asset_tree.assetDeleted.connect(self.on_asset_deleted, Qt.ConnectionType.UniqueConnection)

        self.project_manager.project_loaded.connect(self.on_project_loaded, Qt.ConnectionType.UniqueConnection)
        self.project_manager.project_saved.connect(self.on_project_saved, Qt.ConnectionType.UniqueConnection)
        self.project_manager.status_changed.connect(self.update_status, Qt.ConnectionType.UniqueConnection)
        # Refresh the window title when the project's dirty state flips so
        # the trailing " *" appears as soon as the user makes an unsaved
        # change and clears when they save. Qt's UniqueConnection only
        # works with bound methods (not lambdas), so we route through
        # `_on_dirty_changed` to keep the connection deduplicated across
        # re-entries of setup_connections.
        self.project_manager.dirty_changed.connect(
            self._on_dirty_changed, Qt.ConnectionType.UniqueConnection
        )

    def create_action(self, text, shortcut, slot, icon_name=None):
        """Create a QAction with optional icon, shortcut, and slot

        Args:
            text: Action text
            shortcut: Keyboard shortcut (e.g., "Ctrl+S")
            slot: Function to call when action is triggered
            icon_name: QStyle.StandardPixmap enum name (e.g., "SP_FileIcon")

        Returns:
            QAction: The created action
        """
        action = QAction(text, self)

        if shortcut:
            action.setShortcut(shortcut)

        if icon_name:
            try:
                style = self.style()
                # Try to get the enum value from QStyle.StandardPixmap
                pixmap_enum = getattr(QStyle.StandardPixmap, icon_name, None)
                if pixmap_enum is not None:
                    icon = style.standardIcon(pixmap_enum)
                    if not icon.isNull():
                        action.setIcon(icon)
                else:
                    # Invalid icon name provided
                    logger.warning(f"⚠️ Warning: Invalid icon name '{icon_name}' - no such StandardPixmap")
            except AttributeError as e:
                logger.warning(f"⚠️ Warning: Could not access QStyle.StandardPixmap.{icon_name}: {e}")
            except Exception as e:
                logger.warning(f"⚠️ Warning: Could not load icon '{icon_name}': {e}")

        if slot:
            action.triggered.connect(slot)

        return action

    def update_recent_projects_menu(self, menu):
        menu.clear()

        recent_projects = Config.get("recent_projects", [])

        if not recent_projects:
            action = menu.addAction(self.tr("No recent projects"))
            action.setEnabled(False)
            return

        for project_path in recent_projects[:10]:
            if Path(project_path).exists():
                project_name = Path(project_path).name
                action = menu.addAction(project_name)
                action.triggered.connect(lambda checked, path=project_path: self.open_recent_project(path))

        # Add separator and clear option
        menu.addSeparator()
        clear_action = menu.addAction(self.tr("Clear Recent Projects"))
        clear_action.triggered.connect(self.clear_recent_projects)

    def clear_recent_projects(self):
        """Clear the recent projects list"""
        reply = QMessageBox.question(
            self,
            self.tr("Clear Recent Projects"),
            self.tr("Are you sure you want to clear the recent projects list?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            Config.set("recent_projects", [])
            Config.save()
            # Update the menu
            self.update_recent_projects_menu(self.recent_projects_menu)
            # Refresh the Welcome tab's inline list too
            if hasattr(self, 'welcome_tab') and hasattr(self.welcome_tab, 'refresh_recent_projects'):
                self.welcome_tab.refresh_recent_projects()
            self.update_status(self.tr("Recent projects list cleared"))

    def new_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec():
            project_info = dialog.get_project_info()
            logger.debug(f"DEBUG new_project: project_info = {project_info}")

            if self.project_manager.create_project(
                project_info["name"],
                project_info["path"],
                project_info["template"]
            ):
                # Update IDE state with newly created project
                project_path = self.project_manager.current_project_path
                project_data = self.project_manager.current_project_data
                logger.debug(f"DEBUG new_project: project_path = {project_path}")
                logger.debug(f"DEBUG new_project: project_data keys = {list(project_data.keys()) if project_data else None}")

                # Call on_project_loaded to properly initialize the IDE
                self.on_project_loaded(project_path, project_data)
                logger.debug("DEBUG new_project: on_project_loaded called")

                # Add to recent projects
                self.add_to_recent_projects(str(project_path))

                self.update_status(self.tr("Project created successfully"))
            else:
                logger.debug("DEBUG new_project: create_project returned False")
                QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to create project"))

    def open_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Open Project"),
            Config.get("last_project_directory", str(Path.home())),
            self.tr("Project Files (project.json);;Zip Files (*.zip);;All Files (*)")
        )

        if file_path:
            file_path = Path(file_path)

            # Check if it's a .zip file
            if file_path.suffix == '.zip':
                from utils.project_compression import ProjectCompressor
                if ProjectCompressor.is_project_zip(file_path):
                    if self.project_manager.load_project_from_zip(file_path):
                        Config.set("last_project_directory", str(file_path.parent))
                        self.add_to_recent_projects(str(file_path))
                    else:
                        QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to load project from zip"))
                else:
                    QMessageBox.warning(self, self.tr("Invalid Zip"),
                                    self.tr("This zip file does not contain a valid PyGameMaker project"))
            else:
                # Regular folder project
                self.load_project(file_path.parent)

    def open_recent_project(self, project_path):
        self.load_project(Path(project_path))

    # ------------------------------------------------------------------
    # Bundled-samples protection helpers
    # ------------------------------------------------------------------
    #
    # The Welcome tab ships a samples/ folder of native pygm2 projects
    # (maze_1..4, treasure). Those folders are tracked in git and must
    # NEVER be modified by the IDE — otherwise editing inside a sample
    # leaks back into the repo, and Dropbox / file-system permissions
    # produce confusing PermissionError noise when the IDE tries to
    # auto-save.
    #
    # We enforce "samples/ is read-only" structurally rather than via a
    # filesystem chmod (which Dropbox + Windows happily ignore): any
    # path under samples/ that reaches load_project gets transparently
    # copied to the user's working area first, and the copy is what the
    # IDE opens.
    # ------------------------------------------------------------------

    def _samples_dir(self) -> Path:
        """Return the repo-bundled samples/ directory (resolved)."""
        return (Path(__file__).resolve().parent.parent / 'samples').resolve()

    def _is_samples_path(self, path: Path) -> bool:
        """True if ``path`` is the bundled samples/ folder or a child of it."""
        try:
            return path.resolve().is_relative_to(self._samples_dir())
        except (ValueError, OSError):
            return False

    def _promote_samples_to_working_copy(self, samples_path: Path):
        """Copy a bundled-samples project to a fresh folder under the
        user's Documents and return the new path.

        Returns the destination Path on success, None on failure (the
        user sees a QMessageBox.warning in that case). Mirrors the
        destination-picking logic in WelcomeTab._on_open_sample (same
        ``<name>_2`` / ``_3`` suffix dance) so clicking a sample twice
        from any entry point produces independent copies.
        """
        import shutil
        from utils import documents_dir

        default_parent = documents_dir() / "PyGameMaker Projects"
        try:
            default_parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            default_parent = Path.home()

        base_name = samples_path.name
        dest = default_parent / base_name
        suffix = 2
        while dest.exists():
            dest = default_parent / f"{base_name}_{suffix}"
            suffix += 1

        try:
            shutil.copytree(str(samples_path), str(dest))
        except Exception as exc:
            logger.error(f"Sample copy failed: {exc}", exc_info=True)
            QMessageBox.warning(
                self,
                self.tr("Could not open sample"),
                self.tr("Failed to copy the bundled sample to:\n{0}\n\nError:\n{1}").format(
                    str(dest), str(exc)
                ),
            )
            return None

        logger.info(f"Promoted bundled sample to working copy: {samples_path} -> {dest}")
        self.update_status(
            self.tr("Sample copied to: {0}").format(str(dest))
        )
        return dest

    def load_project(self, project_path):
        logger.debug(f"load_project: {project_path}")
        project_path = Path(project_path)

        # If the requested project is under the bundled samples/ folder
        # (clicked from the Welcome dropdown, picked from Recent Projects
        # that retained a pre-rc.12 in-place sample path, or opened by
        # File → Open Project pointed at samples/), transparently promote
        # it to a working copy under <Documents>/PyGameMaker Projects/
        # before loading. The original samples/ folder stays untouched.
        if self._is_samples_path(project_path):
            promoted = self._promote_samples_to_working_copy(project_path)
            if promoted is None:
                return  # copy failed; promotion code emitted its own QMessageBox
            project_path = promoted

        if self.project_manager.load_project(project_path):
            self.asset_tree.project_manager = self.project_manager
            Config.set("last_project_directory", str(project_path.parent))
            self.add_to_recent_projects(str(project_path))
        else:
            logger.warning(f"load_project: project_manager.load_project failed for {project_path}")
            QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to load project"))

    def save_project(self):
            """Save the current project

            Returns:
                bool: True if save was successful, False otherwise
            """
            if self.current_project_path:
                if self.project_manager.save_project():
                    self.update_status(self.tr("Project saved"))
                    return True
                else:
                    QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to save project"))
                    return False
            else:
                # Delegate to save_project_as and return its result
                return self.save_project_as()

    def save_project_as(self):
            """Save the current project to a new location

            Returns:
                bool: True if save was successful, False otherwise
            """
            if not self.current_project_data:
                return False

            directory = QFileDialog.getExistingDirectory(
                self, self.tr("Save Project As"),
                Config.get("last_project_directory", str(Path.home()))
            )

            if directory:
                project_path = Path(directory)
                if self.project_manager.save_project_as(project_path):
                    self.update_status(self.tr("Project saved"))
                    return True
                else:
                    QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to save project"))
                    return False
            else:
                # User cancelled the dialog
                return False

    def project_settings(self):
        if not self.current_project_data:
            QMessageBox.information(self, self.tr("No Project"), self.tr("Please open a project first"))
            return

        dialog = ProjectSettingsDialog(self, self.current_project_data)
        if dialog.exec():
            settings = dialog.get_settings()
            self.current_project_data.update(settings)
            # Also update project manager's data so changes are saved to file
            self.project_manager.current_project_data.update(settings)
            self.project_manager.mark_dirty()
            self.update_window_title()

    def import_sprite(self):
        # Add the project check
        if not getattr(self, 'current_project_path', None):
            from PySide6.QtWidgets import QMessageBox

            reply = QMessageBox.question(
                self,
                self.tr("No Project Loaded"),
                self.tr("You need to create or open a project before importing sprites.\n\n"
                    "Would you like to create a new project now?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self.new_project()
            else:
                logger.debug("🔥 User cancelled")
            return

        self.import_asset("sprites")

    def import_sound(self):
        if not self.ensure_project_loaded("importing sounds"):
            return
        self.import_asset("sounds")

    def import_background(self):
        if not self.ensure_project_loaded("importing backgrounds"):
            return
        self.import_asset("backgrounds")

    def import_asset(self, asset_type):
        if not self.current_project_path:
            return

        try:
            dialog = ImportAssetDialog(asset_type, self)

            if dialog.exec() == QDialog.Accepted:
                files = dialog.get_selected_files()

                if files:
                    self.asset_tree.import_asset(files, asset_type, self.current_project_path)
                else:
                    logger.debug("No files selected")
            else:
                logger.debug("Import cancelled")

        except Exception as e:
            logger.error(f"Error in import_asset: {e}")

    def on_asset_renamed(self, old_name, new_name, asset_type):
            """Handle asset rename signal - refresh UI components"""
            try:

                # Update properties panel if it's showing the renamed asset
                if hasattr(self, 'properties_panel') and self.properties_panel:
                    # Check if properties panel is currently showing the renamed asset
                    if hasattr(self.properties_panel, 'name_edit'):
                        current_displayed_name = self.properties_panel.name_edit.text()

                        if current_displayed_name == old_name:

                            # Find the updated asset data in the tree
                            updated_asset_item = self.find_renamed_asset(new_name, asset_type)
                            if updated_asset_item and hasattr(updated_asset_item, 'asset_data'):
                                # Refresh the properties panel with new data
                                self.properties_panel.set_asset(updated_asset_item.asset_data)

                # Sync in-memory project data from asset manager cache
                if hasattr(self, 'project_manager') and self.project_manager:
                    if hasattr(self.project_manager, 'asset_manager') and self.project_manager.asset_manager:
                        cache = self.project_manager.asset_manager.assets_cache
                        if self.current_project_data and 'assets' in self.current_project_data:
                            for cat_name, cat_data in cache.items():
                                self.current_project_data['assets'][cat_name] = cat_data

                # When an object is renamed, update all open editors (tabbed
                # AND detached) — palettes, room instance references, and
                # other editors' events panels.
                if asset_type == 'object':
                    for widget in self._iter_open_editors():
                        if hasattr(widget, 'rename_object_in_instances'):
                            widget.rename_object_in_instances(old_name, new_name)
                        if hasattr(widget, 'load_available_objects'):
                            widget.load_available_objects()
                        # Reload open object editors whose events were updated
                        if hasattr(widget, 'events_panel') and widget.events_panel:
                            if hasattr(widget, 'load_asset_data') and hasattr(widget, 'asset_name'):
                                obj_data = self.current_project_data.get('assets', {}).get('objects', {}).get(widget.asset_name)
                                if obj_data:
                                    widget.events_panel.load_events_data(obj_data.get('events', {}))

                # If the renamed asset itself is open as an editor, update
                # its asset_name and propagate to dicts / tab text / window
                # title so the IDE doesn't keep stale references.
                if old_name in self.open_editors:
                    editor = self.open_editors.pop(old_name)
                    self.open_editors[new_name] = editor
                    if hasattr(editor, 'asset_name'):
                        editor.asset_name = new_name
                    # If currently floated, move the window registration too.
                    if old_name in self.detached_editor_windows:
                        self.detached_editor_windows[new_name] = self.detached_editor_windows.pop(old_name)
                    # Refresh window title if the editor knows how.
                    if hasattr(editor, 'update_window_title'):
                        try:
                            editor.update_window_title()
                        except Exception:
                            logger.debug(
                                "rename: editor.update_window_title() raised",
                                exc_info=True,
                            )
                    # Update tab text if the editor is in a tab.
                    for i in range(self.editor_tabs.count()):
                        if self.editor_tabs.widget(i) is editor:
                            self.editor_tabs.setTabText(i, new_name)
                            break

                # Refresh asset dropdowns in any open Blockly tab so the new
                # name shows up immediately (works for any asset_type).
                self._refresh_blockly_asset_lists()

            except Exception as e:
                logger.error(f"❌ Error handling asset rename in main window: {e}")

    def _refresh_blockly_asset_lists(self):
        """Push fresh asset-name lists to every open Blockly editor (tabbed
        and floated)."""
        try:
            for widget in self._iter_open_editors():
                blockly_tab = getattr(widget, 'blockly_tab', None)
                if blockly_tab and hasattr(blockly_tab, 'push_asset_lists'):
                    blockly_tab.push_asset_lists()
        except Exception as e:
            logger.debug(f"Could not refresh Blockly asset lists: {e}")

    def _iter_open_editors(self):
        """Yield every open editor widget regardless of whether it's currently
        in a tab or floated. Used by cross-editor refresh paths so that
        detached windows stay in sync with tabbed ones."""
        seen = set()
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if widget is None or widget is self.welcome_tab:
                continue
            seen.add(id(widget))
            yield widget
        for editor in self.open_editors.values():
            if editor is None or id(editor) in seen:
                continue
            yield editor

    def find_renamed_asset(self, asset_name, asset_type):
        """Find an asset item by name and type in the asset tree"""
        try:
            if not hasattr(self, 'asset_tree'):
                return None

            # Search through the asset tree
            root = self.asset_tree.invisibleRootItem()

            for i in range(root.childCount()):
                category_item = root.child(i)

                # Check if this is the right category
                category_text = category_item.text(0).lower()
                expected_category = asset_type.lower() + 's'  # sprites, sounds, etc.

                if category_text == expected_category:
                    # Search through assets in this category
                    for j in range(category_item.childCount()):
                        asset_item = category_item.child(j)

                        if (hasattr(asset_item, 'asset_data') and
                            asset_item.asset_data.get('name') == asset_name):
                            return asset_item

            return None

        except Exception as e:
            logger.error(f"❌ Error finding renamed asset: {e}")
            return None

    def on_asset_deleted(self, asset_type: str, asset_name: str):
        """Handle asset deletion - update open editors that reference the deleted asset"""
        try:
            logger.debug(f"🗑️ IDE: Asset deleted - {asset_type}/{asset_name}")

            # If a sprite was deleted, refresh all open object editors
            if asset_type == "sprites":
                for editor_name, editor in self.open_editors.items():
                    if hasattr(editor, '__class__') and editor.__class__.__name__ == 'ObjectEditor':
                        # Reload sprites in the object editor
                        if hasattr(editor, 'load_project_assets'):
                            editor.load_project_assets()
                            logger.debug(f"🔄 Refreshed sprites in object editor: {editor_name}")

                        # If this object was using the deleted sprite, update its data
                        if hasattr(editor, 'current_object_properties'):
                            if editor.current_object_properties.get('sprite') == asset_name:
                                editor.current_object_properties['sprite'] = ''
                                # Refresh the properties panel to show "None"
                                if hasattr(editor, 'properties_panel'):
                                    editor.properties_panel.load_properties(editor.current_object_properties)
                                logger.debug(f"🔄 Cleared sprite reference in object: {editor_name}")

            # If an object was deleted and it's open, close its editor
            elif asset_type == "objects":
                if asset_name in self.open_editors:
                    self.close_editor_by_name(asset_name)
                    logger.debug(f"🔄 Closed deleted object's editor: {asset_name}")

            # Refresh asset dropdowns in any open Blockly tab so the deleted
            # name disappears from the lists.
            self._refresh_blockly_asset_lists()

        except Exception as e:
            logger.error(f"❌ Error handling asset deletion: {e}")
            import traceback
            traceback.print_exc()

    def create_object(self):
        if not self.ensure_project_loaded("creating objects"):
            return
        self.create_asset("objects")

    def create_room(self):
        if not self.ensure_project_loaded("creating rooms"):
            return
        self.create_asset("rooms")

    def create_script(self):
        if not self.ensure_project_loaded("creating scripts"):
            return
        self.create_asset("scripts")

    def create_font(self):
        if not self.ensure_project_loaded("creating fonts"):
            return
        self.create_asset("fonts")

    def create_asset(self, asset_type):
        if not self.current_project_path:
            QMessageBox.information(self, self.tr("No Project"), self.tr("Please open a project first"))
            return

        # Get asset name from user
        asset_type_singular = asset_type[:-1]  # Remove 's'
        asset_type_title = asset_type_singular.title()

        name, ok = QInputDialog.getText(
            self, self.tr("Create {0}").format(asset_type_title),
            self.tr("Enter name for new {0}:").format(asset_type_singular)
        )

        if not ok or not name:
            return

        # Create the asset data directly
        self.create_asset_with_data(asset_type, name)

    def create_asset_with_data(self, asset_type: str, asset_name: str):
        """Create asset with proper data structure and save to project"""
        try:
            # Create default asset data based on type
            if asset_type == 'rooms':
                asset_data = {
                    'name': asset_name,
                    'width': 1024,
                    'height': 768,
                    'background_color': '#87CEEB',
                    'views_enabled': False,
                    'instances': [],
                    'asset_type': 'room',
                    'imported': True
                }
            elif asset_type == 'objects':
                asset_data = {
                    'name': asset_name,
                    'sprite': '',
                    'visible': True,
                    'solid': False,
                    'persistent': False,
                    'asset_type': 'object',
                    'imported': True,
                    'events': {}
                }
            elif asset_type == 'playgrounds':
                asset_data = {
                    'name': asset_name,
                    'asset_type': 'playground',
                    'imported': True,
                    'arena': {
                        'width': 400,
                        'height': 400,
                        'color': 'white',
                        'ground_texture': '',
                    },
                    'colors': [
                        {'name': 'white', 'r': 1.0, 'g': 1.0, 'b': 1.0},
                        {'name': 'wall', 'r': 0.45, 'g': 0.45, 'b': 0.5},
                    ],
                    'walls': [],
                    'robots': [],
                }
            else:
                # Generic asset data
                asset_data = {
                    'name': asset_name,
                    'asset_type': asset_type[:-1],
                    'imported': True
                }

            # Add to project data
            if not self.current_project_data:
                logger.warning("No project data available")
                return

            assets = self.current_project_data.setdefault('assets', {})
            asset_category = assets.setdefault(asset_type, {})
            asset_category[asset_name] = asset_data

            # IMPORTANT: Also add to asset_manager's cache so it persists on save
            # The save_project() method uses assets_cache to write project data,
            # so if we only add to current_project_data, the asset gets lost on save
            if self.project_manager and self.project_manager.asset_manager:
                cache = self.project_manager.asset_manager.assets_cache
                if asset_type not in cache:
                    from collections import OrderedDict
                    cache[asset_type] = OrderedDict()
                cache[asset_type][asset_name] = asset_data
                logger.debug(f"✅ Added {asset_name} to asset_manager cache")

            # Mark project as dirty and save
            self.project_manager.mark_dirty()

            # Update the asset tree
            self.asset_tree.add_asset(asset_type, asset_name, asset_data)

            # Save the project immediately to persist the new asset
            if self.project_manager.save_project():
                self.update_status(self.tr("Created {0}").format(asset_name))

                # Refresh any open room editors' object palette when a new object is created
                if asset_type == 'objects':
                    self._refresh_room_editor_objects()

                # Push the new asset name into Blockly dropdowns of any open editor.
                self._refresh_blockly_asset_lists()
            else:
                logger.error(f"Failed to save project after creating {asset_name}")

        except Exception as e:
            logger.error(f"Error creating {asset_type[:-1]}: {e}")
            QMessageBox.warning(self, self.tr("Error"),
                            self.tr("Failed to create {0}: {1}").format(asset_type[:-1], e))

    def _refresh_room_editor_objects(self):
        """Refresh the object palette in any open room editors"""
        try:
            for i in range(self.editor_tabs.count()):
                widget = self.editor_tabs.widget(i)
                if hasattr(widget, 'load_available_objects'):
                    widget.load_available_objects()
                    logger.debug(f"✅ Refreshed object palette in room editor tab {i}")
        except Exception as e:
            logger.warning(f"⚠️ Could not refresh room editor objects: {e}")

    def test_game(self):
        """Test the current game"""
        # Check if a game subprocess is already running
        if hasattr(self, '_game_process') and self._game_process is not None:
            if self._game_process.poll() is None:  # Still running
                QMessageBox.information(
                    self,
                    self.tr("Game Running"),
                    self.tr("A game is already running. Please close it first.")
                )
                return

        # Check if project is open
        if not self.current_project_path:
            QMessageBox.warning(
                self,
                self.tr("No Project"),
                self.tr("Please open or create a project first before testing a game.")
            )
            return

        # Sync all open editors' data to the project before testing
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if hasattr(widget, 'get_data') and hasattr(widget, 'asset_name') and widget.asset_name:
                try:
                    data = widget.get_data()
                    self.on_editor_save_requested(widget.asset_name, data)
                except Exception as e:
                    logger.debug(f"Could not sync editor data for {getattr(widget, 'asset_name', '?')}: {e}")

        # Save project before testing
        self.save_project()

        # Validate project and show warnings
        self._show_validation_warnings()

        try:
            self.update_status(self.tr("Running game..."))

            project_json = self.current_project_path / "project.json"

            if not project_json.exists():
                QMessageBox.warning(
                    self,
                    self.tr("Project Error"),
                    self.tr("project.json not found in project directory")
                )
                return

            # Run game in subprocess to avoid OpenGL conflicts between Qt WebEngine and pygame
            # This isolates pygame's SDL/OpenGL context from Qt's Chromium OpenGL context
            game_script = Path(__file__).parent.parent / "runtime" / "run_game.py"

            # Check if we're running from a packaged executable (Nuitka/PyInstaller)
            # In that case, sys.executable may point to a non-existent Python path
            # Detection methods:
            # 1. PyInstaller sets sys.frozen
            # 2. Nuitka onefile: sys.executable doesn't exist (points to fictional python)
            # 3. __file__ is in /tmp/ directory (Nuitka extraction)
            # 4. Check if executable name doesn't contain 'python'
            exe_exists = os.path.exists(sys.executable)
            file_dir = os.path.dirname(os.path.abspath(__file__))
            temp_dir = os.environ.get('TEMP', '')
            is_packaged = (
                getattr(sys, 'frozen', False) or  # PyInstaller
                not exe_exists or  # Nuitka: sys.executable doesn't exist
                file_dir.startswith('/tmp/') or  # Nuitka onefile extraction
                (temp_dir and file_dir.startswith(temp_dir))  # Windows temp (avoid empty string match)
            )
            logger.debug(f"🔍 Packaged detection: frozen={getattr(sys, 'frozen', False)}, exe_exists={exe_exists}, file_dir={file_dir}, is_packaged={is_packaged}")

            if is_packaged:
                # When packaged, run game in-process using the game runner
                # This works because pygame is bundled in the package
                if self.game_runner.test_game(str(self.current_project_path), Config.get('language', 'en')):
                    self.update_status(self.tr("Game closed"))
                else:
                    self.update_status(self.tr("Game test failed"))
                return

            # Run the game subprocess
            # Pass language code as second argument for runtime translations
            language = Config.get('language', 'en')

            # Use Popen instead of run to avoid blocking the Qt event loop
            # This allows the IDE to remain responsive while the game runs
            env = os.environ.copy()
            # Ensure clean display environment for pygame on Linux
            if sys.platform != 'win32' and sys.platform != 'darwin':
                # Force X11 driver on Linux for better compatibility when launched from Qt
                env['SDL_VIDEODRIVER'] = 'x11'

            # On Windows, suppress the brief python.exe console window that
            # would otherwise flash before pygame's SDL window appears.
            # CREATE_NO_WINDOW is Windows-only; getattr() yields 0 elsewhere,
            # which is a no-op for Popen on POSIX.
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

            # Capture the game's stderr to a temp *file* (not subprocess.PIPE).
            # A PIPE nobody drains can deadlock the child once the OS pipe
            # buffer fills — the exact hazard the old "don't capture output"
            # comment was avoiding. A file has no such buffer limit, so we get
            # the crash traceback without risking a hang. Drained + deleted in
            # _drain_game_stderr when the process exits.
            import tempfile
            stderr_fd, stderr_path = tempfile.mkstemp(prefix='pygm2_game_', suffix='.log')
            self._game_stderr_path = stderr_path
            self._game_stderr_handle = os.fdopen(stderr_fd, 'w')

            process = subprocess.Popen(
                [sys.executable, str(game_script), str(project_json), language],
                cwd=str(self.current_project_path),
                env=env,
                stdout=None,
                stderr=self._game_stderr_handle,
                creationflags=creationflags,
            )

            # Store reference to allow stopping the game
            self._game_process = process

            # Use QTimer to check when game exits without blocking
            self._check_game_timer = QTimer(self)
            self._check_game_timer.timeout.connect(self._check_game_process)
            self._check_game_timer.start(100)  # Check every 100ms

            self.update_status(self.tr("Game running... (close game window to return)"))

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Game Test Error"),
                self.tr("Failed to run game:\n\n{0}\n\nCheck console for details.").format(str(e))
            )
            logger.error(f"❌ Game test error: {e}")
            import traceback
            traceback.print_exc()
            self.update_status(self.tr("Game test failed"))

    def _check_game_process(self):
        """Check if the game subprocess has finished (called by QTimer)"""
        if not hasattr(self, '_game_process') or self._game_process is None:
            if hasattr(self, '_check_game_timer') and self._check_game_timer:
                self._check_game_timer.stop()
            return

        # Check if process has terminated
        return_code = self._game_process.poll()
        if return_code is not None:
            # Process has finished
            self._check_game_timer.stop()
            self._game_process = None

            if return_code != 0:
                logger.debug(f"Game exited with code: {return_code}")

            self._drain_game_stderr(return_code)
            self.update_status(self.tr("Game closed"))

    def _drain_game_stderr(self, return_code):
        """Read, surface, and clean up the game subprocess's captured stderr.

        On a non-zero exit the captured traceback is logged so a crashing game
        no longer fails silently. The temp file is always removed. Safe to call
        more than once / when no capture is active.
        """
        handle = getattr(self, '_game_stderr_handle', None)
        path = getattr(self, '_game_stderr_path', None)
        self._game_stderr_handle = None
        self._game_stderr_path = None

        if handle is not None:
            try:
                handle.close()
            except OSError:
                pass
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                output = f.read().strip()
            if output and return_code not in (0, None):
                logger.error(
                    f"Game subprocess (exit {return_code}) stderr:\n{output}"
                )
        except OSError as e:
            logger.debug(f"Could not read game stderr log: {e}")
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    def stop_game(self):
        """Stop the running game subprocess"""
        return_code = None
        if hasattr(self, '_game_process') and self._game_process is not None:
            try:
                self._game_process.terminate()
                # Give it a moment to terminate gracefully
                try:
                    return_code = self._game_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._game_process.kill()
                self._game_process = None
                self.update_status(self.tr("Game stopped"))
            except Exception as e:
                logger.error(f"Error stopping game: {e}")
        if hasattr(self, '_check_game_timer') and self._check_game_timer:
            self._check_game_timer.stop()
        self._drain_game_stderr(return_code)

    def debug_game(self):
        """Run game in debug mode with additional logging"""
        if self.game_runner.is_game_running():
            QMessageBox.information(
                self,
                self.tr("Game Running"),
                self.tr("A game is already running. Please stop it first.")
            )
            return

        # Save project first
        if self.project_manager.is_dirty():
            self.save_project()

        # For now, debug mode is the same as test mode with verbose output
        # Future: Add breakpoints, variable inspection, step-through debugging
        self.update_status(self.tr("Starting game in debug mode..."))

        QMessageBox.information(
            self,
            self.tr("Debug Mode"),
            self.tr("Debug mode will start the game with verbose console output.\n\n"
                    "Future features:\n"
                    "• Breakpoints\n"
                    "• Variable inspection\n"
                    "• Step-through execution\n"
                    "• Performance profiling\n\n"
                    "For now, check the console for debug messages.")
        )

        # Run game in test mode (debug mode to be implemented)
        if self.game_runner.test_game(str(self.current_project_path), Config.get('language', 'en')):
            self.update_status(self.tr("Game started in debug mode - Check console for debug output"))
        else:
            self.update_status(self.tr("Failed to start game"))
            QMessageBox.warning(
                self,
                self.tr("Game Error"),
                self.tr("Failed to start the game. Check console for details.")
            )

    def _show_validation_warnings(self):
        """Validate project and show any warnings to the user"""
        issues = self.project_manager.validate_project()

        if not issues:
            return

        # Separate errors and warnings
        errors = [i for i in issues if i['type'] == 'error']
        warnings = [i for i in issues if i['type'] == 'warning']

        # Build message
        message_parts = []

        if errors:
            message_parts.append(self.tr("Errors:"))
            for err in errors:
                message_parts.append(f"  • {err['message']}")
            message_parts.append("")

        if warnings:
            message_parts.append(self.tr("Warnings:"))
            for warn in warnings:
                message_parts.append(f"  • {warn['message']}")

        message = "\n".join(message_parts)

        if errors:
            # Show errors as critical - they will likely cause problems
            QMessageBox.warning(
                self,
                self.tr("Project Validation Issues"),
                message
            )
        elif warnings:
            # Show warnings as information
            QMessageBox.information(
                self,
                self.tr("Project Validation Warnings"),
                message
            )

    def export_game(self):
        """Export game - shows dialog with export options"""
        # Check if project is open
        if not self.current_project_path:
            QMessageBox.warning(
                self,
                self.tr("No Project"),
                self.tr("Please open or create a project first before exporting a game.")
            )
            return

        # Validate project and show warnings
        self._show_validation_warnings()

        # Create export options dialog
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QButtonGroup, QRadioButton

        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Export Game"))
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(self.tr("<h3>Export Game</h3>")))
        layout.addWidget(QLabel(self.tr("Choose export format:")))

        # Export format options
        button_group = QButtonGroup(dialog)

        html5_radio = QRadioButton(self.tr("HTML5 (Web Browser) - ✅ Available"))
        html5_radio.setChecked(True)
        button_group.addButton(html5_radio, 1)
        layout.addWidget(html5_radio)

        import platform as _platform
        if _platform.system() == 'Windows':
            windows_radio = QRadioButton(self.tr("Windows Executable (.exe) - ✅ Available"))
        else:
            windows_radio = QRadioButton(self.tr("Windows Executable (.exe) - ⚠️ Requires Windows"))
        windows_radio.setEnabled(True)
        button_group.addButton(windows_radio, 2)
        layout.addWidget(windows_radio)

        if _platform.system() == 'Linux':
            linux_radio = QRadioButton(self.tr("Linux Binary - ✅ Available"))
        else:
            linux_radio = QRadioButton(self.tr("Linux Binary - ⚠️ Requires Linux"))
        linux_radio.setEnabled(True)
        button_group.addButton(linux_radio, 3)
        layout.addWidget(linux_radio)

        if _platform.system() == 'Darwin':
            mac_radio = QRadioButton(self.tr("macOS Application (.app) - ✅ Available"))
        else:
            mac_radio = QRadioButton(self.tr("macOS Application (.app) - ⚠️ Requires macOS"))
        mac_radio.setEnabled(True)
        button_group.addButton(mac_radio, 4)
        layout.addWidget(mac_radio)

        if _platform.system() in ('Linux', 'Darwin'):
            android_radio = QRadioButton(self.tr("Android Package (.apk) - ✅ Available"))
        elif _platform.system() == 'Windows':
            # Check if WSL is available for Android export on Windows
            try:
                from export.android.wsl_bridge import WSLBridge
                _wsl = WSLBridge()
                if _wsl.is_wsl_available():
                    android_radio = QRadioButton(
                        self.tr("Android Package (.apk) - ✅ Available (via WSL)"))
                else:
                    android_radio = QRadioButton(
                        self.tr("Android Package (.apk) - ⚠️ Requires WSL (not detected)"))
            except Exception:
                android_radio = QRadioButton(
                    self.tr("Android Package (.apk) - ⚠️ Requires WSL (not detected)"))
        else:
            android_radio = QRadioButton(self.tr("Android Package (.apk) - ⚠️ Requires Linux or macOS"))
        android_radio.setEnabled(True)
        button_group.addButton(android_radio, 5)
        layout.addWidget(android_radio)

        if _platform.system() == 'Darwin':
            ios_radio = QRadioButton(self.tr("iOS App (.ipa) - ✅ Available (macOS only)"))
        else:
            ios_radio = QRadioButton(self.tr("iOS App (.ipa) - ⚠️ Requires macOS with Xcode"))
        ios_radio.setEnabled(True)
        button_group.addButton(ios_radio, 6)
        layout.addWidget(ios_radio)

        # Buttons
        button_layout = QHBoxLayout()
        export_btn = QPushButton(self.tr("Export"))
        export_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(export_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        if dialog.exec() == QDialog.Accepted:
            selected_id = button_group.checkedId()

            if selected_id == 1:  # HTML5
                self.export_html5()
            elif selected_id == 2:  # Windows EXE
                self.export_windows_exe()
            elif selected_id == 3:  # Linux Binary
                self.export_linux_binary()
            elif selected_id == 4:  # macOS App
                self.export_macos_app()
            elif selected_id == 5:  # Android APK
                self.export_android_apk()
            elif selected_id == 6:  # iOS IPA
                self.export_ios_app()
            else:
                QMessageBox.information(
                    self,
                    self.tr("Coming Soon"),
                    self.tr("This export format is not yet available.")
                )

    # ------------------------------------------------------------------
    # Platform export methods — thin shells delegating to the shared
    # _run_export_with_progress helper below. Each shell only picks the
    # exporter class, the per-target settings dict, and the user-facing
    # labels that differ between targets.
    # ------------------------------------------------------------------

    def export_windows_exe(self):
        """Handle Windows EXE export with progress dialog."""
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_exe')
        if not output_dir:
            return
        from export.exe.exe_exporter import ExeExporter
        self._run_export_with_progress(
            exporter_class=ExeExporter,
            output_dir=output_dir,
            export_settings={
                'output_path': output_dir,
                'include_assets': True,
                'optimize': True,
                'include_debug': False,
            },
            dialog_title=self.tr("Exporting Game"),
            status_text=self.tr("Preparing export..."),
            dialog_size=(500, 150),
            success_title=self.tr("Export Complete"),
            failure_title=self.tr("Export Failed"),
            open_folder_prompt=self.tr("Would you like to open the output folder?"),
            show_cancel=False,
        )

    def export_linux_binary(self):
        """Handle Linux binary export with progress dialog."""
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_linux')
        if not output_dir:
            return
        from export.linux.linux_exporter import LinuxExporter
        self._run_export_with_progress(
            exporter_class=LinuxExporter,
            output_dir=output_dir,
            export_settings={
                'output_path': output_dir,
                'include_assets': True,
                'optimize': True,
                'include_debug': False,
            },
            dialog_title=self.tr("Exporting Game"),
            status_text=self.tr("Preparing export..."),
            dialog_size=(500, 150),
            success_title=self.tr("Export Complete"),
            failure_title=self.tr("Export Failed"),
            open_folder_prompt=self.tr("Would you like to open the output folder?"),
            show_cancel=False,
        )

    def export_macos_app(self):
        """Handle macOS .app export with progress dialog."""
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_macos')
        if not output_dir:
            return
        from export.macos.macos_exporter import MacOSExporter
        self._run_export_with_progress(
            exporter_class=MacOSExporter,
            output_dir=output_dir,
            export_settings={
                'output_path': output_dir,
                'include_assets': True,
                'optimize': True,
                'include_debug': False,
            },
            dialog_title=self.tr("Exporting Game"),
            status_text=self.tr("Preparing export..."),
            dialog_size=(500, 150),
            success_title=self.tr("Export Complete"),
            failure_title=self.tr("Export Failed"),
            open_folder_prompt=self.tr("Would you like to open the output folder?"),
            show_cancel=False,
        )

    def export_android_apk(self):
        """Handle Android APK export with progress dialog (Cancel supported)."""
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_android')
        if not output_dir:
            return
        from export.android.android_exporter import AndroidExporter
        self._run_export_with_progress(
            exporter_class=AndroidExporter,
            output_dir=output_dir,
            export_settings={
                'output_path': output_dir,
                'include_assets': True,
                'optimize': True,
                'include_debug': False,
            },
            dialog_title=self.tr("Exporting Game"),
            status_text=self.tr("Preparing export..."),
            dialog_size=(500, 150),
            success_title=self.tr("Export Complete"),
            failure_title=self.tr("Export Failed"),
            open_folder_prompt=self.tr("Would you like to open the output folder?"),
            show_cancel=True,
            cancel_status_message=self.tr("Export cancelled"),
        )

    def export_ios_app(self):
        """Handle iOS IPA export with progress dialog (macOS + free Apple ID)."""
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_ios')
        if not output_dir:
            return
        from export.ios.ios_exporter import iOSExporter
        # iOS deliberately omits 'optimize' from the settings dict — the
        # iOSExporter does not currently consume it. Preserve this so the
        # exporter sees the same payload as before consolidation.
        self._run_export_with_progress(
            exporter_class=iOSExporter,
            output_dir=output_dir,
            export_settings={
                'output_path': output_dir,
                'include_assets': True,
                'include_debug': False,
            },
            dialog_title=self.tr("Building iOS App"),
            status_text=self.tr("Preparing iOS export..."),
            dialog_size=(520, 160),
            success_title=self.tr("iOS Export Complete"),
            failure_title=self.tr("iOS Export Failed"),
            open_folder_prompt=self.tr("Open the output folder?"),
            show_cancel=True,
            cancel_status_message=self.tr("iOS export cancelled"),
        )

    def export_aseba_code(self):
        """Export Thymio objects from the project as Aseba AESL code.

        Aseba export is synchronous and fast (it just writes text files),
        so it bypasses the progress-dialog helper used by the platform
        binary exporters and runs inline with a status update + a single
        completion dialog.
        """
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_aseba')
        if not output_dir:
            return

        from export.Aseba.aseba_exporter import AsebaExporter
        project_file = str(Path(self.current_project_path) / "project.json")

        self.update_status(self.tr("Exporting Aseba code..."))
        try:
            success = AsebaExporter().export(project_file, output_dir)
        except Exception as e:
            logger.error(f"Aseba export failed: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Aseba Export Failed"),
                self.tr("Failed to export Aseba code:\n\n{0}").format(str(e))
            )
            self.update_status(self.tr("Aseba export failed"))
            return

        if not success:
            QMessageBox.warning(
                self,
                self.tr("Aseba Export"),
                self.tr(
                    "No Thymio objects found in this project, so no Aseba "
                    "code was generated. Add a Thymio object to the project "
                    "and try again."
                )
            )
            self.update_status(self.tr("Aseba export: nothing to export"))
            return

        self.update_status(self.tr("Aseba export complete"))
        result = QMessageBox.information(
            self,
            self.tr("Aseba Export Complete"),
            self.tr("Aseba .aesl files written to:\n{0}\n\n"
                    "Would you like to open the output folder?").format(output_dir),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if result == QMessageBox.StandardButton.Yes:
            import platform
            if platform.system() == 'Windows':
                os.startfile(output_dir)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', output_dir])
            else:  # Linux
                subprocess.run(['xdg-open', output_dir])

    # ------------------------------------------------------------------
    # Helpers backing the shells above.
    # ------------------------------------------------------------------

    def _require_open_project(self) -> bool:
        """Show the standard "no project" warning and return False when
        no project is currently open. Centralises the guard that all five
        platform-export methods used to inline.
        """
        if not self.current_project_path:
            QMessageBox.warning(
                self,
                self.tr("No Project"),
                self.tr("Please open or create a project first.")
            )
            return False
        return True

    def _ask_export_dir(self, suffix: str) -> str:
        """Prompt the user for an output directory, defaulting to
        ``<localised-Desktop>/<sanitised-project-name><suffix>``.
        Returns the absolute path string or "" if cancelled.

        Uses ``utils.desktop_dir()`` instead of ``Path.home() / "Desktop"``
        so the default works on Linux locales whose desktop is "Bureau",
        "Schreibtisch", etc., and on Windows where the desktop may be
        OneDrive-redirected.
        """
        from utils import desktop_dir
        default_name = self.current_project_data.get('name', 'Game').replace(' ', '_')
        return QFileDialog.getExistingDirectory(
            self,
            self.tr("Choose Export Location"),
            str(desktop_dir() / f"{default_name}{suffix}"),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

    def _run_export_with_progress(
        self,
        *,
        exporter_class,
        output_dir: str,
        export_settings: dict,
        dialog_title: str,
        status_text: str,
        dialog_size: tuple,
        success_title: str,
        failure_title: str,
        open_folder_prompt: str,
        show_cancel: bool = False,
        cancel_status_message: str = "",
    ):
        """Drive an exporter to completion behind a modal progress dialog.

        Centralises the construction of the progress UI and the
        success/failure/cancel handlers that all five platform export
        methods previously inlined. Behaviour is identical to those
        per-method implementations; the only variation between targets
        is encoded in this function's keyword arguments.

        Note: ``exporter_class`` is a *class* (not an instance) so the
        helper can instantiate it AFTER the progress dialog is built,
        matching the construction order of the original per-method
        implementations. Caller-side ``ExporterClass()`` would invert
        the order because keyword arguments are evaluated before the
        call.
        """
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle(dialog_title)
        progress_dialog.setModal(True)
        progress_dialog.resize(*dialog_size)

        layout = QVBoxLayout(progress_dialog)

        status_label = QLabel(status_text)
        layout.addWidget(status_label)

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        layout.addWidget(progress_bar)

        cancel_btn = None
        if show_cancel:
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            cancel_btn = QPushButton(self.tr("Cancel"))
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)

        # Construct the exporter AFTER the dialog widgets, to preserve
        # the construction order observable by code review tooling.
        exporter = exporter_class()
        _export_cancelled = False

        def update_progress(percent, message):
            progress_bar.setValue(percent)
            status_label.setText(message)

        def export_finished(success, message):
            progress_dialog.accept()
            if show_cancel and _export_cancelled:
                self.update_status(cancel_status_message)
                return
            if success:
                result = QMessageBox.information(
                    self,
                    success_title,
                    message + "\n\n" + open_folder_prompt,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if result == QMessageBox.StandardButton.Yes:
                    import os
                    import platform
                    if platform.system() == 'Windows':
                        os.startfile(output_dir)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', output_dir])
                    else:  # Linux
                        subprocess.run(['xdg-open', output_dir])
            else:
                QMessageBox.critical(self, failure_title, message)

        def cancel_export():
            nonlocal _export_cancelled
            _export_cancelled = True
            cancel_btn.setEnabled(False)
            status_label.setText(self.tr("Cancelling..."))
            exporter.cancel_requested = True

        exporter.progress_update.connect(update_progress)
        exporter.export_complete.connect(export_finished)
        if show_cancel and cancel_btn is not None:
            cancel_btn.clicked.connect(cancel_export)

        export_thread = ExportThread(
            exporter,
            str(self.current_project_path),
            output_dir,
            export_settings
        )

        export_thread.start()
        progress_dialog.exec()
        export_thread.wait()

    def _active_editor(self):
        """Return the editor the user is interacting with right now.

        Prefers the currently focused widget's owning editor (which works
        for detached editor windows), falling back to the active tab's
        widget. Returns None if no editor is in focus or the active tab
        is the welcome tab.
        """
        from PySide6.QtWidgets import QApplication
        focused = QApplication.focusWidget()
        if focused is not None:
            open_set = set(self.open_editors.values())
            walk = focused
            while walk is not None:
                if walk in open_set:
                    return walk
                walk = walk.parent()
        current = self.editor_tabs.currentWidget()
        if current is None or current is self.welcome_tab:
            return None
        return current

    def undo(self):
        """Handle undo - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is None:
            logger.debug("Undo (no editor-specific undo available)")
            return
        if hasattr(editor, 'undo'):
            try:
                editor.undo()
            except Exception:
                logger.debug("Undo: editor.undo() raised", exc_info=True)

    def redo(self):
        """Handle redo - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is None:
            logger.debug("Redo (no editor-specific redo available)")
            return
        if hasattr(editor, 'redo'):
            try:
                editor.redo()
            except Exception:
                logger.debug("Redo: editor.redo() raised", exc_info=True)

    def cut(self):
        """Handle cut - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is not None:
            if editor.__class__.__name__ == 'RoomEditor' and hasattr(editor, 'cut_instance'):
                editor.cut_instance()
                return
            if hasattr(editor, 'cut'):
                try:
                    editor.cut()
                    return
                except Exception:
                    logger.debug("Cut: editor.cut() raised", exc_info=True)
        # Fall back to the focused widget for plain text-edit cut
        focused_widget = self.focusWidget()
        if focused_widget and hasattr(focused_widget, 'cut'):
            try:
                focused_widget.cut()
            except Exception:
                logger.debug("Cut: focusWidget().cut() raised", exc_info=True)

    def copy(self):
        """Handle copy - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is not None:
            if editor.__class__.__name__ == 'RoomEditor' and hasattr(editor, 'copy_instance'):
                editor.copy_instance()
                return
            if hasattr(editor, 'copy'):
                try:
                    editor.copy()
                    return
                except Exception:
                    logger.debug("Copy: editor.copy() raised", exc_info=True)
        focused_widget = self.focusWidget()
        if focused_widget and hasattr(focused_widget, 'copy'):
            try:
                focused_widget.copy()
            except Exception:
                logger.debug("Copy: focusWidget().copy() raised", exc_info=True)

    def paste(self):
        """Handle paste - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is not None:
            if editor.__class__.__name__ == 'RoomEditor' and hasattr(editor, 'paste_instance'):
                editor.paste_instance()
                return
            if hasattr(editor, 'paste'):
                try:
                    editor.paste()
                    return
                except Exception:
                    logger.debug("Paste: editor.paste() raised", exc_info=True)
        focused_widget = self.focusWidget()
        if focused_widget and hasattr(focused_widget, 'paste'):
            try:
                focused_widget.paste()
            except Exception:
                logger.debug("Paste: focusWidget().paste() raised", exc_info=True)

    def duplicate(self):
        """Handle duplicate - delegate to active editor (tabbed or detached)."""
        editor = self._active_editor()
        if editor is not None and editor.__class__.__name__ == 'RoomEditor':
            if hasattr(editor, 'duplicate_instance'):
                editor.duplicate_instance()
                return
        logger.debug("Duplicate action (no room editor active)")

    def preferences(self):
            """Open preferences/settings dialog"""
            from dialogs.preferences_dialog import PreferencesDialog
            dialog = PreferencesDialog(self)
            dialog.exec()

    def configure_blockly(self):
        """Open Blockly configuration dialog to customize available blocks"""
        from config.blockly_config import load_config, save_config, PRESETS, BlocklyConfig

        # Try to load preset from current project settings first
        current_config = None
        if self.current_project_data:
            project_preset = self.current_project_data.get('settings', {}).get('blockly_preset')
            if project_preset and project_preset in PRESETS:
                # Make a copy to avoid modifying the original preset
                current_config = BlocklyConfig.from_dict(PRESETS[project_preset].to_dict())

        # Fall back to global config if no project preset
        if not current_config:
            current_config = load_config()

        # Show dialog
        dialog = BlocklyConfigDialog(self, current_config)
        if dialog.exec() == QDialog.Accepted:
            # Save the new configuration
            new_config = dialog.config
            save_config(new_config)

            # Also save to project settings if a project is open
            if self.current_project_path and self.current_project_data:
                if 'settings' not in self.current_project_data:
                    self.current_project_data['settings'] = {}
                self.current_project_data['settings']['blockly_preset'] = new_config.preset_name
                self.save_project()
                logger.info(f"✅ Saved Blockly preset '{new_config.preset_name}' to project")

            # Refresh any open GM80 events panels
            self.refresh_event_panels_config()

            # Show confirmation
            QMessageBox.information(
                self,
                self.tr("Configuration Saved"),
                self.tr("Blockly configuration has been saved.\n\n"
                        "The new event/block selection is now active in:\n"
                        "• Visual programming editor (Blockly)\n"
                        "• Traditional event editor\n\n"
                        "Changes apply immediately to currently open editors.")
            )

            logger.info(f"✅ Blockly configuration updated: {new_config.preset_name} preset")
            logger.debug(f"   Enabled blocks: {len(new_config.enabled_blocks)}")
            logger.debug(f"   Enabled categories: {', '.join(new_config.enabled_categories)}")

    def configure_thymio(self):
        """Open Thymio configuration dialog to customize available Thymio blocks"""
        from config.blockly_config import load_config, save_config, PRESETS, BlocklyConfig

        # Try to load preset from current project settings first
        current_config = None
        if self.current_project_data:
            project_preset = self.current_project_data.get('settings', {}).get('blockly_preset')
            if project_preset and project_preset in PRESETS:
                current_config = BlocklyConfig.from_dict(PRESETS[project_preset].to_dict())

        # Fall back to global config if no project preset
        if not current_config:
            current_config = load_config()

        # Show Thymio-specific dialog
        dialog = ThymioConfigDialog(self, current_config)
        if dialog.exec() == QDialog.Accepted:
            # Save the new configuration
            new_config = dialog.config
            save_config(new_config)

            # Also save to project settings if a project is open
            if self.current_project_path and self.current_project_data:
                if 'settings' not in self.current_project_data:
                    self.current_project_data['settings'] = {}
                self.current_project_data['settings']['blockly_preset'] = new_config.preset_name
                self.save_project()
                logger.info("✅ Saved Thymio preset to project")

            # Refresh any open events panels
            self.refresh_event_panels_config()

            # Show confirmation
            QMessageBox.information(
                self,
                self.tr("Thymio Configuration Saved"),
                self.tr("Thymio block configuration has been saved.\n\n"
                        "The new Thymio event/action selection is now active.")
            )

            logger.info("✅ Thymio configuration updated")

    def refresh_event_panels_config(self):
        """Refresh configuration in all open object editors (events panel + blockly)"""
        from config.blockly_config import PRESETS, BlocklyConfig, load_config

        # Determine the active config
        config = None
        if self.current_project_data:
            preset_name = self.current_project_data.get('settings', {}).get('blockly_preset')
            if preset_name and preset_name in PRESETS:
                config = BlocklyConfig.from_dict(PRESETS[preset_name].to_dict())
        if not config:
            config = load_config()

        # Apply to all open object editors
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            # Update events panel
            if hasattr(widget, 'events_panel') and widget.events_panel:
                widget.events_panel.apply_config(config)
                logger.debug(f"   ♻️ Reloaded event panel config for: {self.editor_tabs.tabText(i)}")
            # Update blockly editor
            if hasattr(widget, 'blockly_tab') and widget.blockly_tab:
                blockly_widget = getattr(widget.blockly_tab, 'blockly_widget', None)
                if blockly_widget and hasattr(blockly_widget, 'apply_configuration'):
                    blockly_widget.apply_configuration(config)

    def toggle_thymio_tab(self):
        """Toggle visibility of Thymio tab in object editors"""
        show_thymio = self.show_thymio_tab_action.isChecked()

        # Save preference
        Config.set('show_thymio_tab', show_thymio)

        # Update all open object editors
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if hasattr(widget, 'set_thymio_tab_visible'):
                widget.set_thymio_tab_visible(show_thymio)

        logger.info(f"Thymio tab visibility: {'shown' if show_thymio else 'hidden'}")

    def show_thymio_playground(self):
        """Open the Thymio Playground simulator window"""
        from widgets.thymio_playground import ThymioPlaygroundWindow

        # Create and show the playground window
        self.thymio_playground = ThymioPlaygroundWindow(self)
        self.thymio_playground.show()
        logger.info("Opened Thymio Playground window")

    def show_thymio_event_selector(self):
        """Show the Thymio event selector dialog"""
        from dialogs.thymio_event_selector import ThymioEventSelector

        dialog = ThymioEventSelector(self)
        if dialog.exec() == QDialog.Accepted:
            selected_event = dialog.get_selected_event()
            if selected_event:
                # Try to add event to current object editor
                current_widget = self.editor_tabs.currentWidget()
                if hasattr(current_widget, 'events_panel'):
                    # Call the panel's Thymio event method
                    if hasattr(current_widget.events_panel, 'add_thymio_event_with_selector'):
                        # Directly add the event since we already selected it
                        events_panel = current_widget.events_panel
                        if selected_event in events_panel.current_events_data:
                            QMessageBox.information(
                                self,
                                self.tr("Event Exists"),
                                self.tr("This Thymio event already exists in the object.")
                            )
                        else:
                            events_panel.current_events_data[selected_event] = {"actions": []}
                            events_panel.refresh_events_display()
                            events_panel.events_modified.emit()
                else:
                    QMessageBox.information(
                        self,
                        self.tr("No Object Editor"),
                        self.tr("Please open an object editor first to add Thymio events.")
                    )

    def show_thymio_action_selector(self):
        """Show the Thymio action selector dialog"""
        from dialogs.thymio_action_selector import ThymioActionSelector

        # Check if we have an object editor open
        current_widget = self.editor_tabs.currentWidget()
        if not hasattr(current_widget, 'events_panel'):
            QMessageBox.information(
                self,
                self.tr("No Object Editor"),
                self.tr("Please open an object editor first to add Thymio actions.")
            )
            return

        events_panel = current_widget.events_panel
        # Get the currently selected event
        current_item = events_panel.events_tree.currentItem()
        if not current_item:
            QMessageBox.information(
                self,
                self.tr("No Event Selected"),
                self.tr("Please select an event first to add actions to it.")
            )
            return

        # Get event name (handle both top-level events and sub-events)
        event_name = current_item.data(0, Qt.UserRole)
        if not event_name or not isinstance(event_name, str):
            QMessageBox.information(
                self,
                self.tr("Invalid Selection"),
                self.tr("Please select an event (not an action) to add Thymio actions.")
            )
            return

        dialog = ThymioActionSelector(self)
        if dialog.exec() == QDialog.Accepted:
            action_name, parameters = dialog.get_result()
            if action_name:
                # Add action to the selected event
                action_data = {
                    "action": action_name,
                    "parameters": parameters
                }

                if event_name in events_panel.current_events_data:
                    events_panel.current_events_data[event_name]["actions"].append(action_data)
                    events_panel.refresh_events_display()
                    events_panel.events_modified.emit()

    def validate_project(self):
        """Validate project structure and assets"""
        if not self.current_project_path:
            QMessageBox.information(
                self,
                self.tr("No Project"),
                self.tr("Please open a project first to validate.")
            )
            return

        # Basic validation
        issues = []

        # Check if project.json exists
        project_file = Path(self.current_project_path) / "project.json"
        if not project_file.exists():
            issues.append("• project.json file is missing")

        # Check for asset directories
        for asset_type in ['sprites', 'sounds', 'backgrounds', 'objects', 'rooms', 'scripts']:
            asset_dir = Path(self.current_project_path) / asset_type
            if not asset_dir.exists():
                issues.append(f"• {asset_type} directory is missing")

        # Show results
        if issues:
            QMessageBox.warning(
                self,
                self.tr("Validation Issues Found"),
                self.tr("Project validation found the following issues:\n\n") + "\n".join(issues)
            )
        else:
            QMessageBox.information(
                self,
                self.tr("Validation Passed"),
                self.tr("Project structure is valid!\n\n"
                        "✓ All required directories exist\n"
                        "✓ project.json is present")
            )

    def migrate_project_structure(self):
        """Migrate project to use external files for objects and rooms"""
        if not self.current_project_path:
            QMessageBox.information(
                self,
                self.tr("No Project"),
                self.tr("Please open a project first to migrate.")
            )
            return

        reply = QMessageBox.question(
            self,
            self.tr("Migrate Project Structure"),
            self.tr("This will migrate your project to use a modular file structure:\n\n"
                    "• Objects will be saved to objects/*.json\n"
                    "• Rooms will be saved to rooms/*.json\n\n"
                    "This makes the project easier to manage and version control.\n\n"
                    "Do you want to continue?"),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.project_manager.migrate_to_external_files():
                QMessageBox.information(
                    self,
                    self.tr("Migration Complete"),
                    self.tr("Project has been migrated to modular structure.\n\n"
                            "Objects and rooms are now stored in separate files.")
                )
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Migration Failed"),
                    self.tr("Failed to migrate project structure.\n"
                            "Check the console for error details.")
                )

    def _get_docs_url(self):
        """Return the GitHub USER_MANUAL URL for the current IDE language."""
        from core.language_manager import get_language_manager
        lang = get_language_manager().get_current_language()
        base = "https://github.com/Gabe1290/pythongm/blob/main/docs"
        # Map language codes to the USER_MANUAL file suffixes
        suffix_map = {
            "fr": "_FR", "de": "_DE", "es": "_ES", "it": "_IT",
            "ru": "_RU", "uk": "_UK", "sl": "_SL",
        }
        suffix = suffix_map.get(lang, "")
        return f"{base}/USER_MANUAL{suffix}.md"

    def show_documentation(self):
        """Open documentation window or website"""
        url = self._get_docs_url()
        QMessageBox.information(
            self,
            self.tr("Documentation"),
            self.tr("Quick Help:\n"
                    "• F1: Open this help\n"
                    "• Ctrl+N: New Project\n"
                    "• Ctrl+O: Open Project\n"
                    "• Ctrl+S: Save Project\n"
                    "• Double-click assets to edit them\n"
                    "• Right-click for more options\n\n"
                    "For full documentation, go to:\n"
                    "Help → Online Documentation\n"
                    "or visit:") + "\n" + url
        )

    def show_online_documentation(self):
        """Open the online documentation on GitHub in the default browser."""
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl(self._get_docs_url()))

    def show_tutorials(self):
        """Open tutorials in a floating window"""
        from widgets.tutorial_dialog import TutorialDialog
        from widgets.tutorial_panel import TutorialPanel

        # Find the Tutorials folder - try multiple locations
        tutorials_path = None

        # Try relative to source file (development mode)
        candidate = Path(__file__).parent.parent / "Tutorials"
        if candidate.exists():
            tutorials_path = candidate

        # Try PyInstaller bundle (single-file exe extracts data here)
        if not tutorials_path and hasattr(sys, '_MEIPASS'):
            candidate = Path(sys._MEIPASS) / "Tutorials"
            if candidate.exists():
                tutorials_path = candidate

        # Try relative to executable (packaged mode)
        if not tutorials_path:
            candidate = Path(sys.executable).parent / "Tutorials"
            if candidate.exists():
                tutorials_path = candidate

        # Try current working directory
        if not tutorials_path:
            candidate = Path.cwd() / "Tutorials"
            if candidate.exists():
                tutorials_path = candidate

        # Let the user pick a tutorial (modal selector).
        dialog = TutorialDialog(self, tutorials_path)
        if dialog.exec() != QDialog.Accepted:
            return
        selected_tutorial = dialog.get_selected_tutorial()
        if not (selected_tutorial and tutorials_path):
            return

        # Host the tutorial viewer in a QDockWidget, created once and
        # reused. Docked, it stays visible alongside the IDE on every
        # platform and is owned by the IDE main window (destroyed with
        # it). Detaching is NOT done via QDockWidget's float (unmovable
        # on Wayland — Qt's float-drag uses grabMouse() which the Wayland
        # plugin only allows for popups). Instead the panel's Float
        # button pops it into a DetachedEditorWindow — a plain QMainWindow
        # with native decorations that the compositor can move normally,
        # exactly like a detached editor.
        from PySide6.QtWidgets import QDockWidget

        if getattr(self, '_tutorial_dock', None) is None:
            self._tutorial_detached_window = None
            self._tutorial_panel = TutorialPanel(self)
            self._tutorial_panel.float_toggle_requested.connect(
                self._toggle_tutorial_float)
            dock = QDockWidget(self.tr("Tutorials"), self)
            dock.setObjectName("TutorialDock")
            dock.setWidget(self._tutorial_panel)
            dock.setFeatures(
                QDockWidget.DockWidgetClosable
                | QDockWidget.DockWidgetMovable
            )
            dock.setAllowedAreas(
                Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
            self._tutorial_dock = dock

        self._tutorial_panel.set_tutorials_path(tutorials_path)
        self._tutorial_panel.open_tutorial_by_data(selected_tutorial)
        if self._tutorial_detached_window is not None:
            # Currently floated — surface the floating window instead.
            self._tutorial_detached_window.show()
            self._tutorial_detached_window.raise_()
            self._tutorial_detached_window.activateWindow()
        else:
            self._tutorial_dock.show()
            self._tutorial_dock.raise_()

    def _toggle_tutorial_float(self):
        """Float the docked tutorial into an editor-style movable window,
        or re-dock it if it is already floating."""
        if getattr(self, '_tutorial_detached_window', None) is not None:
            # Already floating — closing the window re-docks it via
            # _on_tutorial_redock (mirrors the editor reattach path).
            self._tutorial_detached_window.close()
            return

        from editors.detached_editor_window import DetachedEditorWindow

        # Constructing the window reparents the panel out of the dock.
        window = DetachedEditorWindow(self._tutorial_panel, parent=self)
        window.reattach_requested.connect(self._on_tutorial_redock)
        self._tutorial_detached_window = window
        self._tutorial_dock.hide()  # dock is now empty
        self._tutorial_panel.set_floating_state(True)
        window.show()
        window.raise_()
        window.activateWindow()

    def _on_tutorial_redock(self, _panel):
        """The detached tutorial window is closing — put the panel back
        into the dock."""
        window = getattr(self, '_tutorial_detached_window', None)
        if window is None:
            return
        panel = window.take_editor() or self._tutorial_panel
        self._tutorial_detached_window = None
        self._tutorial_dock.setWidget(panel)
        self._tutorial_panel.set_floating_state(False)
        self._tutorial_dock.show()
        self._tutorial_dock.raise_()
        window.deleteLater()

    def about(self):
        """Show comprehensive About PyGameMaker dialog"""
        # Version is interpolated via {0} so bumping it never invalidates the
        # translated About block (the string stays version-independent).
        from utils import __version__ as _version
        about_text = self.tr(
            "<h2>PyGameMaker IDE</h2>"
            "<p><b>Version {0}</b></p>"
            "<p>A comprehensive visual game development environment<br>"
            "inspired by GameMaker Studio, built with Python.</p>"

            "<p><a href='https://github.com/Gabe1290/pythongm'>https://github.com/Gabe1290/pythongm</a></p>"

            "<h3>Features</h3>"
            "<ul>"
            "<li><b>Dual Programming Modes:</b> Visual (Blockly) and Traditional Events</li>"
            "<li><b>Asset Management:</b> Sprites, sounds, objects, and rooms</li>"
            "<li><b>Cross-Platform Export:</b> Windows, Linux, macOS, Android, iOS</li>"
            "<li><b>Flexible Configuration:</b> Customizable block/event visibility</li>"
            "<li><b>Real-time Testing:</b> Run games directly from the IDE</li>"
            "</ul>"

            "<h3>Technology Stack</h3>"
            "<p>"
            "• <b>IDE:</b> PySide6 (Qt 6)<br>"
            "• <b>Game Engine:</b> Pygame<br>"
            "• <b>Visual Programming:</b> Blockly<br>"
            "• <b>Export:</b> PyInstaller, Kivy<br>"
            "• <b>Language:</b> Python 3.11+"
            "</p>"

            "<h3>Project Information</h3>"
            "<p>"
            "PyGameMaker is an educational tool designed to make<br>"
            "game development accessible to beginners while providing<br>"
            "powerful features for experienced developers."
            "</p>"

            "<p><small>Built with ❤️ using Python and Qt</small></p>"
        ).format(_version)

        license_text = self.tr(
            "<h3>License</h3>"
            "<p>"
            "• <b>Source code:</b> MIT License<br>"
            "• <b>Documentation:</b> Creative Commons Attribution 4.0 (CC BY 4.0)<br>"
            "<small>Relicensed from GPLv3 to MIT + CC BY 4.0 to lower the barrier "
            "to reuse for educators, students, and downstream projects. "
            "See the <code>LICENSE</code> and <code>LICENSE-docs</code> files "
            "for full terms.</small>"
            "</p>"
            "<p>&copy; Gabriel Thullen, 2025-2026</p>"
        )

        QMessageBox.about(self, self.tr("About PyGameMaker"), about_text + license_text)

    def on_asset_selected(self, asset_data):
        self.properties_panel.set_asset(asset_data)

    def on_asset_imported(self, asset_name, asset_type, asset_data):
        """Handle asset import with correct signal signature"""
        logger.debug(f"📥 on_asset_imported called: {asset_type}/{asset_name}")
        self.update_status(self.tr("Imported {0}").format(asset_name))

        # Update current_project_data with the new asset
        if self.current_project_data is not None:
            if 'assets' not in self.current_project_data:
                self.current_project_data['assets'] = {}
            if asset_type not in self.current_project_data['assets']:
                self.current_project_data['assets'][asset_type] = {}
            self.current_project_data['assets'][asset_type][asset_name] = asset_data

        # Refresh sprite combo if it's a sprite import
        if asset_type == 'sprites':
            if hasattr(self, 'properties_panel') and hasattr(self.properties_panel, 'refresh_sprite_combo'):
                self.properties_panel.refresh_sprite_combo()
                logger.debug(f"Refreshed sprite combo after importing {asset_name}")

            # Also refresh open object editors so they see the new sprite
            logger.debug("🔄 Refreshing open object editors after sprite import...")
            self.refresh_open_object_editors()

        # Push new asset name into Blockly dropdowns for any open editor.
        self._refresh_blockly_asset_lists()

    def on_asset_double_clicked(self, asset_data):
        """Handle double-click on assets to open in appropriate editor"""
        asset_type = asset_data.get('asset_type', '')
        asset_name = asset_data.get('name', '')
        asset_info = asset_data.get('data', {})

        if asset_type == 'rooms':
            self.open_room_editor(asset_name, asset_info)
        elif asset_type == 'objects':
            self.open_object_editor(asset_name, asset_info)
        elif asset_type == 'sprites':
            self.open_sprite_editor(asset_name, asset_info)
        elif asset_type == 'playgrounds':
            self.open_playground_editor(asset_name, asset_info)
        elif asset_type == 'scripts':
            self.open_script_editor(asset_name, asset_info)
        else:
            logger.warning(f"No editor registered for asset type '{asset_type}' (asset: {asset_name})")

    def open_room_editor(self, room_name: str, room_data: dict):
        """Open a room in the room editor"""

        # Check if room is already open — focus tab or detached window.
        if room_name in self.open_editors:
            if self._focus_detached_editor(room_name):
                return
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.tabText(i) == room_name:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            # Create room editor
            room_editor = RoomEditor(str(self.current_project_path), self)

            # Load the room data
            room_editor.load_asset(room_name, room_data)

            # Connect editor signals (using UniqueConnection to prevent duplicates)
            room_editor.save_requested.connect(self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            room_editor.close_requested.connect(self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            room_editor.data_modified.connect(self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            room_editor.float_requested.connect(self.float_editor, Qt.ConnectionType.UniqueConnection)
            room_editor.reattach_requested.connect(self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            # Connect room editor activation signal
            room_editor.room_editor_activated.connect(self.on_room_editor_activated, Qt.ConnectionType.UniqueConnection)

            # Add to tabs
            tab_index = self.editor_tabs.addTab(room_editor, room_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            # Track the editor
            self.open_editors[room_name] = room_editor

            self.update_status(self.tr("Opened room: {0}").format(room_name))

            # Honor global window mode.
            if self.window_mode == 'floating':
                self.float_editor(room_editor)

        except Exception as e:
            logger.error(f"Error opening room editor: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open room editor: {0}").format(e))

    def open_playground_editor(self, playground_name: str, playground_data: dict):
        """Open a playground in the playground editor"""

        # Check if already open — focus tab or detached window
        if playground_name in self.open_editors:
            if self._focus_detached_editor(playground_name):
                return
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.tabText(i) == playground_name:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            from editors.playground_editor import PlaygroundEditor

            editor = PlaygroundEditor(str(self.current_project_path), self)
            editor.load_asset(playground_name, playground_data)

            # Connect signals
            editor.save_requested.connect(
                self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            editor.close_requested.connect(
                self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            editor.data_modified.connect(
                self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            editor.float_requested.connect(
                self.float_editor, Qt.ConnectionType.UniqueConnection)
            editor.reattach_requested.connect(
                self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            # Add to tabs
            tab_index = self.editor_tabs.addTab(editor, playground_name)
            self.editor_tabs.setCurrentIndex(tab_index)
            self.open_editors[playground_name] = editor

            self.update_status(self.tr("Opened playground: {0}").format(playground_name))

            # Honor global window mode.
            if self.window_mode == 'floating':
                self.float_editor(editor)

        except Exception as e:
            logger.error(f"Error opening playground editor: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                                 self.tr("Failed to open playground editor: {0}").format(e))

    def open_object_editor(self, object_name: str, object_data: dict):
        """Open an object in the object editor"""

        # Check if object is already open — focus its tab or its detached window
        if object_name in self.open_editors:
            if self._focus_detached_editor(object_name):
                return
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.tabText(i) == object_name:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            # Create object editor
            object_editor = ObjectEditor(str(self.current_project_path), self)

            # Load the object data
            object_editor.load_asset(object_name, object_data)

            # Connect editor signals (using UniqueConnection to prevent duplicates)
            object_editor.save_requested.connect(self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            object_editor.close_requested.connect(self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            object_editor.data_modified.connect(self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            object_editor.float_requested.connect(self.float_editor, Qt.ConnectionType.UniqueConnection)
            object_editor.reattach_requested.connect(self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            # Connect object editor activation signal
            object_editor.object_editor_activated.connect(self.on_object_editor_activated, Qt.ConnectionType.UniqueConnection)

            # Add to tabs - object editor occupies full center panel
            tab_index = self.editor_tabs.addTab(object_editor, object_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            # Track the editor
            self.open_editors[object_name] = object_editor

            # Collapse right panel when object editor is active
            # (Object editor has its own internal properties)
            self._collapse_right_panel()

            self.update_status(self.tr("Opened object: {0}").format(object_name))

            # Honor global window mode — float immediately if that's the
            # current default. Done last so the editor is fully wired up.
            if self.window_mode == 'floating':
                self.float_editor(object_editor)

        except Exception:
            import traceback
            tb = traceback.format_exc()
            traceback.print_exc()
            # Write crash log for GUI-only builds (no console).
            # Swallowed intentionally: we're already in the crash handler;
            # a failure to log the crash must not raise and replace the
            # original traceback shown in the QMessageBox below.
            try:
                from pathlib import Path
                crash_log = Path.home() / 'pygamemaker_crash.log'
                with open(crash_log, 'a', encoding='utf-8', errors='replace') as f:
                    f.write(f"\n{'='*60}\nObject editor crash:\n{tb}\n")
            except Exception:
                pass
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open object editor:\n\n{0}").format(tb))

    def open_sprite_editor(self, sprite_name: str, sprite_data: dict):
        """Open a sprite in the sprite editor"""

        # Check if sprite is already open — focus its tab or its detached window
        if sprite_name in self.open_editors:
            if self._focus_detached_editor(sprite_name):
                return
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.tabText(i) == sprite_name:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            sprite_editor = SpriteEditor(str(self.current_project_path), self)
            sprite_editor.load_asset(sprite_name, sprite_data)

            sprite_editor.save_requested.connect(self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            sprite_editor.close_requested.connect(self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            sprite_editor.data_modified.connect(self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            sprite_editor.float_requested.connect(self.float_editor, Qt.ConnectionType.UniqueConnection)
            sprite_editor.reattach_requested.connect(self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            tab_index = self.editor_tabs.addTab(sprite_editor, sprite_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            self.open_editors[sprite_name] = sprite_editor

            self.update_status(self.tr("Opened sprite: {0}").format(sprite_name))

            # Honor global window mode — float immediately if that's the
            # current default.
            if self.window_mode == 'floating':
                self.float_editor(sprite_editor)

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open sprite editor: {0}").format(e))

    def open_script_editor(self, script_name: str, script_data: dict):
        """Open a project-level script in the minimal script editor.

        Mirrors the open_sprite_editor / open_object_editor wiring:
        single tab per asset, same save/close/modified/float signal
        connections, same focus-existing-on-reopen behaviour. The script
        editor itself (editors/script_editor.py) is a thin QPlainTextEdit
        wrapper — see the module docstring for why it's intentionally
        minimal rather than a full code IDE.
        """
        from editors.script_editor import ScriptEditor

        if script_name in self.open_editors:
            if self._focus_detached_editor(script_name):
                return
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.tabText(i) == script_name:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            script_editor = ScriptEditor(str(self.current_project_path), self)
            script_editor.load_asset(script_name, script_data)

            script_editor.save_requested.connect(self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            script_editor.close_requested.connect(self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            script_editor.data_modified.connect(self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            script_editor.float_requested.connect(self.float_editor, Qt.ConnectionType.UniqueConnection)
            script_editor.reattach_requested.connect(self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            tab_index = self.editor_tabs.addTab(script_editor, script_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            self.open_editors[script_name] = script_editor

            self.update_status(self.tr("Opened script: {0}").format(script_name))

            if self.window_mode == 'floating':
                self.float_editor(script_editor)

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open script editor: {0}").format(e))

    def on_object_editor_activated(self, object_name: str, object_properties: dict):
        """Handle object editor activation"""
        logger.debug(f"🚨🚨🚨 IDE: on_object_editor_activated called for {object_name}")
        logger.debug(f"🚨 IDE: properties_panel exists? {hasattr(self, 'properties_panel')}")
        logger.debug(f"🚨 IDE: properties_panel type: {type(self.properties_panel).__name__ if hasattr(self, 'properties_panel') else 'N/A'}")

        # Find the object editor widget
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if (hasattr(widget, '__class__') and
                widget.__class__.__name__ == 'ObjectEditor' and
                hasattr(widget, 'asset_name') and
                widget.asset_name == object_name):

                # Set properties panel context
                self.properties_panel.set_object_editor_context(widget, object_name, object_properties)

                break

    def on_room_editor_activated(self, room_name: str, room_properties: dict):
        """Handle room editor activation"""
        # Find the room editor widget
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if (hasattr(widget, '__class__') and
                widget.__class__.__name__ == 'RoomEditor' and
                hasattr(widget, 'asset_name') and
                widget.asset_name == room_name):

                # Set properties panel context
                self.properties_panel.set_room_editor_context(widget, room_name, room_properties)

                break

    def on_editor_save_requested(self, asset_name: str, asset_data: dict):
        """Handle save request from editors"""

        if not self.project_manager:
            logger.error("ERROR: No project manager available")
            return

        try:
            # Determine asset type (PLURAL for category, SINGULAR for asset_type field)
            asset_category = None  # For file structure (plural)
            asset_type_field = None  # For data field (singular)

            if 'instances' in asset_data:  # Room has instances
                asset_category = 'rooms'
                asset_type_field = 'room'
            elif 'events' in asset_data or 'sprite' in asset_data:  # Object has sprite/events
                asset_category = 'objects'
                asset_type_field = 'object'
            elif 'asset_type' in asset_data:
                # Use existing asset_type, derive category
                asset_type_field = asset_data['asset_type']
                # Convert singular to plural for category
                if asset_type_field.endswith('s'):
                    asset_category = asset_type_field
                else:
                    asset_category = asset_type_field + 's'
            else:
                logger.warning("Could not determine asset type")
                return

            logger.debug(f"💾 Saving: category='{asset_category}', type_field='{asset_type_field}'")

            # Ensure required fields with CORRECT singular asset_type
            asset_data['name'] = asset_name
            asset_data['asset_type'] = asset_type_field  # SINGULAR form

            # Re-check the asset's file now that its editor has (re)written it.
            # This heals a stale "(not imported)" / file_missing badge left from
            # a load when the file was still absent — e.g. a sprite whose art
            # was being created. Falls back to marking imported when the asset
            # has no backing file (objects/rooms) or no asset manager is wired.
            if getattr(self, 'asset_manager', None):
                self.asset_manager.revalidate_asset_import_state(asset_data)
            else:
                asset_data['imported'] = True

            # Debug: Print what we're about to save
            if asset_category == 'rooms':
                logger.debug(f"💾 Room data keys: {list(asset_data.keys())}")
                logger.debug(f"💾 Background color: {asset_data.get('background_color', 'NOT SET')}")
                logger.debug(f"💾 Instances count: {len(asset_data.get('instances', []))}")

            # Use the project manager's update method with PLURAL category
            if self.project_manager.update_asset(asset_category, asset_name, asset_data):
                pass  # Success
            else:
                logger.error(f"Failed to update asset {asset_name}")
                return

            # Force immediate save
            if self.project_manager.save_project():
                # Update our local copy
                self.current_project_data = self.project_manager.get_current_project_data()

                # Update UI
                self.update_status(f"Saved: {asset_name}")
                self.update_window_title()

                # Refresh asset tree
                self.asset_tree.refresh_from_project(self.current_project_data)

                # Refresh properties panel sprite combo
                if hasattr(self.properties_panel, 'refresh_sprite_combo'):
                    self.properties_panel.refresh_sprite_combo()

                # Clear the tab asterisk to show save completed
                for i in range(self.editor_tabs.count()):
                    tab_text = self.editor_tabs.tabText(i)
                    if tab_text == asset_name + '*':
                        self.editor_tabs.setTabText(i, asset_name)
                        break

                # Broadcast so any *other* open editor (including floated
                # ones) refreshes its asset dropdowns. Cheap and idempotent.
                self._refresh_blockly_asset_lists()

                logger.info(f"✅ Save completed successfully for {asset_name}")

            else:
                logger.error("Project save FAILED")
                QMessageBox.warning(self, self.tr("Save Error"),
                                  self.tr("Failed to save project to disk"))
                return

        except Exception as e:
            logger.error(f"Error in save: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, self.tr("Save Error"),
                              self.tr("Failed to save {0}: {1}").format(asset_name, e))

    def on_editor_close_requested(self, asset_name: str):
        """Handle close request from editors"""
        self.close_editor_by_name(asset_name)

    def on_editor_data_modified(self, asset_name: str):
        """Handle data modification in editors"""
        # Update tab title to show modification
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.tabText(i) == asset_name:
                if not self.editor_tabs.tabText(i).endswith('*'):
                    self.editor_tabs.setTabText(i, asset_name + '*')
                break

        # NOTE: Do NOT refresh the properties panel here.
        # Calling show_asset_properties triggers widget signal changes which
        # feed back into the editor (mark_modified → data_modified → here),
        # creating an infinite auto-save loop.  The properties panel is already
        # populated when the editor tab is selected.

    def close_editor_by_name(self, asset_name: str):
        """Close editor by asset name (handles tabbed and detached editors)."""
        # Detached path: tear down the floating window and drop the editor.
        if asset_name in self.detached_editor_windows:
            self._destroy_detached_editor(asset_name)
            return
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.tabText(i).replace('*', '') == asset_name:
                self.close_editor_tab(i)
                break

    def _focus_detached_editor(self, asset_name: str) -> bool:
        """If the editor is currently floated, raise its window. Returns True
        if a detached window was found and focused."""
        window = self.detached_editor_windows.get(asset_name)
        if window is None:
            return False
        window.showNormal()
        window.raise_()
        window.activateWindow()
        return True

    def float_editor(self, editor):
        """Pop an editor out of the tab strip into its own floating window."""
        from editors.detached_editor_window import DetachedEditorWindow

        asset_name = getattr(editor, "asset_name", None)
        if not asset_name:
            logger.warning("float_editor called on editor with no asset_name")
            return
        if asset_name in self.detached_editor_windows:
            self._focus_detached_editor(asset_name)
            return

        # Find and remove the tab without going through close_editor_tab
        # (which would prompt about unsaved changes).
        tab_index = -1
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.widget(i) is editor:
                tab_index = i
                break
        if tab_index >= 0:
            self.editor_tabs.removeTab(tab_index)

        # Build the floating window. Keep the IDE as logical parent so the
        # window inherits stylesheet/icons but stays independently movable.
        window = DetachedEditorWindow(editor, parent=self)
        window.reattach_requested.connect(self._on_detached_reattach_requested)
        self.detached_editor_windows[asset_name] = window

        if hasattr(editor, "set_floating_state"):
            editor.set_floating_state(True)

        window.show()
        window.raise_()
        window.activateWindow()

        # If the tab strip is now empty, restore the welcome tab so the
        # center panel doesn't look broken.
        if self.editor_tabs.count() == 0:
            self.editor_tabs.addTab(self.welcome_tab, self.tr("Welcome"))

        self.update_status(self.tr("Floated: {0}").format(asset_name))

    def reattach_editor(self, editor):
        """Move a floated editor back into the tab strip."""
        asset_name = getattr(editor, "asset_name", None)
        if not asset_name:
            return
        window = self.detached_editor_windows.get(asset_name)
        if window is None:
            return
        # Closing the window triggers _on_detached_reattach_requested below.
        window.close()

    def _on_detached_reattach_requested(self, editor):
        """The detached window is closing — pull the editor back into a tab."""
        asset_name = getattr(editor, "asset_name", None)
        if not asset_name:
            return

        window = self.detached_editor_windows.pop(asset_name, None)
        if window is not None:
            taken = window.take_editor()
            if taken is not None:
                editor = taken
            window.deleteLater()

        # Drop the welcome tab if it's the only thing showing — we're about
        # to replace it with the real editor.
        if (self.editor_tabs.count() == 1
                and self.editor_tabs.widget(0) is self.welcome_tab):
            self.editor_tabs.removeTab(0)

        tab_index = self.editor_tabs.addTab(editor, asset_name)
        self.editor_tabs.setCurrentIndex(tab_index)

        if hasattr(editor, "set_floating_state"):
            editor.set_floating_state(False)

        self.update_status(self.tr("Reattached: {0}").format(asset_name))

    def toggle_window_mode(self):
        """Flip between global tabbed / floating mode and apply immediately."""
        new_mode = 'floating' if self.window_mode == 'tabbed' else 'tabbed'
        self.set_window_mode(new_mode)

    def set_window_mode(self, mode: str):
        """Set global window mode and apply it to all currently open editors.

        ``mode='tabbed'`` reattaches every floating editor (the recovery path
        when a window has been dragged off-screen). ``mode='floating'`` pops
        every tabbed editor out into its own window.
        """
        if mode not in ('tabbed', 'floating'):
            return
        self.window_mode = mode
        Config.set('window_mode', mode)
        self._update_window_mode_action_label()

        if mode == 'tabbed':
            # Reattach every detached editor. close() routes through
            # _on_detached_reattach_requested which puts the editor back.
            for asset_name in list(self.detached_editor_windows.keys()):
                window = self.detached_editor_windows.get(asset_name)
                if window is not None:
                    window.close()
            self.update_status(self.tr("Window mode: Tabbed"))
        else:
            # Float every editor currently in the tab strip.
            to_float = []
            for i in range(self.editor_tabs.count()):
                widget = self.editor_tabs.widget(i)
                if widget is None or widget is self.welcome_tab:
                    continue
                if hasattr(widget, 'asset_name') and widget.asset_name:
                    to_float.append(widget)
            for editor in to_float:
                self.float_editor(editor)
            self.update_status(self.tr("Window mode: Floating"))

    def _update_window_mode_action_label(self):
        """Sync the toolbar action's label and tooltip to the current mode."""
        if not hasattr(self, 'window_mode_action'):
            return
        if self.window_mode == 'floating':
            self.window_mode_action.setText(self.tr("⧉ Floating"))
            self.window_mode_action.setToolTip(self.tr(
                "Window mode: Floating. Click to switch all editors back into tabs "
                "(use this if a floating window has been dragged off-screen)."
            ))
        else:
            self.window_mode_action.setText(self.tr("⊞ Tabbed"))
            self.window_mode_action.setToolTip(self.tr(
                "Window mode: Tabbed. Click to pop every editor out into its own window."
            ))

    def _destroy_detached_editor(self, asset_name: str):
        """Fully close a floated editor (used by close_editor_by_name and
        project teardown — bypasses the reattach path)."""
        window = self.detached_editor_windows.pop(asset_name, None)
        editor = self.open_editors.pop(asset_name, None)
        if window is not None:
            window.reattach_on_close = False
            # take_editor() unparents the editor so deleteLater on the
            # window doesn't take the editor down with it before we get a
            # chance to disconnect signals.
            window.take_editor()
            window.close()
            window.deleteLater()
        if editor is not None:
            try:
                if hasattr(editor, 'save_requested'):
                    self.safe_disconnect_signal(editor.save_requested, self.on_editor_save_requested)
                if hasattr(editor, 'close_requested'):
                    self.safe_disconnect_signal(editor.close_requested, self.on_editor_close_requested)
                if hasattr(editor, 'data_modified'):
                    self.safe_disconnect_signal(editor.data_modified, self.on_editor_data_modified)
                if hasattr(editor, 'float_requested'):
                    self.safe_disconnect_signal(editor.float_requested, self.float_editor)
                if hasattr(editor, 'reattach_requested'):
                    self.safe_disconnect_signal(editor.reattach_requested, self.reattach_editor)
            except Exception:
                logger.debug(
                    "editor teardown: signal disconnect raised", exc_info=True
                )
            editor.deleteLater()

    def on_project_loaded(self, project_path, project_data):
        logger.debug(f"DEBUG on_project_loaded: START - path={project_path}, data_keys={list(project_data.keys()) if project_data else None}")

        # Close all open editor tabs from previous project to free memory
        while self.editor_tabs.count() > 0:
            widget = self.editor_tabs.widget(0)
            self.editor_tabs.removeTab(0)
            if widget and widget is not self.welcome_tab:
                widget.deleteLater()
        # Tear down any floated editors from the previous project too.
        for asset_name in list(self.detached_editor_windows.keys()):
            self._destroy_detached_editor(asset_name)
        self.open_editors.clear()
        self.editor_tabs.addTab(self.welcome_tab, self.tr("Welcome"))

        self.current_project_path = project_path
        self.current_project_data = project_data

        # Initialize game runner with project
        try:
            project_json = Path(project_path) / "project.json"
            if project_json.exists():
                self.game_runner = GameRunner(str(project_json))
                logger.debug(f"Game runner initialized for project: {project_json}")
            else:
                logger.warning(f"Warning: project.json not found at {project_json}")
                self.game_runner = None
        except Exception as e:
            logger.error(f"Error initializing game runner: {e}")
            import traceback
            traceback.print_exc()
            self.game_runner = None

        # Load assets into asset tree (order is preserved through OrderedDict)
        logger.debug("DEBUG on_project_loaded: calling asset_tree.set_project")
        self.asset_tree.set_project(str(project_path), project_data)
        logger.debug("DEBUG on_project_loaded: asset_tree.set_project done")

        # Set project base path for properties panel
        if hasattr(self.properties_panel, 'set_project_base_path'):
            self.properties_panel.set_project_base_path(str(project_path))
        # Reveal the asset-detail groups; they are hidden by default so
        # the right panel doesn't show three empty "No asset selected"
        # stubs on first launch (see EnhancedPropertiesPanel.set_project_loaded).
        if hasattr(self.properties_panel, 'set_project_loaded'):
            self.properties_panel.set_project_loaded(True)

        self.update_window_title()
        self.update_ui_state()
        self.update_status(self.tr("Project loaded: {0}").format(project_data['name']))
        logger.debug("DEBUG on_project_loaded: END")

    def on_project_saved(self):
        self.update_status(self.tr("Project saved"))

    def update_window_title(self):
        """Update the main window title to reflect the loaded project.

        Format follows the Windows/Linux convention "<Document> — <App>"
        so the project name shows in taskbar previews and Alt-Tab
        switchers (those clip the right-hand app name first). A trailing
        " *" marks the project as having unsaved changes, matching the
        per-editor dirty marker used by BaseEditor.
        """
        if self.current_project_data:
            project_name = self.current_project_data.get('name', 'Untitled')
            dirty = ' *' if self.project_manager.is_dirty() else ''
            title = f"{project_name}{dirty} — PyGameMaker IDE"
        else:
            title = "PyGameMaker IDE"
        self.setWindowTitle(title)

    def _on_dirty_changed(self, _is_dirty: bool):
        """Slot bound to project_manager.dirty_changed.

        Kept as a real bound method (rather than the obvious lambda)
        because Qt's UniqueConnection flag requires a pointer to a member
        function — passing a lambda fails with a runtime warning and the
        connection silently becomes non-unique (re-entries of
        setup_connections would then double-fire the slot).
        """
        self.update_window_title()

    def update_ui_state(self):
        has_project = self.current_project_path is not None

        # Import-as-new-project actions create a project from a source file, so
        # they must stay enabled even when no project is currently loaded. The
        # generic "Import" substring match below would otherwise grey them out.
        always_enabled_imports = set()
        for attr in ('import_roberta_action', 'import_gmk_action', 'thymio_import_roberta_action'):
            if hasattr(self, attr):
                always_enabled_imports.add(getattr(self, attr))

        for action in self.findChildren(QAction):
            if action in always_enabled_imports:
                action.setEnabled(True)
                continue
            if action.text() in [self.tr("Save Project"), self.tr("Save Project As..."), self.tr("Project Settings...")]:
                action.setEnabled(has_project)
            elif self.tr("Import") in action.text() or self.tr("Create") in action.text():
                action.setEnabled(has_project)
            elif action.text() in [self.tr("Test Game"), self.tr("Debug Game"), self.tr("Build Game"),
                                self.tr("Build and Run"), self.tr("Export Game...")]:
                action.setEnabled(has_project)

        # Enable/disable export actions based on project state
        if hasattr(self, 'export_html5_action'):
            self.export_html5_action.setEnabled(has_project)
        if hasattr(self, 'export_zip_action'):
            self.export_zip_action.setEnabled(has_project)
        if hasattr(self, 'export_kivy_action'):
            self.export_kivy_action.setEnabled(has_project)
        if hasattr(self, 'export_aseba_action'):
            self.export_aseba_action.setEnabled(has_project)
        if hasattr(self, 'export_project_action'):
            self.export_project_action.setEnabled(has_project)
        # Tools-menu items that only make sense with an open project
        if hasattr(self, 'validate_project_action'):
            self.validate_project_action.setEnabled(has_project)
        if hasattr(self, 'migrate_project_action'):
            self.migrate_project_action.setEnabled(has_project)
        # Thymio Add Event/Action target the active object editor, which
        # cannot exist without an open project.
        if hasattr(self, 'thymio_add_event_action'):
            self.thymio_add_event_action.setEnabled(has_project)
        if hasattr(self, 'thymio_add_action_action'):
            self.thymio_add_action_action.setEnabled(has_project)
        # File-menu / toolbar shared actions. Save and Save As require a
        # project; New and Open stay always-enabled (they're entry points).
        # These are stored as attributes specifically so update_ui_state
        # can drive both the menu copy and the toolbar copy through one
        # call (Qt shares QAction state across containers).
        if hasattr(self, 'save_project_action'):
            self.save_project_action.setEnabled(has_project)
        if hasattr(self, 'save_project_as_action'):
            self.save_project_as_action.setEnabled(has_project)
        # Toolbar quick-add for Thymio events — same constraint as the
        # submenu Add Event/Action (needs an object editor, which needs
        # a project as the minimum precondition).
        if hasattr(self, 'thymio_toolbar_action'):
            self.thymio_toolbar_action.setEnabled(has_project)
        # Enable/disable build actions based on project state
        if hasattr(self, 'test_game_action'):
            self.test_game_action.setEnabled(has_project)
        if hasattr(self, 'debug_game_action'):
            self.debug_game_action.setEnabled(has_project)
        if hasattr(self, 'export_game_action'):
            self.export_game_action.setEnabled(has_project)

        # Enable/disable Build menu based on project state
        if hasattr(self, 'build_menu'):
            self.build_menu.setEnabled(has_project)

        if has_project:
            self.project_label.setText(self.tr("Project: {0}").format(self.current_project_data['name']))
        else:
            self.project_label.setText(self.tr("No project loaded"))

    def update_status(self, message):
        self.status_label.setText(message)

        QTimer.singleShot(3000, lambda: self.status_label.setText(self.tr("Ready")))

    def refresh_open_object_editors(self):
        """Refresh sprite lists in all open object editors (tabbed + floated)."""
        # The IDE's live project data already holds a just-imported sprite,
        # which isn't written to project.json until save. Push it directly so
        # floated editors — whose parent chain may not reach the IDE, so they
        # can't find this data themselves — still pick up the new sprite.
        sprites = None
        if self.current_project_data:
            sprites = self.current_project_data.get('assets', {}).get('sprites')

        for widget in self._iter_open_editors():
            if hasattr(widget, 'load_project_assets'):
                widget.load_project_assets()
                logger.debug(f"🔄 Refreshed sprites in object editor: {getattr(widget, 'asset_name', '?')}")
            if sprites is not None and hasattr(widget, 'apply_available_sprites'):
                widget.apply_available_sprites(sprites)

    def refresh_object_sprites(self, object_name: str, old_sprite: str, new_sprite: str):
        """Refresh object sprites in room editors when they change.

        Walks both tabbed and detached editors so floated rooms see the
        new sprite assignment without a manual refresh.
        """
        logger.debug(f"Refreshing sprite for object {object_name}: {old_sprite} -> {new_sprite}")

        for widget in self._iter_open_editors():
            if hasattr(widget, 'room_canvas') and hasattr(widget, 'object_palette'):
                # Update room canvas with latest project data so it sees the new sprite assignment
                if hasattr(widget.room_canvas, 'set_project_info') and self.current_project_data:
                    project_path = self.current_project_path if hasattr(self, 'current_project_path') else None
                    widget.room_canvas.set_project_info(project_path, self.current_project_data)

                # Clear sprite cache for the object (set_project_info clears all, but be explicit)
                if hasattr(widget.room_canvas, 'sprite_cache') and object_name in widget.room_canvas.sprite_cache:
                    del widget.room_canvas.sprite_cache[object_name]

                # Refresh the object palette
                if hasattr(widget.object_palette, 'refresh_object_list'):
                    widget.object_palette.refresh_object_list()

                # Force canvas update
                widget.room_canvas.update()

        # DON'T refresh sprite combo here - it causes loops
        # The combo will be refreshed when the object editor updates

    def add_to_recent_projects(self, project_path):
        # Refuse to record bundled-samples paths. Clicking such a path
        # from Recent Projects would skip the load_project promotion in
        # some entry points (or surprise users on a future build that
        # removes the samples dir). Anything reachable via the IDE is
        # always under the user's working area.
        try:
            if self._is_samples_path(Path(project_path)):
                logger.debug(f"Skipping samples/ path in recent projects: {project_path}")
                return
        except Exception:
            pass

        recent = Config.get("recent_projects", [])

        if project_path in recent:
            recent.remove(project_path)

        recent.insert(0, project_path)
        recent = recent[:10]

        Config.set("recent_projects", recent)

        # Keep the Welcome tab's inline recent-projects list in sync so a
        # user who opens a project, closes it, then comes back to Welcome
        # sees the project they just had open at the top of the list.
        if hasattr(self, 'welcome_tab') and hasattr(self.welcome_tab, 'refresh_recent_projects'):
            self.welcome_tab.refresh_recent_projects()

    def _strip_samples_from_recent_projects(self) -> None:
        """One-time cleanup of pre-rc.12 in-place sample opens.

        Before commit f8a0eb7, clicking a sample ran the GMK importer in
        place under samples/, so the path got persisted into the user's
        recent_projects list. Those entries are dead: clicking them now
        promotes to a working copy (via load_project), so the original
        Recent Projects row would silently point to a different folder
        on next launch — confusing. Strip them once at startup.
        """
        recent = Config.get("recent_projects", [])
        if not recent:
            return
        cleaned = [p for p in recent if not self._is_samples_path(Path(p))]
        if len(cleaned) != len(recent):
            removed = [p for p in recent if p not in cleaned]
            logger.info(
                f"Removed {len(removed)} stale samples/ path(s) from "
                f"recent_projects: {removed}"
            )
            Config.set("recent_projects", cleaned)

    def restore_geometry(self):
        geometry = Config.get("window_geometry")
        state = Config.get("window_state")

        if geometry:
            self.restoreGeometry(geometry)

        if state:
            self.restoreState(state)

    def safe_disconnect_signal(self, signal, slot=None):
        """Safely disconnect a signal, avoiding warnings"""
        if not signal:
            return False
        try:
            if slot:
                # Disconnect specific slot
                try:
                    signal.disconnect(slot)
                    return True
                except (RuntimeError, TypeError):
                    # Connection doesn't exist, that's fine
                    return False
            else:
                # Disconnect all connections
                if hasattr(signal, 'isSignalConnected') and signal.isSignalConnected():
                    signal.disconnect()
                    return True
                else:
                    signal.disconnect()
                    return True
        except (RuntimeError, TypeError, AttributeError):
            return False

    def closeEvent(self, event):
        Config.set("window_geometry", self.saveGeometry())
        Config.set("window_state", self.saveState())

        if self.project_manager.is_dirty():
            reply = QMessageBox.question(
                self, self.tr("Unsaved Changes"),
                self.tr("You have unsaved changes. Do you want to save before closing?"),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                if not self.save_project():
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return

        # Close any detached editor windows without trying to reattach —
        # the IDE itself is going away, so there's nowhere to attach to.
        for window in list(self.detached_editor_windows.values()):
            window.reattach_on_close = False

        # Same for a floated tutorial window: don't try to re-dock into
        # an IDE that is tearing down.
        tutorial_win = getattr(self, '_tutorial_detached_window', None)
        if tutorial_win is not None:
            tutorial_win.reattach_on_close = False

        # Don't orphan a running Test Game: the subprocess outlives the IDE
        # otherwise (closeEvent never touched it). Past the cancel paths above,
        # so a cancelled close leaves the game running.
        self.stop_game()

        event.accept()

    def ensure_project_loaded(self, operation_name):
        """
        Universal method to ensure project is loaded before asset operations
        Returns True if project is loaded, False if user cancels
        """
        if self.current_project_path:
            return True  # Project already loaded

        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            self.tr("No Project Loaded"),
            self.tr("You need to create or open a project before {0}.\n\n"
                "Would you like to:\n"
                "• Create a new project, or\n"
                "• Open an existing project?").format(operation_name),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            # Show options for New vs Open
            project_reply = QMessageBox.question(
                self,
                self.tr("Create or Open Project"),
                self.tr("Choose project action:"),
                QMessageBox.Save | QMessageBox.Open | QMessageBox.Cancel
            )

            if project_reply == QMessageBox.Save:  # New Project
                self.new_project()
                return bool(self.current_project_path)
            elif project_reply == QMessageBox.Open:  # Open Project
                self.open_project()
                return bool(self.current_project_path)

        return False  # User cancelled

    def changeEvent(self, event):
        """Handle events, including language changes"""
        from PySide6.QtCore import QEvent

        if event.type() == QEvent.Type.LanguageChange:
            # Recreate menu bar with new translations
            logger.info("🔄 Language change event detected, recreating menus...")
            self.menuBar().clear()
            self.create_menu_bar()

            # Remove existing toolbar before creating new one
            existing_toolbar = self.findChild(QToolBar, "MainToolbar")
            if existing_toolbar:
                self.removeToolBar(existing_toolbar)
                existing_toolbar.deleteLater()
            self.create_toolbar()

            # Update UI state to enable/disable actions based on project state
            self.update_ui_state()
            logger.info("✅ Menus and toolbars recreated with new language")

        # Call parent class handler
        super().changeEvent(event)
