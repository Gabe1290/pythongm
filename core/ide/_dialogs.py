#!/usr/bin/env python3
"""Dialog / tool-menu openers for :class:`PyGameMakerIDE`.

Extracted verbatim from ``core/ide_window.py`` (``docs/POST_1_0_REFACTOR.md``
File 2). A mixin -- ``self`` / ``self.tr()`` / siblings resolve on the
concrete window.

Patch-target move: ``mock.patch("core.ide_window.QMessageBox")`` in
test_trash_dialog / test_clean_project_dispatch / test_unused_assets_dialog
/ test_orphaned_files_dialog now targets
``core.ide._dialogs.QMessageBox`` (the methods that use it -- clean_project,
show_trash_dialog, show_unused_assets_dialog, show_orphaned_files_dialog --
live here now).
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from utils.config import Config
from dialogs.blockly_config_dialog import BlocklyConfigDialog
from dialogs.thymio_config_dialog import ThymioConfigDialog
from core.logger import get_logger

logger = get_logger(__name__)


class DialogsMixin:

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
        """Open the Thymio Playground simulator window.

        Reuse a still-live window instead of leaking a new one on every open,
        and mark it WA_DeleteOnClose so closing it frees the C++ object rather
        than keeping a dangling handle around.
        """
        from widgets.thymio_playground import ThymioPlaygroundWindow
        import shiboken6

        existing = getattr(self, "thymio_playground", None)
        if existing is not None and shiboken6.isValid(existing):
            # Already open and live — raise it instead of spawning another.
            existing.showNormal()
            existing.raise_()
            existing.activateWindow()
            logger.info("Raised existing Thymio Playground window")
            return

        from PySide6.QtCore import Qt
        self.thymio_playground = ThymioPlaygroundWindow(self)
        self.thymio_playground.setAttribute(Qt.WA_DeleteOnClose)
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

    def show_trash_dialog(self):
        """Open the Trash dialog to restore or permanently delete soft-
        deleted assets — see utils/asset_trash.py's module docstring for
        why deletion is a trash mechanism rather than undo/redo."""
        if not self.current_project_path or not self.project_manager.asset_manager:
            QMessageBox.information(
                self,
                self.tr("No Project"),
                self.tr("Please open a project first.")
            )
            return

        from widgets.asset_tree.asset_dialogs import TrashDialog
        dialog = TrashDialog(self.project_manager.asset_manager, parent=self)

        def _on_restored(asset_type, asset_name, asset_data):
            self.asset_tree.add_asset(asset_type, asset_name, asset_data)
            self.project_manager.save_project()
            self.update_status(self.tr("Restored: {0}").format(asset_name))

        dialog.on_restored = _on_restored
        dialog.exec()

    def show_unused_assets_dialog(self):
        """Open the Unused Assets dialog (Tier 4, docs/ASSET_MANAGER_PLAN.md)
        to review and trash assets nothing references."""
        if not self.current_project_path or not self.project_manager.asset_manager:
            QMessageBox.information(
                self,
                self.tr("No Project"),
                self.tr("Please open a project first.")
            )
            return

        from widgets.asset_tree.asset_dialogs import UnusedAssetsDialog
        dialog = UnusedAssetsDialog(
            self.current_project_data, self.project_manager.asset_manager, parent=self)

        def _on_deleted(asset_type, asset_name):
            self.asset_tree.remove_asset(asset_type, asset_name)

        dialog.on_deleted = _on_deleted
        dialog.exec()

        if dialog.deleted_count:
            self.project_manager.save_project()
            self.update_status(
                self.tr("Moved {0} unused asset(s) to Trash").format(dialog.deleted_count))

    def clean_project(self):
        """Tier 1 of docs/CLEAN_PROJECT_PLAN.md: sweep orphaned *.tmp
        atomic-write siblings from the project directory. Unlike asset
        deletion, these never go through the Trash — a .tmp file is never
        the authoritative copy of anything, so permanent removal is
        correct (see utils/project_cleanup.py)."""
        if not self.current_project_path:
            QMessageBox.information(
                self,
                self.tr("No Project"),
                self.tr("Please open a project first.")
            )
            return

        from utils.project_cleanup import sweep_orphan_tmp_files
        removed = sweep_orphan_tmp_files(Path(self.current_project_path))

        if removed:
            names = "\n".join(str(p.relative_to(self.current_project_path)) for p in removed)
            QMessageBox.information(
                self,
                self.tr("Clean Project"),
                self.tr("Removed {0} leftover temporary file(s):\n\n{1}").format(len(removed), names)
            )
            self.update_status(self.tr("Removed {0} leftover temporary file(s)").format(len(removed)))
        else:
            QMessageBox.information(
                self,
                self.tr("Clean Project"),
                self.tr("Nothing to clean — no leftover temporary files found.")
            )

    def show_orphaned_files_dialog(self):
        """Open the Orphaned Files dialog (Tier 3, docs/CLEAN_PROJECT_PLAN.md)
        to review and trash physical asset files nothing references."""
        if not self.current_project_path or not self.project_manager.asset_manager:
            QMessageBox.information(
                self,
                self.tr("No Project"),
                self.tr("Please open a project first.")
            )
            return

        from widgets.asset_tree.asset_dialogs import OrphanedFilesDialog
        dialog = OrphanedFilesDialog(
            self.current_project_data, self.project_manager.asset_manager, parent=self)
        dialog.exec()

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

        # Try relative to source file (development mode). This module is
        # core/ide/_dialogs.py -> parents[2] is the repo root (it was
        # ide_window.py's parent.parent before the File-2 move).
        candidate = Path(__file__).resolve().parents[2] / "Tutorials"
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
