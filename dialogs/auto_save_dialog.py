#!/usr/bin/env python3
"""
Auto-Save Settings Dialog for PyGameMaker IDE
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QCheckBox, QSpinBox, QLabel, QPushButton,
                               QDialogButtonBox, QGroupBox)
from PySide6.QtCore import Qt


class AutoSaveSettingsDialog(QDialog):
    """Dialog for configuring auto-save settings"""
    
    def __init__(self, current_enabled: bool = True, current_interval: int = 30, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(self.tr("Auto-Save Settings"))
        self.setModal(True)
        self.resize(400, 250)
        
        self.setup_ui(current_enabled, current_interval)
    
    def setup_ui(self, current_enabled: bool, current_interval: int):
        layout = QVBoxLayout(self)
        
        # Auto-save enable/disable
        enable_group = QGroupBox(self.tr("Auto-Save"))
        enable_layout = QVBoxLayout(enable_group)
        
        self.enable_checkbox = QCheckBox(self.tr("Enable automatic saving"))
        self.enable_checkbox.setChecked(current_enabled)
        self.enable_checkbox.toggled.connect(self.on_enable_toggled)
        enable_layout.addWidget(self.enable_checkbox)
        
        info_label = QLabel(self.tr("When enabled, your project will be saved automatically at regular intervals."))
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        enable_layout.addWidget(info_label)
        
        layout.addWidget(enable_group)
        
        # Interval settings
        interval_group = QGroupBox(self.tr("Save Interval"))
        interval_layout = QFormLayout(interval_group)
        
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(10)  # Minimum 10 seconds
        self.interval_spinbox.setMaximum(600)  # Maximum 10 minutes
        self.interval_spinbox.setValue(current_interval)
        self.interval_spinbox.setSuffix(self.tr(" seconds"))
        self.interval_spinbox.setEnabled(current_enabled)
        
        interval_layout.addRow(self.tr("Save every:"), self.interval_spinbox)
        
        # Preset buttons
        preset_layout = QHBoxLayout()
        
        preset_15 = QPushButton(self.tr("15s"))
        preset_15.clicked.connect(lambda: self.interval_spinbox.setValue(15))
        preset_layout.addWidget(preset_15)
        
        preset_30 = QPushButton(self.tr("30s"))
        preset_30.clicked.connect(lambda: self.interval_spinbox.setValue(30))
        preset_layout.addWidget(preset_30)
        
        preset_60 = QPushButton(self.tr("1m"))
        preset_60.clicked.connect(lambda: self.interval_spinbox.setValue(60))
        preset_layout.addWidget(preset_60)
        
        preset_120 = QPushButton(self.tr("2m"))
        preset_120.clicked.connect(lambda: self.interval_spinbox.setValue(120))
        preset_layout.addWidget(preset_120)
        
        preset_300 = QPushButton(self.tr("5m"))
        preset_300.clicked.connect(lambda: self.interval_spinbox.setValue(300))
        preset_layout.addWidget(preset_300)
        
        interval_layout.addRow(self.tr("Presets:"), preset_layout)
        
        layout.addWidget(interval_group)
        
        # Warning label
        warning_label = QLabel(self.tr("⚠️  Shorter intervals may impact performance on large projects."))
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("color: #d97706; font-size: 10px; padding: 5px;")
        layout.addWidget(warning_label)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def on_enable_toggled(self, checked: bool):
        """Handle enable checkbox toggle"""
        self.interval_spinbox.setEnabled(checked)
    
    def get_settings(self):
        """Get the configured settings"""
        return (
            self.enable_checkbox.isChecked(),
            self.interval_spinbox.value()
        )