#!/usr/bin/env python3
"""
Editor Status Widget - Shows save status and auto-save state
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont


class EditorStatusWidget(QWidget):
    """Widget showing editor status (saved/unsaved, auto-save state)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._blink_color = "#4CAF50"
        self.setup_ui()

        # Animation timer for unsaved indicator
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_blink)
        self.blink_state = False

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)

        # Modified indicator — always present in layout to avoid shifts
        self.modified_label = QLabel("●")
        self.modified_label.setFont(QFont("Arial", 14))
        self.modified_label.setStyleSheet("color: transparent;")
        layout.addWidget(self.modified_label)

        # Status text
        self.status_label = QLabel(self.tr("Saved"))
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Auto-save indicator
        self.auto_save_label = QLabel(self.tr("🔄 Auto-save: ON"))
        self.auto_save_label.setStyleSheet("color: #4CAF50;")
        layout.addWidget(self.auto_save_label)

    def _show_dot(self, color: str):
        """Show the dot with the given color."""
        self._blink_color = color
        self.modified_label.setStyleSheet(f"color: {color};")

    def _hide_dot(self):
        """Hide the dot by making it transparent (keeps layout stable)."""
        self.modified_label.setStyleSheet("color: transparent;")

    def set_modified(self, modified: bool, auto_save_enabled: bool):
        """Update modified status"""
        if modified:
            if auto_save_enabled:
                # Green bullet - will auto-save
                self._show_dot("#4CAF50")
                self.status_label.setText(self.tr("Unsaved (auto-save in 3s)"))
                self.blink_timer.start(500)
            else:
                # Red bullet - needs manual save
                self._show_dot("#F44336")
                self.status_label.setText(self.tr("Unsaved - press Ctrl+S"))
                self.blink_timer.start(300)
        else:
            self.status_label.setText(self.tr("Saved"))
            self.blink_timer.stop()
            self._show_dot("#4CAF50")

    def set_auto_save_enabled(self, enabled: bool):
        """Update auto-save status"""
        if enabled:
            self.auto_save_label.setText(self.tr("🔄 Auto-save: ON"))
            self.auto_save_label.setStyleSheet("color: #4CAF50;")
        else:
            self.auto_save_label.setText(self.tr("⏸️ Auto-save: OFF"))
            self.auto_save_label.setStyleSheet("color: #FF9800;")

    def set_saving(self):
        """Show saving indicator"""
        self.status_label.setText(self.tr("Saving..."))
        self._show_dot("#2196F3")
        self.blink_timer.stop()

    def set_saved(self):
        """Show saved indicator"""
        self.status_label.setText(self.tr("Saved ✓"))
        self._hide_dot()
        self.blink_timer.stop()

        # Show checkmark briefly
        QTimer.singleShot(2000, lambda: self.status_label.setText(self.tr("Saved")))

    def toggle_blink(self):
        """Toggle blink state for unsaved indicator using color transparency to avoid layout shift."""
        self.blink_state = not self.blink_state
        if self.blink_state:
            self.modified_label.setStyleSheet(f"color: {self._blink_color};")
        else:
            self.modified_label.setStyleSheet("color: transparent;")
