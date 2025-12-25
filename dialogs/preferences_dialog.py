#!/usr/bin/env python3
"""
Preferences Dialog for PyGameMaker IDE
Comprehensive settings dialog with multiple tabs
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QSpinBox, QGroupBox, QFormLayout,
                               QComboBox, QDialogButtonBox, QTabWidget, QWidget,
                               QCheckBox, QDoubleSpinBox, QLineEdit, QFileDialog,
                               QMessageBox)
from PySide6.QtGui import QFont
from utils.config import Config


class PreferencesDialog(QDialog):
    """Comprehensive preferences dialog with multiple setting categories"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Preferences"))
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.setup_ui()
        self.load_current_settings()
        self.connect_signals()
    
    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.create_appearance_tab()
        self.create_editor_tab()
        self.create_project_tab()
        self.create_advanced_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Info label
        info_label = QLabel(self.tr("Note: Some settings require restarting the IDE to take effect."))
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        main_layout.addWidget(info_label)
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        main_layout.addWidget(self.button_box)
    
    def create_appearance_tab(self):
        """Create the Appearance settings tab"""
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        
        # Font Settings Group
        font_group = QGroupBox(self.tr("Font Settings"))
        font_form = QFormLayout(font_group)
        
        # Font size
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 24)
        self.size_spin.setSuffix(" pt")
        font_form.addRow(self.tr("Font Size:"), self.size_spin)
        
        # Font family
        self.family_combo = QComboBox()
        self.family_combo.addItems([
            self.tr("System Default"),
            "Segoe UI", "Arial", "Ubuntu", "Helvetica", "SF Pro Text", "Roboto"
        ])
        font_form.addRow(self.tr("Font Family:"), self.family_combo)
        
        # Preview
        self.preview_label = QLabel(self.tr("Preview: The quick brown fox jumps over the lazy dog"))
        self.preview_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; background: white;")
        font_form.addRow(self.tr("Preview:"), self.preview_label)
        
        appearance_layout.addWidget(font_group)
        
        # Theme Settings Group
        theme_group = QGroupBox(self.tr("Theme Settings"))
        theme_form = QFormLayout(theme_group)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Default", "Dark", "Light"])
        theme_form.addRow(self.tr("Theme:"), self.theme_combo)
        
        # UI Scale
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.5, 2.0)
        self.scale_spin.setSingleStep(0.1)
        self.scale_spin.setSuffix("x")
        theme_form.addRow(self.tr("UI Scale:"), self.scale_spin)
        
        # Show tooltips
        self.tooltips_check = QCheckBox(self.tr("Show tooltips"))
        theme_form.addRow("", self.tooltips_check)
        
        appearance_layout.addWidget(theme_group)
        appearance_layout.addStretch()
        
        self.tabs.addTab(appearance_tab, self.tr("Appearance"))
    
    def create_editor_tab(self):
        """Create the Editor settings tab"""
        editor_tab = QWidget()
        editor_layout = QVBoxLayout(editor_tab)
        
        # Auto-Save Settings
        autosave_group = QGroupBox(self.tr("Auto-Save Settings"))
        autosave_form = QFormLayout(autosave_group)
        
        self.autosave_enabled = QCheckBox(self.tr("Enable auto-save"))
        autosave_form.addRow("", self.autosave_enabled)
        
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 30)
        self.autosave_interval.setSuffix(self.tr(" minutes"))
        autosave_form.addRow(self.tr("Auto-save interval:"), self.autosave_interval)
        
        editor_layout.addWidget(autosave_group)
        
        # Grid Settings
        grid_group = QGroupBox(self.tr("Grid & Snapping"))
        grid_form = QFormLayout(grid_group)
        
        self.show_grid = QCheckBox(self.tr("Show grid in editors"))
        grid_form.addRow("", self.show_grid)
        
        self.grid_size = QSpinBox()
        self.grid_size.setRange(8, 128)
        self.grid_size.setSuffix(" px")
        grid_form.addRow(self.tr("Grid size:"), self.grid_size)
        
        self.snap_to_grid = QCheckBox(self.tr("Snap to grid"))
        grid_form.addRow("", self.snap_to_grid)
        
        self.show_collision = QCheckBox(self.tr("Show collision boxes"))
        grid_form.addRow("", self.show_collision)
        
        editor_layout.addWidget(grid_group)
        editor_layout.addStretch()
        
        self.tabs.addTab(editor_tab, self.tr("Editor"))
    
    def create_project_tab(self):
        """Create the Project settings tab"""
        project_tab = QWidget()
        project_layout = QVBoxLayout(project_tab)
        
        # Project Paths
        paths_group = QGroupBox(self.tr("Project Paths"))
        paths_form = QFormLayout(paths_group)
        
        projects_dir_layout = QHBoxLayout()
        self.projects_dir_edit = QLineEdit()
        self.projects_dir_edit.setMinimumWidth(300)
        self.projects_dir_btn = QPushButton(self.tr("Browse..."))
        projects_dir_layout.addWidget(self.projects_dir_edit)
        projects_dir_layout.addWidget(self.projects_dir_btn)
        
        paths_form.addRow(self.tr("Default projects folder:"), projects_dir_layout)
        
        project_layout.addWidget(paths_group)
        
        # Project Settings
        project_settings_group = QGroupBox(self.tr("Project Settings"))
        project_settings_form = QFormLayout(project_settings_group)
        
        self.recent_limit = QSpinBox()
        self.recent_limit.setRange(5, 50)
        project_settings_form.addRow(self.tr("Recent projects limit:"), self.recent_limit)
        
        self.create_backup = QCheckBox(self.tr("Create backup on save"))
        project_settings_form.addRow("", self.create_backup)
        
        project_layout.addWidget(project_settings_group)
        project_layout.addStretch()
        
        self.tabs.addTab(project_tab, self.tr("Project"))
    
    def create_advanced_tab(self):
        """Create the Advanced settings tab"""
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # Debug Settings
        debug_group = QGroupBox(self.tr("Debug Settings"))
        debug_form = QFormLayout(debug_group)
        
        self.debug_mode = QCheckBox(self.tr("Enable debug mode"))
        debug_form.addRow("", self.debug_mode)
        
        self.console_output = QCheckBox(self.tr("Show console output"))
        debug_form.addRow("", self.console_output)
        
        advanced_layout.addWidget(debug_group)
        
        # Performance Settings
        perf_group = QGroupBox(self.tr("Performance"))
        perf_form = QFormLayout(perf_group)
        
        self.max_undo = QSpinBox()
        self.max_undo.setRange(10, 200)
        perf_form.addRow(self.tr("Maximum undo steps:"), self.max_undo)
        
        advanced_layout.addWidget(perf_group)
        advanced_layout.addStretch()
        
        self.tabs.addTab(advanced_tab, self.tr("Advanced"))
    
    def load_current_settings(self):
        """Load current settings from config"""
        # Font settings
        font_config = Config.get_font_config()
        self.size_spin.setValue(font_config['size'])
        
        current_family = font_config.get('family', '')
        if current_family:
            index = self.family_combo.findText(current_family)
            if index >= 0:
                self.family_combo.setCurrentIndex(index)
        
        # Appearance settings
        appearance_config = Config.get_appearance_config()
        self.theme_combo.setCurrentText(appearance_config['theme'].title())
        self.scale_spin.setValue(appearance_config['ui_scale'])
        self.tooltips_check.setChecked(appearance_config['show_tooltips'])
        
        # Editor settings
        editor_config = Config.get_editor_config()
        self.autosave_enabled.setChecked(editor_config['auto_save_enabled'])
        self.autosave_interval.setValue(editor_config['auto_save_interval'])
        self.autosave_interval.setEnabled(editor_config['auto_save_enabled'])
        self.show_grid.setChecked(editor_config['show_grid'])
        self.grid_size.setValue(editor_config['grid_size'])
        self.snap_to_grid.setChecked(editor_config['snap_to_grid'])
        self.show_collision.setChecked(editor_config['show_collision_boxes'])
        
        # Project settings
        project_config = Config.get_project_config()
        self.projects_dir_edit.setText(project_config['default_projects_dir'])
        self.recent_limit.setValue(project_config['recent_projects_limit'])
        self.create_backup.setChecked(project_config['create_backup_on_save'])
        
        # Advanced settings
        advanced_config = Config.get_advanced_config()
        self.debug_mode.setChecked(advanced_config['debug_mode'])
        self.max_undo.setValue(advanced_config['max_undo_steps'])
        self.console_output.setChecked(advanced_config['console_output'])
        
        # Update font preview
        self.update_font_preview()
    
    def connect_signals(self):
        """Connect all signals"""
        # Font preview updates
        self.size_spin.valueChanged.connect(self.update_font_preview)
        self.family_combo.currentIndexChanged.connect(self.update_font_preview)
        
        # Auto-save enable/disable
        self.autosave_enabled.toggled.connect(self.autosave_interval.setEnabled)
        
        # Browse button
        self.projects_dir_btn.clicked.connect(self.browse_projects_dir)
        
        # Dialog buttons
        self.button_box.button(QDialogButtonBox.Ok).clicked.connect(self.accept_settings)
        self.button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
    
    def update_font_preview(self):
        """Update the font preview label"""
        preview_font = QFont()
        if self.family_combo.currentIndex() > 0:
            preview_font.setFamily(self.family_combo.currentText())
        preview_font.setPointSize(self.size_spin.value())
        self.preview_label.setFont(preview_font)
    
    def browse_projects_dir(self):
        """Browse for default projects directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Default Projects Directory"),
            self.projects_dir_edit.text()
        )
        if directory:
            self.projects_dir_edit.setText(directory)
    
    def apply_settings(self):
        """Apply all settings without closing"""
        # Font settings
        font_family = None if self.family_combo.currentIndex() == 0 else self.family_combo.currentText()
        Config.set_font_config(family=font_family, size=self.size_spin.value())
        
        # Appearance settings
        Config.set_appearance_config(
            theme=self.theme_combo.currentText().lower(),
            ui_scale=self.scale_spin.value(),
            show_tooltips=self.tooltips_check.isChecked()
        )
        
        # Apply theme immediately
        from utils.theme_manager import ThemeManager
        ThemeManager.apply_theme(self.theme_combo.currentText().lower())
        
        # Editor settings
        Config.set_editor_config(
            auto_save_enabled=self.autosave_enabled.isChecked(),
            auto_save_interval=self.autosave_interval.value(),
            show_grid=self.show_grid.isChecked(),
            grid_size=self.grid_size.value(),
            snap_to_grid=self.snap_to_grid.isChecked(),
            show_collision_boxes=self.show_collision.isChecked()
        )
        
        # Project settings
        Config.set_project_config(
            default_projects_dir=self.projects_dir_edit.text(),
            recent_projects_limit=self.recent_limit.value(),
            create_backup_on_save=self.create_backup.isChecked()
        )
        
        # Advanced settings
        Config.set_advanced_config(
            debug_mode=self.debug_mode.isChecked(),
            max_undo_steps=self.max_undo.value(),
            console_output=self.console_output.isChecked()
        )
        
        QMessageBox.information(
            self,
            self.tr("Settings Saved"),
            self.tr("Settings have been saved successfully.\n\n"
                   "Some changes may require restarting the IDE to take effect.")
        )
    
    def accept_settings(self):
        """Save settings and close"""
        self.apply_settings()
        self.accept()
