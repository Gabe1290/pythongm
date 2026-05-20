#!/usr/bin/env python3
"""
Base Editor Class for GameMaker IDE
Provides common functionality for all asset editors
"""

from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import json

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBar, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QUndoCommand, QUndoStack

from core.logger import get_logger
from editors._floatable_editor import FloatableEditorMixin
logger = get_logger(__name__)


class EditorUndoCommand(QUndoCommand):
    """Base undo command for editor operations"""

    def __init__(self, editor, description: str):
        super().__init__(description)
        self.editor = editor
        self.old_data = None
        self.new_data = None

    def undo(self):
        """Undo the operation"""
        if self.old_data is not None:
            self.editor.load_data(self.old_data)

    def redo(self):
        """Redo the operation"""
        if self.new_data is not None:
            self.editor.load_data(self.new_data)


class BaseEditor(FloatableEditorMixin, QWidget):
    """
    Base class for all asset editors in the IDE
    Provides common functionality like save/load, undo/redo, etc.
    """

    # Signals (float_requested/reattach_requested come from FloatableEditorMixin)
    data_modified = Signal(str)  # asset_name
    save_requested = Signal(str, dict)  # asset_name, data
    close_requested = Signal(str)  # asset_name
    status_changed = Signal(str)  # status_message

    def __init__(self, project_path: Optional[str] = None, parent=None):
        super().__init__(parent)

        # Core properties
        self.project_path = project_path
        self.asset_name = None
        self.asset_data = {}
        self.is_modified = False
        self.is_read_only = False

        # Undo/Redo system
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(200)
        self.undo_stack.canUndoChanged.connect(self.update_undo_actions)
        self.undo_stack.canRedoChanged.connect(self.update_undo_actions)

        # Auto-save timer (parented to self so it dies with the editor and
        # doesn't fire after the widget is gone)
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.setSingleShot(True)

        # Auto-save settings
        self.auto_save_enabled = True  # Can be toggled
        self.auto_save_delay_ms = 3000  # 3 seconds default
        self._saving = False  # Guard to prevent re-modification during save

        # Setup UI
        self.setup_base_ui()
        self.setup_shortcuts()

        # Track modification state
        self.data_modified.connect(self.on_data_modified)

    def setup_base_ui(self):
        """Setup basic UI components common to all editors"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # Minimize spacing between toolbar, status, and content

        # Create toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)

        # Add common actions
        self.setup_toolbar_actions()
        layout.addWidget(self.toolbar)

        # Status bar with enhanced indicators - make it very compact
        from editors.editor_status_widget import EditorStatusWidget
        self.status_widget = EditorStatusWidget()
        self.status_widget.setMaximumHeight(20)  # Limit status bar height
        layout.addWidget(self.status_widget, 0)  # No stretch factor

        # Keep original status label for compatibility
        self.status_label = self.status_widget.status_label

        # Content area - to be implemented by subclasses
        # CRITICAL: Give content widget stretch factor so it expands
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.content_widget, 1)  # Stretch factor = 1, takes all available space

    def setup_toolbar_actions(self):
        """Setup common toolbar actions"""
        # Save action
        self.save_action = self.toolbar.addAction(self.tr("💾 Save"), self.save)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.setEnabled(False)

        # Auto-save toggle - IMPROVED VERSION
        self.auto_save_action = self.toolbar.addAction(self.tr("🔄 Auto-save: ON"), self.toggle_auto_save)
        self.auto_save_action.setCheckable(True)
        self.auto_save_action.setChecked(self.auto_save_enabled)
        self.auto_save_action.setToolTip(self.tr("Toggle automatic saving (currently every 3 seconds)"))

        # Update the text based on state
        self.update_auto_save_button_text()

        self.toolbar.addSeparator()

        # Undo/Redo actions (no keyboard shortcuts — the IDE Edit menu
        # owns Ctrl+Z / Ctrl+Y and delegates to the active editor)
        self.undo_action = self.toolbar.addAction(self.tr("↶ Undo"), self.undo_stack.undo)
        self.undo_action.setEnabled(False)

        self.redo_action = self.toolbar.addAction(self.tr("↷ Redo"), self.undo_stack.redo)
        self.redo_action.setEnabled(False)

        self.toolbar.addSeparator()

        # Float / Attach toggle — lets the user pop this editor out into its
        # own window and back. The IDE listens on float_requested to do the
        # reparent; reattach happens automatically when the floating window
        # closes (see DetachedEditorWindow). The label flips to indicate state.
        self.float_action = self.toolbar.addAction(self.tr("🪟 Float"), self._on_float_clicked)
        self.float_action.setToolTip(self.tr("Open this editor in its own window"))
        self._is_floating = False

    def update_auto_save_button_text(self):
        """Update auto-save button text to show current state"""
        if hasattr(self, 'auto_save_action'):
            if self.auto_save_enabled:
                self.auto_save_action.setText(self.tr("🔄 Auto-save: ON"))
                self.auto_save_action.setToolTip(self.tr("Auto-save is enabled. Click to disable."))
            else:
                self.auto_save_action.setText(self.tr("⏸️ Auto-save: OFF"))
                self.auto_save_action.setToolTip(self.tr("Auto-save is disabled. Click to enable."))

    def toggle_auto_save(self):
        """Toggle auto-save on/off"""
        new_state = not self.auto_save_enabled
        self.set_auto_save_enabled(new_state)
        self.auto_save_action.setChecked(new_state)

        # Update button text to reflect new state
        self.update_auto_save_button_text()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Save shortcut
        QShortcut(QKeySequence.Save, self, self.save)

        # Close shortcut
        QShortcut(QKeySequence("Ctrl+W"), self, self.request_close)

        # Refresh shortcut
        QShortcut(QKeySequence("F5"), self, self.refresh)

    # _on_float_clicked / set_floating_state provided by FloatableEditorMixin

    def update_undo_actions(self):
        """Update undo/redo action states"""
        self.undo_action.setEnabled(self.undo_stack.canUndo())
        self.redo_action.setEnabled(self.undo_stack.canRedo())

        # Update action text with command descriptions
        if self.undo_stack.canUndo():
            self.undo_action.setText(self.tr("↶ Undo {0}").format(self.undo_stack.undoText()))
        else:
            self.undo_action.setText(self.tr("↶ Undo"))

        if self.undo_stack.canRedo():
            self.redo_action.setText(self.tr("↷ Redo {0}").format(self.undo_stack.redoText()))
        else:
            self.redo_action.setText(self.tr("↷ Redo"))

    def load_asset(self, asset_name: str, asset_data: Dict[str, Any]):
        """Load an asset for editing"""



        self.asset_name = asset_name
        self.asset_data = asset_data.copy()
        self.is_modified = False

        # Clear undo stack
        self.undo_stack.clear()

        # Load the data into the editor
        self.load_data(asset_data)

        # Update UI
        self.update_window_title()
        self.update_status(self.tr("Loaded: {0}").format(asset_name))

    @abstractmethod
    def load_data(self, data: Dict[str, Any]):
        """Load data into the editor - must be implemented by subclasses"""

    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Get current data from the editor - must be implemented by subclasses"""

    @abstractmethod
    def validate_data(self) -> tuple[bool, str]:
        """Validate current data - returns (is_valid, error_message)"""

    def save(self):
        """Save the current asset"""
        if self.is_read_only:
            QMessageBox.information(self, "Read Only", "This asset is read-only and cannot be saved.")
            return False

        # Validate data
        is_valid, error_msg = self.validate_data()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", f"Cannot save: {error_msg}")
            return False

        self._saving = True
        try:
            # Get current data
            current_data = self.get_data()

            # Emit save request
            self.save_requested.emit(self.asset_name, current_data)

            # Update state
            self.asset_data = current_data.copy()
            self.is_modified = False
            self.save_action.setEnabled(False)

            # Update UI
            self.update_window_title()
            self.update_status(f"Saved: {self.asset_name}")

            # Update status widget if available
            if hasattr(self, 'status_widget'):
                self.status_widget.set_saved()

            return True

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving asset: {e}")
            return False
        finally:
            self._saving = False

    def auto_save(self):
        """Auto-save the asset if enabled and modified"""
        if not self.auto_save_enabled:
            return

        if self.is_modified and not self.is_read_only:
            logger.info(f"Auto-saving: {self.asset_name}")
            success = self.save()
            if success:
                self.update_status(self.tr("Auto-saved: {0}").format(self.asset_name))
                # Ensure blink timer is stopped after auto-save
                if hasattr(self, 'status_widget'):
                    self.status_widget.blink_timer.stop()
                    self.status_widget._hide_dot()
            return success
        return False

    def start_auto_save_timer(self, delay_ms: int = None):
        """Start auto-save timer with specified delay"""
        if not self.auto_save_enabled:
            return

        if delay_ms is None:
            delay_ms = self.auto_save_delay_ms

        self.auto_save_timer.stop()
        self.auto_save_timer.start(delay_ms)

    def set_auto_save_enabled(self, enabled: bool):
        """Enable or disable auto-save"""
        self.auto_save_enabled = enabled

        if not enabled:
            self.auto_save_timer.stop()
        elif self.is_modified:
            self.start_auto_save_timer()

        self.update_window_title()

        # Update status widget
        if hasattr(self, 'status_widget'):
            self.status_widget.set_auto_save_enabled(enabled)

        # Update button text
        if hasattr(self, 'update_auto_save_button_text'):
            self.update_auto_save_button_text()

        status = "enabled" if enabled else "disabled"
        self.update_status(f"Auto-save {status}")


    def refresh(self):
        """Refresh the editor content"""
        if self.asset_data:
            self.load_data(self.asset_data)
            self.update_status("Refreshed")

    def request_close(self):
        """Request to close this editor"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, 'Unsaved Changes',
                f'Asset "{self.asset_name}" has unsaved changes.\nSave before closing?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Save:
                if not self.save():
                    return False

        self.close_requested.emit(self.asset_name)
        return True

    def on_data_modified(self, asset_name: str):
        """Handle data modification signal"""
        # Ignore modifications triggered during save (e.g. properties panel refresh)
        if self._saving:
            return

        if asset_name == self.asset_name:
            self.is_modified = True
            self.save_action.setEnabled(True)
            self.update_window_title()

            # Update status widget
            if hasattr(self, 'status_widget'):
                self.status_widget.set_modified(True, self.auto_save_enabled)

            # Start auto-save timer if enabled
            if self.auto_save_enabled:
                self.start_auto_save_timer()

    def update_window_title(self):
        """Update window title to reflect modification state"""
        title = self.asset_name or "Untitled"

        # Add modification indicator
        if self.is_modified:
            if self.auto_save_enabled:
                title += "● "  # Bullet indicates unsaved but auto-save is on
            else:
                title += "* "  # Asterisk indicates unsaved, manual save required

        if self.is_read_only:
            title += " (Read Only)"

        # Add auto-save status
        if not self.auto_save_enabled:
            title += " [Manual Save]"

        self.setWindowTitle(title)

    def update_status(self, message: str):
        """Update status message"""
        self.status_label.setText(message)
        self.status_changed.emit(message)

    def undo(self):
        """Undo the last operation (called by IDE Edit menu)."""
        if self.undo_stack.canUndo():
            self.undo_stack.undo()

    def redo(self):
        """Redo the last undone operation (called by IDE Edit menu)."""
        if self.undo_stack.canRedo():
            self.undo_stack.redo()




    def load_project_data(self) -> Dict[str, Any]:
        """Load project.json data"""
        if not self.project_path:
            return {}

        try:
            project_file = Path(self.project_path) / "project.json"
            if project_file.exists():
                with open(project_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading project data: {e}")

        return {}

    def closeEvent(self, event):
        """Handle widget close event"""
        if self.request_close():
            # Stop the timer before accept so it can't fire after deleteLater
            if hasattr(self, 'auto_save_timer'):
                self.auto_save_timer.stop()
            event.accept()
        else:
            event.ignore()

    # Virtual methods for subclasses to override
    def on_project_assets_loaded(self, assets: Dict[str, Any]):
        """Called when project assets are loaded - override in subclasses"""

    def on_asset_external_change(self, asset_name: str, new_data: Dict[str, Any]):
        """Called when asset is changed externally - override in subclasses"""
        if asset_name == self.asset_name:
            reply = QMessageBox.question(
                self, 'External Change',
                f'Asset "{asset_name}" was modified externally.\nReload changes?',
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.load_asset(asset_name, new_data)
