#!/usr/bin/env python3
"""Project lifecycle (new / open / load / save / close) for
:class:`PyGameMakerIDE`.

Extracted verbatim from ``core/ide_window.py`` (``docs/POST_1_0_REFACTOR.md``
File 2). A mixin -- ``self`` / ``self.tr()`` / siblings resolve on the
concrete window. ``closeEvent`` itself stays in the shell (it calls
``self.save_project()`` and uses its own ``Config`` / ``QMessageBox`` --
tests patch ``core.ide_window.{Config,QMessageBox}`` for it and those
must NOT be repointed).

Patch-target moves:
  core.ide_window.Config      -> core.ide._project_actions.Config
  core.ide_window.QMessageBox -> core.ide._project_actions.QMessageBox
    (test_recent_zip_reopen -- load_project; test_project_format_guard --
     _show_load_failure_message)
"""

import copy
import json
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QFileDialog

from utils.config import Config
from dialogs.project_dialogs import NewProjectDialog, ProjectSettingsDialog
from core.logger import get_logger

logger = get_logger(__name__)


class ProjectActionsMixin:

    def open_project_zip(self):
        """Open a project from a .zip file - delegated to exporters module"""
        self.exporters.open_project_zip()

    def new_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec():
            project_info = dialog.get_project_info()
            logger.debug(f"DEBUG new_project: project_info = {project_info}")

            if self.project_manager.create_project(
                project_info["name"],
                project_info["path"],
                project_info["template"],
                # Persist the dialog's Description; create_project writes it
                # straight into project.json (L8) so it's not silently dropped.
                project_info.get("description", "")
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

    def load_project(self, project_path):
        logger.debug(f"load_project: {project_path}")
        project_path = Path(project_path)

        # Switching away from an already-open project tears down its editors
        # (on_project_loaded deleteLater()s them with no is_modified check), so
        # flush their live data into the current project and persist it first —
        # otherwise unsaved in-editor work is silently lost on the switch
        # (audit M12).
        if self.current_project_path and getattr(self, 'project_manager', None):
            try:
                self._flush_open_editors()
                if self.project_manager.is_dirty():
                    self.project_manager.save_project()
            except Exception as e:
                logger.debug(f"Pre-switch editor flush failed: {e}")

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

        # Recent Projects records the .zip path for zip-opened projects, but
        # the folder loader looks for <zip>/project.json and always fails —
        # so every zip entry was a permanently dead Recent item. Route .zip
        # paths through the same zip loader open_project uses (audit M7).
        if project_path.suffix == '.zip':
            from utils.project_compression import ProjectCompressor
            if ProjectCompressor.is_project_zip(project_path):
                if self.project_manager.load_project_from_zip(project_path):
                    self.asset_tree.project_manager = self.project_manager
                    Config.set("last_project_directory", str(project_path.parent))
                    self.add_to_recent_projects(str(project_path))
                    self._warn_missing_extensions()
                else:
                    self._show_load_failure_message(self.tr("Failed to load project from zip"))
            else:
                QMessageBox.warning(self, self.tr("Invalid Zip"),
                                    self.tr("This zip file does not contain a valid PyGameMaker project"))
            return

        if self.project_manager.load_project(project_path):
            self.asset_tree.project_manager = self.project_manager
            Config.set("last_project_directory", str(project_path.parent))
            self.add_to_recent_projects(str(project_path))
            self._warn_missing_extensions()
        else:
            logger.warning(f"load_project: project_manager.load_project failed for {project_path}")
            self._show_load_failure_message(self.tr("Failed to load project"))

    def _show_load_failure_message(self, generic_message):
        """Show a load-failure dialog, upgrading to a specific "needs a
        newer PyGameMaker" message when project_manager.load_project() (or
        load_project_from_zip(), which delegates to it) refused the file
        via the format-version guard rather than failing for some other
        reason. Call this immediately after a load attempt returns False —
        last_load_format_error reflects only the most recent attempt."""
        fmt = getattr(self.project_manager, "last_load_format_error", None)
        if fmt is not None:
            QMessageBox.warning(
                self, self.tr("Project Too New"),
                self.tr(
                    "This project was made with a newer version of "
                    "PyGameMaker (format {0}.{1}). Please update PyGameMaker "
                    "to open it."
                ).format(fmt[0], fmt[1]))
        else:
            QMessageBox.warning(self, self.tr("Error"), generic_message)

    def _unsupported_actions_note(self):
        """A user-facing note listing actions the Kivy codegen had to skip in
        the just-finished export (empty string if none). Kivy exports emit
        `pass # TODO` for actions they don't support; without this the export
        looks fully successful while silently dropping behaviour (F1a)."""
        try:
            from export.Kivy.code_generator import get_unsupported_actions
            skipped = get_unsupported_actions()
        except Exception:
            return ""
        if not skipped:
            return ""
        return "\n\n" + self.tr(
            "Note: {n} action(s) aren't supported by this export target and were "
            "skipped — the exported game will not perform them:\n{actions}"
        ).format(n=len(skipped), actions=", ".join(skipped))

    def _warn_missing_extensions(self):
        """Warn if the just-loaded project uses actions from an extension that is
        turned off, so its raycast/3D-View (or any other extension) features
        don't silently do nothing. Purely advisory; a project that needs no
        disabled extension (the common case) shows nothing.

        Also warns separately when the project's persisted
        ``requires_extensions`` names an extension this install has no trace
        of at all (an older build opening a project saved by a newer one, or
        any install missing an extension folder) — see
        ``not_installed_extensions_for_project`` for why that needs its own
        check: without the extension's manifest this install can't name the
        affected actions, only the extension folder the project recorded."""
        try:
            from events.plugin_loader import (missing_extensions_for_project,
                                               not_installed_extensions_for_project)
            data = getattr(self.project_manager, "current_project_data", None)
            missing = missing_extensions_for_project(data)
            not_installed = not_installed_extensions_for_project(data)
        except Exception as e:
            logger.debug(f"extension dependency check failed: {e}")
            return
        if missing:
            lines = "\n".join(
                self.tr("• {name} — needed for: {actions}").format(
                    name=m["name"], actions=", ".join(m["actions"]))
                for m in missing)
            QMessageBox.warning(
                self, self.tr("Disabled extensions"),
                self.tr(
                    "This project uses features from extensions that are turned "
                    "off:\n\n{list}\n\nThose actions won't run and the project may "
                    "look or behave wrong. You can enable an extension via "
                    "Preferences → Extensions.").format(list=lines))
        if not_installed:
            lines = "\n".join(f"• {folder}" for folder in not_installed)
            QMessageBox.warning(
                self, self.tr("Extensions not installed"),
                self.tr(
                    "This project was created with extensions that aren't "
                    "present in this copy of PyGameMaker:\n\n{list}\n\nAny "
                    "actions from them will be skipped, and the project may "
                    "look or behave wrong. Update PyGameMaker or add the "
                    "missing extension folder(s) to restore them."
                ).format(list=lines))

    def save_project(self):
            """Save the current project

            Returns:
                bool: True if save was successful, False otherwise
            """
            if self.current_project_path:
                # Ctrl+S (now owned by the IDE menu, not the editor — audit
                # M15) must capture the active editor's unsaved edits, so pull
                # every open editor's live data into the project first.
                self._flush_open_editors()
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

    def close_project(self):
        """Close the open project and return the IDE to its no-project state.

        Prompts to save unsaved work (with a cancel path), stops a running
        Test Game, tears down editors (tabbed + floated) exactly as a project
        switch does, clears model/runtime/asset-tree state, and re-shows the
        Welcome tab. No-op (status note only) when nothing is open.

        Returns True if the project was closed, False if there was nothing to
        close or the user cancelled at the save prompt.
        """
        if self.current_project_path is None:
            self.update_status(self.tr("No project is open."))
            return False

        # Offer to save unsaved work first (mirrors closeEvent), honouring a
        # Cancel as "abort the close".
        if self.project_manager.is_dirty():
            reply = QMessageBox.question(
                self, self.tr("Unsaved Changes"),
                self.tr("You have unsaved changes. Do you want to save before closing the project?"),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                # Pull in-editor edits into the project before saving (audit M12).
                self._flush_open_editors()
                if not self.save_project():
                    return False
            elif reply == QMessageBox.Cancel:
                return False

        # Don't orphan a running Test Game subprocess.
        self.stop_game()

        # Tear down editors (tabs + floated) — same sequence as on_project_loaded.
        while self.editor_tabs.count() > 0:
            widget = self.editor_tabs.widget(0)
            self.editor_tabs.removeTab(0)
            if widget and widget is not self.welcome_tab:
                widget.deleteLater()
        for asset_name in list(self.detached_editor_windows.keys()):
            self._destroy_detached_editor(asset_name)
        self.open_editors.clear()

        # Clear model + runtime state (also cleans up any zip temp dir).
        self.project_manager.close_project()
        self.current_project_path = None
        self.current_project_data = None
        self.game_runner = None

        # Reset the asset tree + properties panel to their empty state.
        self.asset_tree.clear_assets()
        if hasattr(self.properties_panel, 'set_project_loaded'):
            self.properties_panel.set_project_loaded(False)

        # Back to the Welcome tab and refresh chrome.
        self._add_welcome_tab()
        self.update_window_title()
        self.update_ui_state()
        if hasattr(self, 'welcome_tab') and hasattr(self.welcome_tab, 'refresh_recent_projects'):
            self.welcome_tab.refresh_recent_projects()
        self.update_status(self.tr("Project closed."))
        return True

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
        self._add_welcome_tab()

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
