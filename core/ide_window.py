#!/usr/bin/env python3

import sys
from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                               QSplitter, QMenuBar, QStatusBar, QMessageBox, QDialog,
                               QFileDialog, QInputDialog, QProgressBar, QLabel, QStyle,
                               QTabWidget, QTextBrowser, QSizePolicy, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
from PySide6.QtGui import QAction, QKeySequence, QFont

from widgets.asset_tree.asset_tree_widget import AssetTreeWidget
# from widgets.properties_panel import PropertiesPanel
from widgets.enhanced_properties_panel import EnhancedPropertiesPanel 
from core.project_manager import ProjectManager
from core.asset_manager import AssetManager
from dialogs.project_dialogs import NewProjectDialog, ProjectSettingsDialog
from dialogs.import_dialogs import ImportAssetDialog
from utils.config import Config
from editors.room_editor import RoomEditor
from editors.object_editor import ObjectEditor
from runtime.game_runner import GameRunner

class PyGameMakerIDE(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        # Create managers in the right order
        self.asset_manager = AssetManager()  # CREATE ASSET MANAGER FIRST
        self.project_manager = ProjectManager()  # CREATE PROJECT MANAGER SECOND
        
        # Connect them together - THIS IS CRITICAL
        try:
            print("DEBUG: About to connect asset manager...")
            self.project_manager.set_asset_manager(self.asset_manager)
            print("DEBUG: Asset manager connected successfully!")
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
        
        # Add game runner
        self.game_runner = GameRunner()

        print("DEBUG: About to setup UI...")
        self.setup_ui()
        print("DEBUG: UI setup complete, about to setup connections...")
        self.setup_connections()
        print("DEBUG: Connections setup complete, about to setup styling...")
        self.setup_styling()
        print("DEBUG: Styling setup complete...")
        self.restore_geometry()
        
        self.update_window_title()
        self.update_ui_state()
    
    def setup_ui(self):
        self.setWindowTitle("PyGameMaker IDE")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        print("DEBUG: About to create menu bar...")
        try:
            self.create_menu_bar()

            # Set initial auto-save checkbox state from config
            from utils.config import Config
            auto_save_enabled = Config.get('auto_save_enabled', True)
            if hasattr(self, 'auto_save_action'):
                self.auto_save_action.setChecked(auto_save_enabled)
            
            print("DEBUG: Menu bar created successfully!")
        except Exception as e:
            print(f"ERROR in create_menu_bar: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        print("DEBUG: About to create toolbar...")
        try:
            self.create_toolbar()
            print("DEBUG: Toolbar created successfully!")
        except Exception as e:
            print(f"ERROR in create_toolbar: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        print("DEBUG: About to create main widget...")
        try:
            self.create_main_widget()
            print("DEBUG: Main widget created successfully!")
        except Exception as e:
            print(f"ERROR in create_main_widget: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        print("DEBUG: About to create status bar...")
        try:
            self.create_status_bar()
            print("DEBUG: Status bar created successfully!")
        except Exception as e:
            print(f"ERROR in create_status_bar: {e}")
            import traceback
            traceback.print_exc()
            raise

        # Connect the rename signal
        print("DEBUG: About to connect rename signal...")
        self.asset_tree.asset_renamed.connect(self.on_asset_renamed)
        print("DEBUG: Rename signal connected!")
    
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
        file_menu.addAction(self.create_action(self.tr("Export as HTML5..."), None, self.export_html5))
        file_menu.addAction(self.create_action(self.tr("Export as &Zip..."), None, self.export_project_zip))
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
        build_menu.addAction(self.create_action(self.tr("&Test Game"), "F5", self.test_game))
        build_menu.addAction(self.create_action(self.tr("&Debug Game"), "F6", self.debug_game))
        build_menu.addSeparator()
        build_menu.addAction(self.create_action(self.tr("&Build Game..."), "F7", self.build_game))
        build_menu.addAction(self.create_action(self.tr("Build and &Run"), "F8", self.build_and_run))
        build_menu.addSeparator()
        build_menu.addAction(self.create_action(self.tr("&Export Game..."), None, self.export_game))
        
        tools_menu = menubar.addMenu(self.tr("&Tools"))
        tools_menu.addAction(self.create_action(self.tr("&Preferences..."), None, self.preferences))
        tools_menu.addAction(self.create_action(self.tr("&Asset Manager..."), None, self.show_asset_manager))
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
        help_menu.addAction(self.create_action(self.tr("About &Qt"), None, self.about_qt))
    
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
            action.setChecked(code == current_lang)
            action.setData(code)  # Store language code
            
            # Show if translation is available
            if not language_manager.is_translation_available(code) and code != 'en':
                action.setText(f"{flag} {name} (translation not available)")
            
            action.triggered.connect(lambda checked, lang=code: self.change_language(lang))
            self.language_action_group.addAction(action)
    
    def change_language(self, language_code: str):
        """Change the application language"""
        from core.language_manager import get_language_manager
        from PySide6.QtWidgets import QMessageBox
        
        language_manager = get_language_manager()
        
        # Get language name for display
        lang_name = ""
        for code, name, flag in language_manager.get_available_languages():
            if code == language_code:
                lang_name = name
                break
        
        # Set the language
        success = language_manager.set_language(language_code)
        
        if success or language_code == 'en':
            # Show restart message
            QMessageBox.information(
                self,
                self.tr("Language Changed"),
                self.tr("Language changed to {0}.\n\n"
                    "Please restart PyGameMaker IDE for the changes to take full effect.").format(lang_name)
            )
        else:
            # Translation file not found
            QMessageBox.warning(
                self,
                self.tr("Translation Not Available"),
                self.tr("Translation file for {0} is not available.\n\n"
                    "The language has been set, but the interface will remain in English until "
                    "a translation file is provided.\n\n"
                    "Expected file: translations/pygamemaker_{1}.qm").format(lang_name, language_code)
            )

    def export_html5(self):
        """Export project as HTML5"""
        if not self.current_project_path:
            QMessageBox.information(
                self, 
                self.tr("No Project"), 
                self.tr("Please open a project first")
            )
            return
        
        from exporters.html5_exporter import HTML5Exporter
        
        output_dir = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Export Directory"),
            str(Path.home())
        )
        
        if output_dir:
            exporter = HTML5Exporter()
            
            # Show progress
            self.update_status(self.tr("Exporting to HTML5..."))
            
            if exporter.export(self.current_project_path, Path(output_dir)):
                output_file = Path(output_dir) / f"{self.current_project_data['name']}.html"
                
                reply = QMessageBox.question(
                    self,
                    self.tr("Export Successful"),
                    self.tr("Game exported as HTML5!\n\n{0}\n\nOpen in browser now?").format(output_file.name),
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    import webbrowser
                    webbrowser.open(str(output_file))
                
                self.update_status(self.tr("HTML5 export complete"))
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Export Failed"),
                    self.tr("Failed to export game as HTML5. Check console for details.")
                )
                self.update_status(self.tr("Export failed"))

    def export_project_zip(self):
        """Export current project as a .zip file"""
        if not self.current_project_path:
            QMessageBox.information(self, self.tr("No Project"), self.tr("Please open a project first"))
            return
        
        # Get default filename
        project_name = self.current_project_data.get('name', 'project')
        default_filename = f"{project_name}.zip"
        
        # Ask user where to save
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            self.tr("Export Project as Zip"),
            str(Path.home() / default_filename),
            self.tr("Zip Files (*.zip)")
        )
        
        if file_path:
            zip_path = Path(file_path)
            
            # Show progress
            self.update_status(self.tr("Exporting project..."))
            
            # Export
            if self.project_manager.export_project_as_zip(zip_path):
                QMessageBox.information(
                    self,
                    self.tr("Export Successful"),
                    self.tr("Project exported to:\n{0}").format(zip_path)
                )
                self.update_status(self.tr("Project exported"))
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Export Failed"),
                    self.tr("Failed to export project as zip")
                )
                self.update_status(self.tr("Export failed"))

    def open_project_zip(self):
        """Open a project from a .zip file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            self.tr("Open Zip Project"),
            Config.get("last_project_directory", str(Path.home())),
            self.tr("Zip Files (*.zip)")
        )
        
        if file_path:
            zip_path = Path(file_path)
            
            # Check if it's a valid project zip
            from utils.project_compression import ProjectCompressor
            if not ProjectCompressor.is_project_zip(zip_path):
                QMessageBox.warning(
                    self,
                    self.tr("Invalid Zip"),
                    self.tr("This zip file does not contain a valid PyGameMaker project")
                )
                return
            
            # Show progress
            self.update_status(self.tr("Loading project from zip..."))
            
            # Load
            if self.project_manager.load_project_from_zip(zip_path):
                Config.set("last_project_directory", str(zip_path.parent))
                self.update_status(self.tr("Project loaded from zip"))
            else:
                QMessageBox.warning(
                    self, 
                    self.tr("Error"), 
                    self.tr("Failed to load project from zip")
                )
                self.update_status(self.tr("Failed to load"))

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
        print("DEBUG: Connecting asset_tree signals...")
        self.asset_tree.asset_selected.connect(self.on_asset_selected)
        self.asset_tree.asset_imported.connect(self.on_asset_imported)
        
        self.asset_tree.asset_double_clicked.connect(self.on_asset_double_clicked)
        print("DEBUG: Connecting project_manager signals...")
        self.project_manager.project_loaded.connect(self.on_project_loaded)
        self.project_manager.project_saved.connect(self.on_project_saved)
        self.project_manager.status_changed.connect(self.update_status)
        print("DEBUG: All connections complete!")
    
    def setup_styling(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QMenuBar {
                background-color: #e0e0e0;
                border-bottom: 1px solid #c0c0c0;
            }
            QMenuBar::item {
                padding: 4px 8px;
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #d0d0d0;
            }
            QToolBar {
                background-color: #e8e8e8;
                border: none;
                spacing: 3px;
            }
            QStatusBar {
                background-color: #e0e0e0;
                border-top: 1px solid #c0c0c0;
            }
            QTreeWidget {
                background-color: white;
                border: 1px solid #ccc;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 3px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QSplitter::handle {
                background-color: #ccc;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #999;
            }
        """)

    def create_action(self, text, shortcut, slot, icon_name=None):
        action = QAction(text, self)
        
        if shortcut:
            action.setShortcut(shortcut)
        
        if icon_name:
            try:
                style = self.style()
                if hasattr(QStyle.StandardPixmap, icon_name):
                    pixmap_enum = getattr(QStyle.StandardPixmap, icon_name)
                    icon = style.standardIcon(pixmap_enum)
                    if not icon.isNull():
                        action.setIcon(icon)
            except:
                pass  # Silently ignore icon loading errors
        
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
            
            if self.project_manager.create_project(
                project_info["name"],
                project_info["path"],
                project_info["template"]
            ):
                self.update_status(self.tr("Project created successfully"))
            else:
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
        if self.project_manager.load_project(project_path):
            Config.set("last_project_directory", str(project_path.parent))
            self.add_to_recent_projects(str(project_path))
        else:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to load project"))
    
    def save_project(self):
        if self.current_project_path:
            if self.project_manager.save_project():
                self.update_status(self.tr("Project saved"))
            else:
                QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to save project"))
        else:
            self.save_project_as()
    
    def save_project_as(self):
        if not self.current_project_data:
            return
        
        directory = QFileDialog.getExistingDirectory(
            self, self.tr("Save Project As"),
            Config.get("last_project_directory", str(Path.home()))
        )
        
        if directory:
            project_path = Path(directory)
            if self.project_manager.save_project_as(project_path):
                self.update_status(self.tr("Project saved"))
            else:
                QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to save project"))
    
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
            if hasattr(self, 'properties_widget') and self.properties_widget:
                # Check if properties panel is currently showing the renamed asset
                if hasattr(self.properties_widget, 'name_edit'):
                    current_displayed_name = self.properties_widget.name_edit.text()
                    
                    if current_displayed_name == old_name:
                        
                        # Find the updated asset data in the tree
                        updated_asset_item = self.find_renamed_asset(new_name, asset_type)
                        if updated_asset_item and hasattr(updated_asset_item, 'asset_data'):
                            # Refresh the properties panel with new data
                            self.properties_widget.set_asset(updated_asset_item.asset_data)
            
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
        if not self.current_project_path:
            QMessageBox.information(self, self.tr("No Project"), self.tr("Please open a project first"))
            return
        
        if self.game_runner.is_game_running():
            # Game is running, offer to stop it
            reply = QMessageBox.question(
                self, self.tr("Game Running"), 
                self.tr("A game is already running. Stop it?"),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.game_runner.stop_game()
                self.update_status(self.tr("Game stopped"))
            return
        
        # Save project first
        if self.project_manager.is_dirty():
            self.save_project()
        
        # Test the game
        self.update_status(self.tr("Starting game..."))
        
        if self.game_runner.test_game(str(self.current_project_path)):
            self.update_status(self.tr("Game started - Close game window or press ESC to stop"))
        else:
            self.update_status(self.tr("Failed to start game"))
            QMessageBox.warning(self, self.tr("Game Error"), 
                            self.tr("Failed to start the game. Check console for details."))
    
    def debug_game(self):
        self.update_status(self.tr("Debugging game..."))

    def build_game(self):
        self.update_status(self.tr("Building game..."))

    def build_and_run(self):
        self.update_status(self.tr("Building and running game..."))

    def export_game(self):
        self.update_status(self.tr("Exporting game..."))

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
        pass
    
    def find_replace(self):
        pass
    
    def preferences(self):
        pass
    
    def show_asset_manager(self):
        pass
    
    def validate_project(self):
        pass
    
    def clean_project(self):
        pass
    
    def show_documentation(self):
        pass
    
    def show_tutorials(self):
        pass
    
    def about(self):
        QMessageBox.about(self, self.tr("About PyGameMaker"), 
                        self.tr("PyGameMaker IDE v1.0.0\n\n"
                                "A visual game development environment\n"
                                "inspired by GameMaker Studio."))
    
    def about_qt(self):
        QMessageBox.aboutQt(self)
    
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
        asset_type = asset_data.get('type', '')
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
            
            # Connect editor signals
            room_editor.save_requested.connect(self.on_editor_save_requested)
            room_editor.close_requested.connect(self.on_editor_close_requested)
            room_editor.data_modified.connect(self.on_editor_data_modified)
            
            # Connect room editor activation signal
            room_editor.room_editor_activated.connect(self.on_room_editor_activated)
            
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
            
            # Connect editor signals
            object_editor.save_requested.connect(self.on_editor_save_requested)
            object_editor.close_requested.connect(self.on_editor_close_requested)
            object_editor.data_modified.connect(self.on_editor_data_modified)
            
            # Connect object editor activation signal
            object_editor.object_editor_activated.connect(self.on_object_editor_activated)
            
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
        self.current_project_path = project_path
        self.current_project_data = project_data
        
        # Load assets into asset tree (order is preserved through OrderedDict)
        self.asset_tree.set_project(str(project_path), project_data)

        # Set project base path for properties panel
        if hasattr(self.properties_panel, 'set_project_base_path'):
            self.properties_panel.set_project_base_path(str(project_path))
        
        self.update_window_title()
        self.update_ui_state()
        self.update_status(self.tr("Project loaded: {0}").format(project_data['name']))

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