#!/usr/bin/env python3

from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                               QSplitter, QMessageBox, QTabWidget,
                               QToolBar, QLineEdit)

from PySide6.QtCore import Qt, QTimer
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
from runtime.game_runner import GameRunner

from core.logger import get_logger
logger = get_logger(__name__)






from core.ide._samples import SamplesMixin
from core.ide._edit_actions import EditActionsMixin
from core.ide._dialogs import DialogsMixin
from core.ide._test_game import TestGameMixin
from core.ide._project_actions import ProjectActionsMixin
from core.ide._assets import AssetsMixin
from core.ide._editor_lifecycle import EditorLifecycleMixin
from core.ide._export import ExportMixin
from core.ide._menu_builder import MenuBuilderMixin


class PyGameMakerIDE(SamplesMixin, EditActionsMixin, DialogsMixin, TestGameMixin,
                     ProjectActionsMixin, AssetsMixin, EditorLifecycleMixin,
                     ExportMixin, MenuBuilderMixin, QMainWindow):

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

            # Set initial auto-save checkbox state from the SAME store that
            # wires the timer (editor config), so the menu checkbox can't
            # desynchronize from the actual auto-save state (audit M6).
            from utils.config import Config
            auto_save_enabled = Config.get_editor_config().get('auto_save_enabled', True)
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

            # Persist to the editor config that startup reads, so the menu
            # toggle survives a restart and stays in sync with the dialog and
            # the checkbox init (audit M6).
            from utils.config import Config
            Config.set_editor_config(auto_save_enabled=enabled)

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

                # Persist to the SAME store startup reads (editor config, in
                # minutes). The old top-level 'auto_save_interval' (seconds)
                # key was never read by anyone and 'auto_save_enabled' drove
                # only the menu checkbox, so the dialog's choice evaporated on
                # restart while the timer re-armed from editor config (audit
                # M6). Sub-minute intervals clamp to 1 minute on persistence
                # (editor-config granularity); the live session still uses the
                # exact seconds via set_auto_save above.
                from utils.config import Config
                Config.set_editor_config(
                    auto_save_enabled=enabled,
                    auto_save_interval=max(1, round(interval_seconds / 60)),
                )

                self.update_status(self.tr("Auto-save settings updated"))






    def create_main_widget(self):
        """Modified to include editor tabs in center"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Asset tree, with a filter box above it
        try:
            self.asset_tree = AssetTreeWidget(self)
        except Exception as e:
            logger.error(f"Failed to create AssetTreeWidget: {e}")
            import traceback
            traceback.print_exc()

        asset_panel = QWidget()
        asset_panel_layout = QVBoxLayout(asset_panel)
        asset_panel_layout.setContentsMargins(0, 0, 0, 0)
        asset_panel_layout.setSpacing(2)

        self.asset_filter_box = QLineEdit()
        self.asset_filter_box.setPlaceholderText(self.tr("Filter assets…"))
        self.asset_filter_box.setClearButtonEnabled(True)
        self.asset_filter_box.textChanged.connect(self.asset_tree.apply_asset_filter)
        asset_panel_layout.addWidget(self.asset_filter_box)
        asset_panel_layout.addWidget(self.asset_tree)

        asset_panel.setMinimumWidth(200)
        asset_panel.setMaximumWidth(300)

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
        self.main_splitter.addWidget(asset_panel)
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

        # Store reference to open editors, keyed by a composite
        # "<category>:<name>" so a room and an object that legally share a name
        # don't collide (L5).
        self.open_editors = {}  # "<category>:<name>" -> editor_widget
        # Composite key -> DetachedEditorWindow for editors floated out of the
        # tab strip. Editors in this dict still appear in self.open_editors
        # but are NOT in self.editor_tabs.
        self.detached_editor_windows = {}

        # Welcome tab (default)
        self.welcome_tab = WelcomeTab(self)
        self._add_welcome_tab()

        layout.addWidget(self.editor_tabs)
        return center_widget

    def _add_welcome_tab(self):
        """(Re-)add the welcome tab without a close button.

        The tab title is self.tr("Welcome"), so it must never be identified
        by its text (translated UIs would mismatch); close_editor_tab guards
        by widget identity instead.
        """
        from PySide6.QtWidgets import QTabBar
        index = self.editor_tabs.addTab(self.welcome_tab, self.tr("Welcome"))
        tab_bar = self.editor_tabs.tabBar()
        tab_bar.setTabButton(index, QTabBar.RightSide, None)
        tab_bar.setTabButton(index, QTabBar.LeftSide, None)


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
            # Actions marked exempt (e.g. the Welcome tab's "More options"
            # entry points) must stay usable with no project loaded; the
            # findChildren sweep would otherwise grey them via the Import/
            # Create substring match below. See WelcomeTab._dropdown_button.
            if action.property("pygm_always_enabled"):
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
        if hasattr(self, 'show_trash_action'):
            self.show_trash_action.setEnabled(has_project)
        if hasattr(self, 'show_unused_assets_action'):
            self.show_unused_assets_action.setEnabled(has_project)
        if hasattr(self, 'clean_project_action'):
            self.clean_project_action.setEnabled(has_project)
        if hasattr(self, 'show_orphaned_files_action'):
            self.show_orphaned_files_action.setEnabled(has_project)
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
        if hasattr(self, 'close_project_action'):
            self.close_project_action.setEnabled(has_project)
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
        if hasattr(self, 'build_game_action'):
            self.build_game_action.setEnabled(has_project)
        if hasattr(self, 'build_and_run_action'):
            self.build_and_run_action.setEnabled(has_project)
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
                # Pull any in-editor edits into the project first, otherwise
                # 'Save' would persist the project without the unsaved editor
                # work it was meant to preserve (audit M12).
                self._flush_open_editors()
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

        # Remove the temp extraction dir of an open .zip project so it isn't
        # left behind in TEMP for the session (close_project is never called;
        # _reset_zip_state rmtrees it without the side effects of a full
        # close_project during teardown) (L7).
        try:
            self.project_manager._reset_zip_state()
        except Exception:
            pass

        event.accept()


    def changeEvent(self, event):
        """Handle events, including language changes"""
        from PySide6.QtCore import QEvent

        if event.type() == QEvent.Type.LanguageChange:
            # Recreate menu bar with new translations
            logger.debug("🔄 Language change event detected, recreating menus...")
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
            logger.debug("✅ Menus and toolbars recreated with new language")

        # Call parent class handler
        super().changeEvent(event)
