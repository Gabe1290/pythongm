#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                               QSplitter, QMenuBar, QStatusBar, QMessageBox, QDialog,
                               QFileDialog, QInputDialog, QProgressBar, QLabel, QStyle,
                               QTabWidget, QTextBrowser, QSizePolicy, QGroupBox, QFormLayout,
                               QSpinBox,QComboBox, QDialogButtonBox, QPushButton, QCheckBox,
                               QDoubleSpinBox, QLineEdit)

from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
from PySide6.QtGui import QAction, QKeySequence, QFont

from widgets.asset_tree.asset_tree_widget import AssetTreeWidget
# from widgets.properties_panel import PropertiesPanel
from widgets.enhanced_properties_panel import EnhancedPropertiesPanel
from core.project_manager import ProjectManager
from core.asset_manager import AssetManager
from core.ide_exporters import IDEExporters
from dialogs.project_dialogs import NewProjectDialog, ProjectSettingsDialog, ExportProjectDialog
from dialogs.import_dialogs import ImportAssetDialog
from dialogs.blockly_config_dialog import BlocklyConfigDialog
from utils.config import Config
from editors.room_editor import RoomEditor
from editors.object_editor import ObjectEditor
from runtime.game_runner import GameRunner
from export.exe.exe_exporter import ExeExporter

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
            print(f"ERROR in set_asset_manager: {e}")
            import traceback
            traceback.print_exc()

        # Load auto-save settings from config
        from utils.config import Config
        auto_save_enabled = Config.get('auto_save_enabled', True)
        auto_save_interval = Config.get('auto_save_interval', 30) * 1000  # Convert to milliseconds
        self.project_manager.set_auto_save(auto_save_enabled, auto_save_interval)

        self.current_project_path = None
        self.current_project_data = None

        # Initialize export helper module
        self.exporters = IDEExporters(self)

        # Add game runner
        self.game_runner = None  # Will be initialized when project is loaded

        self.setup_ui()
        self.setup_connections()
        self.restore_geometry()

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
            print(f"ERROR in create_menu_bar: {e}")
            import traceback
            traceback.print_exc()
            raise

        try:
            self.create_toolbar()
        except Exception as e:
            print(f"ERROR in create_toolbar: {e}")
            import traceback
            traceback.print_exc()
            raise

        try:
            self.create_main_widget()
        except Exception as e:
            print(f"ERROR in create_main_widget: {e}")
            import traceback
            traceback.print_exc()
            raise

        try:
            self.create_status_bar()
        except Exception as e:
            print(f"ERROR in create_status_bar: {e}")
            import traceback
            traceback.print_exc()
            raise

        # Connect the rename signal
        self.asset_tree.asset_renamed.connect(self.on_asset_renamed)

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu(self.tr("&File"))
        file_menu.addAction(self.create_action(self.tr("&New Project..."), "Ctrl+N", self.new_project))
        file_menu.addAction(self.create_action(self.tr("&Open Project..."), "Ctrl+O", self.open_project))
        file_menu.addSeparator()
        file_menu.addAction(self.create_action(self.tr("&Save Project"), "Ctrl+S", self.save_project))
        file_menu.addAction(self.create_action(self.tr("Save Project &As..."), "Ctrl+Shift+S", self.save_project_as))
        file_menu.addSeparator()

        recent_menu = file_menu.addMenu(self.tr("Recent Projects"))
        self.update_recent_projects_menu(recent_menu)

        file_menu.addSeparator()
        # Export menu items
        # Store references to export actions
        self.export_html5_action = self.create_action(self.tr("Export as HTML5..."), None, self.export_html5)
        self.export_zip_action = self.create_action(self.tr("Export as &Zip..."), None, self.export_project_zip)
        self.export_kivy_action = self.create_action(self.tr("Export to Kivy..."), None, self.export_kivy)
        self.export_project_action = self.create_action(self.tr("Export Project..."), "Ctrl+E", self.export_project)

        file_menu.addAction(self.export_html5_action)
        file_menu.addAction(self.export_zip_action)
        file_menu.addAction(self.export_kivy_action)
        file_menu.addAction(self.export_project_action)

        file_menu.addAction(self.create_action(self.tr("Open &Zip Project..."), None, self.open_project_zip))
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
        edit_menu.addSeparator()
        edit_menu.addAction(self.create_action(self.tr("&Find..."), "Ctrl+F", self.find))
        edit_menu.addAction(self.create_action(self.tr("Find and &Replace..."), "Ctrl+H", self.find_replace))

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

        build_menu = menubar.addMenu(self.tr("&Build"))
        # Store references to build actions
        self.test_game_action = self.create_action(self.tr("&Test Game"), "F5", self.test_game)
        self.debug_game_action = self.create_action(self.tr("&Debug Game"), "F6", self.debug_game)
        self.build_game_action = self.create_action(self.tr("&Build Game..."), "F7", self.build_game)
        self.build_and_run_action = self.create_action(self.tr("Build and &Run"), "F8", self.build_and_run)
        self.export_game_action = self.create_action(self.tr("&Export Game..."), None, self.export_game)

        build_menu.addAction(self.test_game_action)
        build_menu.addAction(self.debug_game_action)
        build_menu.addSeparator()
        build_menu.addAction(self.build_game_action)
        build_menu.addAction(self.build_and_run_action)
        build_menu.addSeparator()
        build_menu.addAction(self.export_game_action)

        tools_menu = menubar.addMenu(self.tr("&Tools"))
        tools_menu.addAction(self.create_action(self.tr("&Preferences..."), None, self.preferences))
        tools_menu.addAction(self.create_action(self.tr("&Asset Manager..."), None, self.show_asset_manager))
        tools_menu.addAction(self.create_action(self.tr("Configure &Blockly Blocks..."), None, self.configure_blockly))
        tools_menu.addSeparator()
        tools_menu.addAction(self.create_action(self.tr("&Validate Project"), None, self.validate_project))
        tools_menu.addAction(self.create_action(self.tr("&Clean Project"), None, self.clean_project))
        tools_menu.addSeparator()

        # Language submenu
        language_menu = tools_menu.addMenu(self.tr("🌐 &Language"))
        self.create_language_menu(language_menu)

        help_menu = menubar.addMenu(self.tr("&Help"))
        help_menu.addAction(self.create_action(self.tr("&Documentation"), "F1", self.show_documentation))
        help_menu.addAction(self.create_action(self.tr("&Tutorials"), None, self.show_tutorials))
        help_menu.addSeparator()
        help_menu.addAction(self.create_action(self.tr("&About PyGameMaker"), None, self.about))

    def create_language_menu(self, menu):
        """Create language selection submenu"""
        from core.language_manager import get_language_manager

        language_manager = get_language_manager()
        current_lang = language_manager.get_current_language()

        # Create action group for radio buttons
        from PySide6.QtGui import QActionGroup
        self.language_action_group = QActionGroup(self)
        self.language_action_group.setExclusive(True)

        # Add language options
        for code, name, flag in language_manager.get_available_languages():
            action = menu.addAction(f"{flag} {name}")
            action.setCheckable(True)
            action.setData(code)  # Store language code

            # Show if translation is available
            if not language_manager.is_translation_available(code) and code != 'en':
                action.setText(f"{flag} {name} (translation not available)")

            # Block signals while setting the checked state to avoid triggering change_language during initialization
            action.blockSignals(True)
            action.setChecked(code == current_lang)
            action.blockSignals(False)

            # Connect the triggered signal AFTER setting up the action
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
            # Ask if user wants to restart now
            if language_code == 'en':
                # For English, use hardcoded strings since there's no translator
                title = "Language Changed"
                message = (
                    f"Language changed to {lang_name}.\n\n"
                    "The IDE needs to restart for the language change to take effect.\n\n"
                    "Do you want to restart now?")
            else:
                # For other languages, use QCoreApplication.translate() to get fresh translations
                # This ensures the dialog appears in the NEW language, not the old one
                title = QCoreApplication.translate("PyGameMakerIDE", "Language Changed")
                message = QCoreApplication.translate("PyGameMakerIDE",
                    "Language changed to {0}.\n\n"
                    "The IDE needs to restart for the language change to take effect.\n\n"
                    "Do you want to restart now?").format(lang_name)

            reply = QMessageBox.question(
                self,
                title,
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                # Save config to ensure language setting is persisted
                from utils.config import Config
                Config.save()
                print(f"💾 Config saved before restart")

                # Restart the application
                QCoreApplication.quit()
                import subprocess
                import sys
                subprocess.Popen([sys.executable] + sys.argv)
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
        """Toggle auto-save on/off"""
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

    def create_toolbar(self):
        toolbar = self.addToolBar(self.tr("Main"))
        toolbar.setObjectName("MainToolbar")
        toolbar.setMovable(False)

        # Set explicit icon size
        toolbar.setIconSize(QSize(16, 16))

        # Force toolbar to show icons
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        # Create actions first, then add to toolbar
        actions = [
            self.create_action(self.tr("New"), None, self.new_project, "SP_FileIcon"),
            self.create_action(self.tr("Open"), None, self.open_project, "SP_DialogOpenButton"),
            self.create_action(self.tr("Save"), None, self.save_project, "SP_DialogSaveButton"),
        ]

        for action in actions:
            toolbar.addAction(action)

        toolbar.addSeparator()

        toolbar.addAction(self.create_action(self.tr("Test"), None, self.test_game, "SP_MediaPlay"))
        toolbar.addAction(self.create_action(self.tr("Debug"), None, self.debug_game, "SP_ComputerIcon"))
        toolbar.addAction(self.create_action(self.tr("Build"), None, self.build_game, "SP_DialogApplyButton"))
        toolbar.addSeparator()

        toolbar.addAction(self.create_action(self.tr("Import Sprite"), None, self.import_sprite, "SP_FileIcon"))
        toolbar.addAction(self.create_action(self.tr("Import Sound"), None, self.import_sound, "SP_MediaVolume"))

        # Force update
        toolbar.update()

    def create_main_widget(self):
        """Modified to include editor tabs in center"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Asset tree (unchanged)
        try:
            print("DEBUG: About to create AssetTreeWidget...")
            self.asset_tree = AssetTreeWidget(self)
            print("DEBUG: AssetTreeWidget created successfully!")
        except Exception as e:
            print(f"ERROR creating AssetTreeWidget: {e}")
            import traceback
            traceback.print_exc()
        self.asset_tree.setMinimumWidth(200)
        self.asset_tree.setMaximumWidth(300)

        # Center panel - NEW: Tabbed editors
        center_panel = self.create_center_panel_with_editors()

        # Right panel - Properties (unchanged for now)
        self.properties_panel = EnhancedPropertiesPanel()
        self.properties_panel.setMinimumWidth(250)
        self.properties_panel.setMaximumWidth(350)

        # Add panels to main splitter
        main_splitter.addWidget(self.asset_tree)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(self.properties_panel)

        # Set proportions: asset tree, editors, properties
        main_splitter.setSizes([250, 800, 300])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        main_splitter.setCollapsible(2, False)

        layout.addWidget(main_splitter)

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
        self.modified_editors = set()

        # Welcome tab (default)
        self.welcome_tab = WelcomeTab(self)
        self.editor_tabs.addTab(self.welcome_tab, "Welcome")

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

                    # Disconnect editor-specific signals
                    if hasattr(editor_widget, 'room_editor_activated'):
                        self.safe_disconnect_signal(editor_widget.room_editor_activated, self.on_room_editor_activated)
                    if hasattr(editor_widget, 'object_editor_activated'):
                        self.safe_disconnect_signal(editor_widget.object_editor_activated, self.on_object_editor_activated)

                # Remove from open editors dict if it exists
                if tab_text in self.open_editors:
                    del self.open_editors[tab_text]

                # Remove tab
                self.editor_tabs.removeTab(index)

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
                # Room editor is active - show properties panel with room properties
                if hasattr(self, 'properties_panel'):
                    self.properties_panel.show()

                try:
                    room_name = widget.asset_name
                    room_data = widget.get_data() if hasattr(widget, 'get_data') else widget.current_room_properties

                    self.properties_panel.set_room_editor_context(widget, room_name, room_data)

                except Exception as e:
                    print(f"Error setting room editor context: {e}")

            elif editor_class == 'ObjectEditor':
                # Object editor is active - HIDE properties panel (object editor has its own)
                if hasattr(self, 'properties_panel'):
                    self.properties_panel.hide()

                # Clear the context since we're not using the external properties panel
                self.clear_properties_contexts()

            else:
                # Other editor type - show properties panel and clear contexts
                if hasattr(self, 'properties_panel'):
                    self.properties_panel.show()
                self.clear_properties_contexts()

        else:
            # Welcome tab or other non-editor - show properties panel
            if hasattr(self, 'properties_panel'):
                self.properties_panel.show()
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

        self.project_manager.project_loaded.connect(self.on_project_loaded, Qt.ConnectionType.UniqueConnection)
        self.project_manager.project_saved.connect(self.on_project_saved, Qt.ConnectionType.UniqueConnection)
        self.project_manager.status_changed.connect(self.update_status, Qt.ConnectionType.UniqueConnection)

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
                    print(f"⚠️ Warning: Invalid icon name '{icon_name}' - no such StandardPixmap")
            except AttributeError as e:
                print(f"⚠️ Warning: Could not access QStyle.StandardPixmap.{icon_name}: {e}")
            except Exception as e:
                print(f"⚠️ Warning: Could not load icon '{icon_name}': {e}")

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

    def new_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec():
            project_info = dialog.get_project_info()
            print(f"DEBUG new_project: project_info = {project_info}")

            if self.project_manager.create_project(
                project_info["name"],
                project_info["path"],
                project_info["template"]
            ):
                # Update IDE state with newly created project
                project_path = self.project_manager.current_project_path
                project_data = self.project_manager.current_project_data
                print(f"DEBUG new_project: project_path = {project_path}")
                print(f"DEBUG new_project: project_data keys = {list(project_data.keys()) if project_data else None}")

                # Call on_project_loaded to properly initialize the IDE
                self.on_project_loaded(project_path, project_data)
                print("DEBUG new_project: on_project_loaded called")

                # Add to recent projects
                self.add_to_recent_projects(str(project_path))

                self.update_status(self.tr("Project created successfully"))
            else:
                print("DEBUG new_project: create_project returned False")
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

    def load_project(self, project_path):
        print(f"DEBUG load_project: Attempting to load from {project_path}")
        if self.project_manager.load_project(project_path):
            print(f"DEBUG load_project: project_manager.load_project succeeded")
            self.asset_tree.project_manager = self.project_manager

            Config.set("last_project_directory", str(project_path.parent))
            self.add_to_recent_projects(str(project_path))
        else:
            print(f"DEBUG load_project: project_manager.load_project FAILED")
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
            self.project_manager.mark_dirty()

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
                print("🔥 User cancelled")
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
                    print("No files selected")
            else:
                print("Import cancelled")

        except Exception as e:
            print(f"Error in import_asset: {e}")

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

            except Exception as e:
                print(f"❌ Error handling asset rename in main window: {e}")

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
            print(f"❌ Error finding renamed asset: {e}")
            return None


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
                    'enable_views': False,
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
            else:
                # Generic asset data
                asset_data = {
                    'name': asset_name,
                    'asset_type': asset_type[:-1],
                    'imported': True
                }

            # Add to project data
            if not self.current_project_data:
                print("No project data available")
                return

            assets = self.current_project_data.setdefault('assets', {})
            asset_category = assets.setdefault(asset_type, {})
            asset_category[asset_name] = asset_data

            # Mark project as dirty and save
            self.project_manager.mark_dirty()

            # Update the asset tree
            self.asset_tree.add_asset(asset_type, asset_name, asset_data)

            # Save the project immediately to persist the new asset
            if self.project_manager.save_project():
                self.update_status(self.tr("Created {0}").format(asset_name))
            else:
                print(f"Failed to save project after creating {asset_name}")

        except Exception as e:
            print(f"Error creating {asset_type[:-1]}: {e}")
            QMessageBox.warning(self, self.tr("Error"),
                            self.tr("Failed to create {0}: {1}").format(asset_type[:-1], e))

    def test_game(self):
        """Test the current game"""
        # Check if project is open
        if not self.current_project_path:
            QMessageBox.warning(
                self,
                self.tr("No Project"),
                self.tr("Please open or create a project first before testing a game.")
            )
            return
        
        # Save project before testing
        if self.project_manager.is_dirty():
            self.save_project()

        try:
            self.update_status(self.tr("Running game..."))

            # Create GameRunner with path to project.json
            from runtime.game_runner import GameRunner
            project_json = self.current_project_path / "project.json"

            if not project_json.exists():
                QMessageBox.warning(
                    self,
                    self.tr("Project Error"),
                    self.tr("project.json not found in project directory")
                )
                return

            # Create runner and run game
            runner = GameRunner(str(project_json))
            runner.run()

            self.update_status(self.tr("Game closed"))

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Game Test Error"),
                self.tr("Failed to run game:\n\n{0}\n\nCheck console for details.").format(str(e))
            )
            print(f"❌ Game test error: {e}")
            import traceback
            traceback.print_exc()
            self.update_status(self.tr("Game test failed"))

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
        if self.game_runner.test_game(str(self.current_project_path)):
            self.update_status(self.tr("Game started in debug mode - Check console for debug output"))
        else:
            self.update_status(self.tr("Failed to start game"))
            QMessageBox.warning(
                self,
                self.tr("Game Error"),
                self.tr("Failed to start the game. Check console for details.")
            )

    def build_game(self):
        """Build standalone game executable"""
        # Save project first
        if self.project_manager.is_dirty():
            reply = QMessageBox.question(
                self,
                self.tr("Unsaved Changes"),
                self.tr("You have unsaved changes. Save before building?"),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                if not self.save_project():
                    return

        # Ask for build output directory
        output_dir = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Build Output Directory"),
            str(Path.home() / "Desktop")
        )

        if not output_dir:
            return  # User cancelled

        self.update_status(self.tr("Building game..."))

        # Show info about build process
        QMessageBox.information(
            self,
            self.tr("Build Game"),
            self.tr("Standalone executable building is not yet implemented.\n\n"
                    "Current workaround:\n"
                    "• Use 'Export as HTML5' to create a web version\n"
                    "• Use 'Test Game' to run from source\n\n"
                    "Future build targets:\n"
                    "• Windows .exe\n"
                    "• Linux binary\n"
                    "• macOS .app\n"
                    "• Android .apk\n\n"
                    "Would you like to export as HTML5 instead?")
        )

        self.update_status(self.tr("Build cancelled - use HTML5 export instead"))

    def build_and_run(self):
        """Build game and immediately run the built executable"""
        reply = QMessageBox.question(
            self,
            self.tr("Build and Run"),
            self.tr("This will build a standalone executable and run it.\n\n"
                    "Building may take several minutes.\n\n"
                    "Continue?"),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Save project first
        if self.project_manager.is_dirty():
            if not self.save_project():
                return

        self.update_status(self.tr("Building and running game..."))

        # For now, just run in test mode
        QMessageBox.information(
            self,
            self.tr("Build and Run"),
            self.tr("Standalone build is not yet implemented.\n\n"
                    "Running game in test mode instead...")
        )

        # Run in test mode
        self.test_game()

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

        windows_radio = QRadioButton(self.tr("Windows Executable (.exe) - ✅ Available"))
        windows_radio.setEnabled(True)  # CHANGED: Enable Windows export
        button_group.addButton(windows_radio, 2)
        layout.addWidget(windows_radio)

        linux_radio = QRadioButton(self.tr("Linux Binary - 🚧 Coming Soon"))
        linux_radio.setEnabled(False)
        button_group.addButton(linux_radio, 3)
        layout.addWidget(linux_radio)

        mac_radio = QRadioButton(self.tr("macOS Application (.app) - 🚧 Coming Soon"))
        mac_radio.setEnabled(False)
        button_group.addButton(mac_radio, 4)
        layout.addWidget(mac_radio)

        android_radio = QRadioButton(self.tr("Android Package (.apk) - 🚧 Coming Soon"))
        android_radio.setEnabled(False)
        button_group.addButton(android_radio, 5)
        layout.addWidget(android_radio)

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
            elif selected_id == 2:  # Windows EXE - NEW
                self.export_windows_exe()
            else:
                QMessageBox.information(
                    self,
                    self.tr("Coming Soon"),
                    self.tr("This export format is not yet available.\n\n"
                            "Please use HTML5 or Windows EXE export for now.")
                )

    def export_windows_exe(self):
        """Handle Windows EXE export with progress dialog"""
        # Check if project is open
        if not self.current_project_path:
            QMessageBox.warning(
                self,
                self.tr("No Project"),
                self.tr("Please open or create a project first.")
            )
            return

        # Ask user for output location
        from PySide6.QtWidgets import QFileDialog

        default_name = self.current_project_data.get('name', 'Game').replace(' ', '_')
        output_dir = QFileDialog.getExistingDirectory(
            self,
            self.tr("Choose Export Location"),
            str(Path.home() / "Desktop" / f"{default_name}_exe"),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if not output_dir:
            return  # User cancelled

        # Create export settings
        export_settings = {
            'output_path': output_dir,
            'include_assets': True,
            'optimize': True,
            'include_debug': False
        }

        # Create progress dialog
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QProgressBar

        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle(self.tr("Exporting Game"))
        progress_dialog.setModal(True)
        progress_dialog.resize(500, 150)

        layout = QVBoxLayout(progress_dialog)

        status_label = QLabel(self.tr("Preparing export..."))
        layout.addWidget(status_label)

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        layout.addWidget(progress_bar)

        # Import and create exporter
        from export.exe.exe_exporter import ExeExporter
        exporter = ExeExporter()

        # Connect signals
        def update_progress(percent, message):
            progress_bar.setValue(percent)
            status_label.setText(message)

        def export_finished(success, message):
            progress_dialog.accept()
            if success:
                result = QMessageBox.information(
                    self,
                    self.tr("Export Complete"),
                    message + "\n\n" + self.tr("Would you like to open the output folder?"),
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
                QMessageBox.critical(
                    self,
                    self.tr("Export Failed"),
                    message
                )

        exporter.progress_update.connect(update_progress)
        exporter.export_complete.connect(export_finished)

        # Start export in background thread
        from PySide6.QtCore import QThread

        class ExportThread(QThread):
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
                    self.settings
                )

        export_thread = ExportThread(
            exporter,
            str(self.current_project_path),
            output_dir,
            export_settings
        )

        export_thread.start()
        progress_dialog.exec()
        export_thread.wait()

    def undo(self):
        """Handle undo - delegate to active editor if applicable"""
        current_widget = self.editor_tabs.currentWidget()

        # Check if it's a room editor
        if hasattr(current_widget, '__class__') and current_widget.__class__.__name__ == 'RoomEditor':
            if hasattr(current_widget, 'undo'):
                current_widget.undo()
                return

        # Check if it's an object editor or other editor with undo functionality
        if hasattr(current_widget, 'undo'):
            try:
                current_widget.undo()
                return
            except:
                pass

        # Default: project-level undo (if implemented)
        print("Undo (no editor-specific undo available)")

    def redo(self):
        """Handle redo - delegate to active editor if applicable"""
        current_widget = self.editor_tabs.currentWidget()

        # Check if it's a room editor
        if hasattr(current_widget, '__class__') and current_widget.__class__.__name__ == 'RoomEditor':
            if hasattr(current_widget, 'redo'):
                current_widget.redo()
                return

        # Check if it's an object editor or other editor with redo functionality
        if hasattr(current_widget, 'redo'):
            try:
                current_widget.redo()
                return
            except:
                pass

        # Default: project-level redo (if implemented)
        print("Redo (no editor-specific redo available)")

    def cut(self):
        """Handle cut - delegate to active editor if applicable"""
        current_widget = self.editor_tabs.currentWidget()

        # Check if it's a room editor
        if hasattr(current_widget, '__class__') and current_widget.__class__.__name__ == 'RoomEditor':
            if hasattr(current_widget, 'cut_instance'):
                current_widget.cut_instance()
                return

        # Check if it's an object editor or other editor with cut functionality
        if hasattr(current_widget, 'cut'):
            try:
                current_widget.cut()
                return
            except:
                pass

        # Default: try to cut from focused widget
        focused_widget = self.focusWidget()
        if focused_widget and hasattr(focused_widget, 'cut'):
            try:
                focused_widget.cut()
            except:
                pass

    def copy(self):
        """Handle copy - delegate to active editor if applicable"""
        current_widget = self.editor_tabs.currentWidget()

        # Check if it's a room editor
        if hasattr(current_widget, '__class__') and current_widget.__class__.__name__ == 'RoomEditor':
            if hasattr(current_widget, 'copy_instance'):
                current_widget.copy_instance()
                return

        # Check if it's an object editor or other editor with copy functionality
        if hasattr(current_widget, 'copy'):
            try:
                current_widget.copy()
                return
            except:
                pass

        # Default: try to copy from focused widget
        focused_widget = self.focusWidget()
        if focused_widget and hasattr(focused_widget, 'copy'):
            try:
                focused_widget.copy()
            except:
                pass

    def paste(self):
        """Handle paste - delegate to active editor if applicable"""
        current_widget = self.editor_tabs.currentWidget()

        # Check if it's a room editor
        if hasattr(current_widget, '__class__') and current_widget.__class__.__name__ == 'RoomEditor':
            if hasattr(current_widget, 'paste_instance'):
                current_widget.paste_instance()
                return

        # Check if it's an object editor or other editor with paste functionality
        if hasattr(current_widget, 'paste'):
            try:
                current_widget.paste()
                return
            except:
                pass

        # Default: try to paste to focused widget
        focused_widget = self.focusWidget()
        if focused_widget and hasattr(focused_widget, 'paste'):
            try:
                focused_widget.paste()
            except:
                pass

    def duplicate(self):
        """Handle duplicate - delegate to active editor if applicable"""
        current_widget = self.editor_tabs.currentWidget()

        # Check if it's a room editor
        if hasattr(current_widget, '__class__') and current_widget.__class__.__name__ == 'RoomEditor':
            if hasattr(current_widget, 'duplicate_instance'):
                current_widget.duplicate_instance()
                return

        # For other editors, could implement duplicate functionality here
        print("Duplicate action (no room editor active)")

    def find(self):
        """Find text in current editor - to be implemented"""
        QMessageBox.information(
            self,
            self.tr("Not Implemented"),
            self.tr("Find functionality is not yet implemented.")
        )

    def find_replace(self):
        """Find and replace text in current editor - to be implemented"""
        QMessageBox.information(
            self,
            self.tr("Not Implemented"),
            self.tr("Find and Replace functionality is not yet implemented.")
        )

    def preferences(self):
            """Open preferences/settings dialog"""
            from dialogs.preferences_dialog import PreferencesDialog
            dialog = PreferencesDialog(self)
            dialog.exec()

    def show_asset_manager(self):
        """Show asset manager window for managing project assets"""
        if not self.current_project_path:
            QMessageBox.information(
                self,
                self.tr("No Project"),
                self.tr("Please open a project first to manage assets.")
            )
            return

        QMessageBox.information(
            self,
            self.tr("Asset Manager"),
            self.tr("Asset Manager is not yet implemented.\n\n"
                    "Current workaround:\n"
                    "Use the Asset Tree panel on the left to manage your assets.\n\n"
                    "Future features:\n"
                    "• Bulk asset operations\n"
                    "• Asset search and filter\n"
                    "• Asset usage tracking\n"
                    "• Unused asset cleanup")
        )
    
    def configure_blockly(self):
        """Open Blockly configuration dialog to customize available blocks"""
        from config.blockly_config import load_config, save_config
        
        # Load current configuration
        current_config = load_config()
        
        # Show dialog
        dialog = BlocklyConfigDialog(self, current_config)
        if dialog.exec() == QDialog.Accepted:
            # Save the new configuration
            new_config = dialog.config
            save_config(new_config)
            
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
            
            print(f"✅ Blockly configuration updated: {new_config.preset_name} preset")
            print(f"   Enabled blocks: {len(new_config.enabled_blocks)}")
            print(f"   Enabled categories: {', '.join(new_config.enabled_categories)}")
    
    def refresh_event_panels_config(self):
        """Refresh configuration in all open GM80 events panels"""
        # Find all open object editors with GM80 events panels
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            # Check if it's an object editor
            if hasattr(widget, 'gm80_events_panel'):
                # Reload configuration in the events panel
                widget.gm80_events_panel.reload_config()
                print(f"   ♻️ Reloaded event panel config for: {self.editor_tabs.tabText(i)}")


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

    def clean_project(self):
        """Clean temporary files and unused assets from project"""
        if not self.current_project_path:
            QMessageBox.information(
                self,
                self.tr("No Project"),
                self.tr("Please open a project first to clean.")
            )
            return

        reply = QMessageBox.question(
            self,
            self.tr("Clean Project"),
            self.tr("Project cleanup is not yet implemented.\n\n"
                    "Future features:\n"
                    "• Remove temporary files\n"
                    "• Delete unused assets\n"
                    "• Clean build artifacts\n"
                    "• Optimize project size\n\n"
                    "Would you like to learn more?"),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self,
                self.tr("Coming Soon"),
                self.tr("This feature will be available in a future update.\n\n"
                        "For now, you can manually delete temporary files from:\n"
                        "• .cache/ directory\n"
                        "• __pycache__/ directories\n"
                        "• *.pyc files")
            )

    def show_documentation(self):
        """Open documentation window or website"""
        QMessageBox.information(
            self,
            self.tr("Documentation"),
            self.tr("Documentation is not yet available.\n\n"
                    "Quick Help:\n"
                    "• F1: Open this help\n"
                    "• Ctrl+N: New Project\n"
                    "• Ctrl+O: Open Project\n"
                    "• Ctrl+S: Save Project\n"
                    "• Double-click assets to edit them\n"
                    "• Right-click for more options\n\n"
                    "Online documentation coming soon!")
        )

    def show_tutorials(self):
        """Open tutorials window or website"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget

        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Tutorials"))
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(self.tr("<h3>PyGameMaker Tutorials</h3>")))
        layout.addWidget(QLabel(self.tr("Coming soon! Tutorials will include:")))

        tutorial_list = QListWidget()
        tutorial_list.addItems([
            "📚 Getting Started with PyGameMaker",
            "🎮 Creating Your First Game",
            "🖼️ Working with Sprites and Assets",
            "🏗️ Building Game Objects",
            "🗺️ Designing Game Rooms",
            "🎬 Using the Event System",
            "🎯 Collision Detection Tutorial",
            "📜 Introduction to Scripting",
            "🚀 Exporting Your Game"
        ])
        layout.addWidget(tutorial_list)

        layout.addWidget(QLabel(self.tr("\n💡 Tip: Check the documentation (F1) for quick help!")))

        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def about(self):
        """Show comprehensive About PyGameMaker dialog"""
        about_text = self.tr(
            "<h2>PyGameMaker IDE</h2>"
            "<p><b>Version 0.9.0</b></p>"
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
        )

        QMessageBox.about(self, self.tr("About PyGameMaker"), about_text)

    def on_asset_selected(self, asset_data):
        self.properties_panel.set_asset(asset_data)

    def on_asset_imported(self, asset_name, asset_type, asset_data):
        """Handle asset import with correct signal signature"""
        self.update_status(self.tr("Imported {0}").format(asset_name))

        # Refresh sprite combo if it's a sprite import
        if asset_type == 'sprites':
            if hasattr(self, 'properties_panel') and hasattr(self.properties_panel, 'refresh_sprite_combo'):
                self.properties_panel.refresh_sprite_combo()
                print(f"Refreshed sprite combo after importing {asset_name}")

    def on_asset_double_clicked(self, asset_data):
        """Handle double-click on assets to open in appropriate editor"""
        asset_type = asset_data.get('asset_type', '')
        asset_name = asset_data.get('name', '')
        asset_info = asset_data.get('data', {})

        if asset_type == 'rooms':
            self.open_room_editor(asset_name, asset_info)
        elif asset_type == 'objects':
            self.open_object_editor(asset_name, asset_info)
        else:
            # For now, just show a message for other asset types
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, self.tr("Editor"),
                                self.tr("Editor for {0} not yet implemented.\n"
                                    "Asset: {1}").format(asset_type, asset_name))

    def open_room_editor(self, room_name: str, room_data: dict):
        """Open a room in the room editor"""

        # Check if room is already open
        if room_name in self.open_editors:
            # Switch to existing tab
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

            # Connect room editor activation signal
            room_editor.room_editor_activated.connect(self.on_room_editor_activated, Qt.ConnectionType.UniqueConnection)

            # Add to tabs
            tab_index = self.editor_tabs.addTab(room_editor, room_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            # Track the editor
            self.open_editors[room_name] = room_editor

            self.update_status(self.tr("Opened room: {0}").format(room_name))

        except Exception as e:
            print(f"Error opening room editor: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open room editor: {0}").format(e))

    def open_object_editor(self, object_name: str, object_data: dict):
        """Open an object in the object editor"""

        # Check if object is already open
        if object_name in self.open_editors:
            # Switch to existing tab
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

            # Connect object editor activation signal
            object_editor.object_editor_activated.connect(self.on_object_editor_activated, Qt.ConnectionType.UniqueConnection)

            # Add to tabs - object editor occupies full center panel
            tab_index = self.editor_tabs.addTab(object_editor, object_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            # Track the editor
            self.open_editors[object_name] = object_editor

            # Hide the properties panel when object editor is active
            # (Object editor has its own internal properties)
            if hasattr(self, 'properties_panel'):
                self.properties_panel.hide()

            self.update_status(self.tr("Opened object: {0}").format(object_name))

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open object editor: {0}").format(e))

    def on_object_editor_activated(self, object_name: str, object_properties: dict):
        """Handle object editor activation"""
        print(f"🚨🚨🚨 IDE: on_object_editor_activated called for {object_name}")
        print(f"🚨 IDE: properties_panel exists? {hasattr(self, 'properties_panel')}")
        print(f"🚨 IDE: properties_panel type: {type(self.properties_panel).__name__ if hasattr(self, 'properties_panel') else 'N/A'}")

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
            print("ERROR: No project manager available")
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
                print("Could not determine asset type")
                return

            print(f"💾 Saving: category='{asset_category}', type_field='{asset_type_field}'")

            # Ensure required fields with CORRECT singular asset_type
            asset_data['imported'] = True
            asset_data['name'] = asset_name
            asset_data['asset_type'] = asset_type_field  # SINGULAR form

            # Debug: Print what we're about to save
            if asset_category == 'rooms':
                print(f"💾 Room data keys: {list(asset_data.keys())}")
                print(f"💾 Background color: {asset_data.get('background_color', 'NOT SET')}")
                print(f"💾 Instances count: {len(asset_data.get('instances', []))}")

            # Use the project manager's update method with PLURAL category
            if self.project_manager.update_asset(asset_category, asset_name, asset_data):
                pass  # Success
            else:
                print(f"Failed to update asset {asset_name}")
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

                print(f"✅ Save completed successfully for {asset_name}")

            else:
                print("Project save FAILED")
                QMessageBox.warning(self, self.tr("Save Error"),
                                  self.tr("Failed to save project to disk"))
                return

        except Exception as e:
            print(f"Error in save: {e}")
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

    def close_editor_by_name(self, asset_name: str):
        """Close editor tab by asset name"""
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.tabText(i).replace('*', '') == asset_name:
                self.close_editor_tab(i)
                break

    def on_project_loaded(self, project_path, project_data):
        print(f"DEBUG on_project_loaded: START - path={project_path}, data_keys={list(project_data.keys()) if project_data else None}")
        self.current_project_path = project_path
        self.current_project_data = project_data

        # Initialize game runner with project
        try:
            project_json = Path(project_path) / "project.json"
            if project_json.exists():
                self.game_runner = GameRunner(str(project_json))
                print(f"Game runner initialized for project: {project_json}")
            else:
                print(f"Warning: project.json not found at {project_json}")
                self.game_runner = None
        except Exception as e:
            print(f"Error initializing game runner: {e}")
            import traceback
            traceback.print_exc()
            self.game_runner = None

        # Load assets into asset tree (order is preserved through OrderedDict)
        print(f"DEBUG on_project_loaded: calling asset_tree.set_project")
        self.asset_tree.set_project(str(project_path), project_data)
        print(f"DEBUG on_project_loaded: asset_tree.set_project done")

        # Set project base path for properties panel
        if hasattr(self.properties_panel, 'set_project_base_path'):
            self.properties_panel.set_project_base_path(str(project_path))

        self.update_window_title()
        self.update_ui_state()
        self.update_status(self.tr("Project loaded: {0}").format(project_data['name']))
        print(f"DEBUG on_project_loaded: END")

    def on_project_saved(self):
        self.update_status(self.tr("Project saved"))

    def update_window_title(self):
        if self.current_project_data:
            title = f"PyGameMaker - {self.current_project_data['name']}"
            if self.project_manager.is_dirty():
                title += " *"
        else:
            title = "PyGameMaker IDE"

        self.setWindowTitle(title)

    def update_ui_state(self):
        has_project = self.current_project_path is not None

        for action in self.findChildren(QAction):
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
        if hasattr(self, 'export_project_action'):
            self.export_project_action.setEnabled(has_project)
        # Enable/disable build actions based on project state
        if hasattr(self, 'test_game_action'):
            self.test_game_action.setEnabled(has_project)
        if hasattr(self, 'debug_game_action'):
            self.debug_game_action.setEnabled(has_project)
        if hasattr(self, 'build_game_action'):
            self.build_game_action.setEnabled(has_project)
        if hasattr(self, 'build_and_run_action'):
            self.build_and_run_action.setEnabled(has_project)
        if hasattr(self, 'export_game_action'):
            self.export_game_action.setEnabled(has_project)

        if has_project:
            self.project_label.setText(self.tr("Project: {0}").format(self.current_project_data['name']))
        else:
            self.project_label.setText(self.tr("No project loaded"))

    def update_status(self, message):
        self.status_label.setText(message)

        QTimer.singleShot(3000, lambda: self.status_label.setText(self.tr("Ready")))

    def refresh_object_sprites(self, object_name: str, old_sprite: str, new_sprite: str):
        """Refresh object sprites in room editors when they change"""
        print(f"Refreshing sprite for object {object_name}: {old_sprite} -> {new_sprite}")

        # Refresh all room editors
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if hasattr(widget, 'room_canvas') and hasattr(widget, 'object_palette'):
                # Clear sprite cache for the object
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
        recent = Config.get("recent_projects", [])

        if project_path in recent:
            recent.remove(project_path)

        recent.insert(0, project_path)
        recent = recent[:10]

        Config.set("recent_projects", recent)

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
            print("🔄 Language change event detected, recreating menus...")
            self.menuBar().clear()
            self.create_menu_bar()
            self.create_toolbar()
            print("✅ Menus and toolbars recreated with new language")

        # Call parent class handler
        super().changeEvent(event)
