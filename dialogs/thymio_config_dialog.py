#!/usr/bin/env python3
"""
Thymio Configuration Dialog
Allows users to customize which Thymio blocks are available.
This is a separate window from the standard BlocklyConfigDialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

from config.blockly_config import (
    BlocklyConfig, BLOCK_REGISTRY, PRESETS, save_config, load_config,
    BLOCK_DEPENDENCIES, is_block_implemented
)
from config.blockly_translations import (
    get_translated_category,
    get_translated_block_name,
    get_translated_block_description
)


# Thymio-specific categories
THYMIO_CATEGORIES = {
    "Thymio Events",
    "Thymio Motors",
    "Thymio LEDs",
    "Thymio Sound",
    "Thymio Sensors",
    "Thymio Conditions",
    "Thymio Timers",
    "Thymio Variables",
}

# Category colors for Thymio
THYMIO_CATEGORY_COLORS = {
    "Thymio Events": "#FFD500",
    "Thymio Motors": "#5C81A6",
    "Thymio LEDs": "#9B59B6",
    "Thymio Sound": "#9966FF",
    "Thymio Sensors": "#5CA65C",
    "Thymio Conditions": "#E67E22",  # Orange for conditionals
    "Thymio Timers": "#FF6B6B",
    "Thymio Variables": "#A6745C",
}


class ThymioConfigDialog(QDialog):
    """Dialog for configuring available Thymio blocks"""

    config_changed = Signal(BlocklyConfig)

    def __init__(self, parent=None, current_config: BlocklyConfig = None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Configure Thymio Events & Actions"))
        self.resize(600, 500)

        # Current configuration
        self.config = current_config or load_config()
        self.original_config = BlocklyConfig.from_dict(self.config.to_dict())  # Deep copy

        # Detect current language from parent or system
        self.language = self._detect_language()

        self.setup_ui()
        self.load_config_to_ui()

    def _detect_language(self) -> str:
        """Detect current IDE language setting"""
        from core.language_manager import get_language_manager

        language_manager = get_language_manager()
        current_lang = language_manager.get_current_language()

        return current_lang if current_lang else 'en'

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)

        # ====== Preset Selection ======
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel(self.tr("Preset:")))

        self.preset_combo = QComboBox()
        self.preset_combo.blockSignals(True)
        self.preset_combo.addItems([
            self.tr("Thymio Full (All Thymio Blocks)"),
            self.tr("Thymio Basic (Buttons + Motors)"),
            self.tr("Thymio Sensors"),
            self.tr("Custom")
        ])
        self.preset_combo.blockSignals(False)
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(self.preset_combo)

        preset_layout.addStretch()

        # Info label
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #666; font-style: italic;")
        preset_layout.addWidget(self.info_label)

        layout.addLayout(preset_layout)

        # ====== Block Tree ======
        tree_label = QLabel(self.tr("Select Thymio blocks to enable:"))
        tree_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(tree_label)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([self.tr("Block"), self.tr("Description")])
        self.tree.setColumnWidth(0, 250)
        self.tree.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.tree)

        # ====== Warning Label ======
        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        self.warning_label.setWordWrap(True)
        self.warning_label.setVisible(False)
        layout.addWidget(self.warning_label)

        # Populate tree AFTER warning_label is created
        self.populate_tree()

        # ====== Button Bar ======
        button_layout = QHBoxLayout()

        self.select_all_btn = QPushButton(self.tr("Select All"))
        self.select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(self.select_all_btn)

        self.select_none_btn = QPushButton(self.tr("Select None"))
        self.select_none_btn.clicked.connect(self.select_none)
        button_layout.addWidget(self.select_none_btn)

        button_layout.addStretch()

        self.save_btn = QPushButton(self.tr("Save"))
        self.save_btn.clicked.connect(self.save_and_close)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton(self.tr("Cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def populate_tree(self):
        """Populate the tree widget with Thymio categories and blocks only"""
        self.tree.blockSignals(True)

        self.tree.clear()
        self.category_items = {}
        self.block_items = {}

        for category, blocks in BLOCK_REGISTRY.items():
            # Only show Thymio categories
            if category not in THYMIO_CATEGORIES:
                continue

            # Translate category name
            translated_category = get_translated_category(category, self.language)
            if not translated_category:
                translated_category = category

            # Create category item
            category_item = QTreeWidgetItem(self.tree, [translated_category, self.tr("{0} blocks").format(len(blocks))])
            category_item.setFlags(category_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
            category_item.setCheckState(0, Qt.Unchecked)
            category_item.setData(0, Qt.UserRole, category)
            category_item.setExpanded(True)

            # Set category colors
            if category in THYMIO_CATEGORY_COLORS:
                color_hex = THYMIO_CATEGORY_COLORS[category]
                color = QColor(color_hex)
                category_item.setBackground(0, QBrush(color))
                category_item.setForeground(0, QBrush(Qt.white if self._is_dark_color(color_hex) else Qt.black))

            self.category_items[category] = category_item

            # Add block items
            for block in blocks:
                # Translate block name and description
                translated_name = get_translated_block_name(block["type"], self.language)
                translated_desc = get_translated_block_description(block["type"], self.language)

                display_name = translated_name if translated_name else block["name"]
                display_desc = translated_desc if translated_desc else block["description"]

                # Check if block is implemented
                implemented = is_block_implemented(block["type"])

                if not implemented:
                    display_name = f"⚠ {display_name}"
                    display_desc = self.tr("[Not implemented] {0}").format(display_desc)

                block_item = QTreeWidgetItem(category_item, [display_name, display_desc])
                block_item.setFlags(block_item.flags() | Qt.ItemIsUserCheckable)
                block_item.setCheckState(0, Qt.Unchecked)
                block_item.setData(0, Qt.UserRole, block["type"])

                if not implemented:
                    block_item.setForeground(0, QBrush(QColor("#888888")))
                    block_item.setForeground(1, QBrush(QColor("#888888")))

                if block["type"] in BLOCK_DEPENDENCIES:
                    deps = BLOCK_DEPENDENCIES[block["type"]]
                    dep_names = [self._get_block_name(d) for d in deps]
                    block_item.setToolTip(0, self.tr("Requires: {0}").format(', '.join(dep_names)))
                    block_item.setToolTip(1, block["description"] + "\n" + self.tr("Requires: {0}").format(', '.join(dep_names)))

                self.block_items[block["type"]] = block_item

        self.tree.blockSignals(False)

    def _is_dark_color(self, hex_color: str) -> bool:
        """Check if a hex color is dark (for text contrast)"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness < 128

    def _get_block_name(self, block_type: str) -> str:
        """Get human-readable name for a block type"""
        for blocks in BLOCK_REGISTRY.values():
            for block in blocks:
                if block["type"] == block_type:
                    return block["name"]
        return block_type

    def load_config_to_ui(self):
        """Load current configuration into UI"""
        self.tree.blockSignals(True)
        self.preset_combo.blockSignals(True)

        # Set checkboxes based on config
        for block_type, item in self.block_items.items():
            checked = self.config.is_block_enabled(block_type)
            item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)

        # Update preset combo based on config
        # Check if it matches a known Thymio preset
        if self._is_thymio_full():
            self.preset_combo.setCurrentIndex(0)
        elif self._is_thymio_basic():
            self.preset_combo.setCurrentIndex(1)
        elif self._is_thymio_sensors():
            self.preset_combo.setCurrentIndex(2)
        else:
            self.preset_combo.setCurrentIndex(3)  # Custom

        self.tree.blockSignals(False)
        self.preset_combo.blockSignals(False)

        self.update_info_label()
        self.check_dependencies()

    def _is_thymio_full(self) -> bool:
        """Check if all Thymio blocks are enabled"""
        for category in THYMIO_CATEGORIES:
            if category in BLOCK_REGISTRY:
                for block in BLOCK_REGISTRY[category]:
                    if not self.config.is_block_enabled(block["type"]):
                        return False
        return True

    def _is_thymio_basic(self) -> bool:
        """Check if only basic Thymio blocks are enabled"""
        # Basic = Thymio Events (buttons only) + Thymio Motors
        basic_categories = {"Thymio Events", "Thymio Motors"}
        for category in THYMIO_CATEGORIES:
            if category in BLOCK_REGISTRY:
                for block in BLOCK_REGISTRY[category]:
                    is_enabled = self.config.is_block_enabled(block["type"])
                    should_be_enabled = category in basic_categories
                    if is_enabled != should_be_enabled:
                        return False
        return True

    def _is_thymio_sensors(self) -> bool:
        """Check if Thymio sensor-focused blocks are enabled"""
        sensor_categories = {"Thymio Events", "Thymio Sensors", "Thymio Conditions", "Thymio Motors"}
        for category in THYMIO_CATEGORIES:
            if category in BLOCK_REGISTRY:
                for block in BLOCK_REGISTRY[category]:
                    is_enabled = self.config.is_block_enabled(block["type"])
                    should_be_enabled = category in sensor_categories
                    if is_enabled != should_be_enabled:
                        return False
        return True

    def on_preset_changed(self, text: str):
        """Handle preset selection"""
        if text == self.tr("Thymio Full (All Thymio Blocks)"):
            self._apply_thymio_full()
        elif text == self.tr("Thymio Basic (Buttons + Motors)"):
            self._apply_thymio_basic()
        elif text == self.tr("Thymio Sensors"):
            self._apply_thymio_sensors()
        elif text == self.tr("Custom"):
            pass  # Don't change anything

        self.load_config_to_ui()

    def _apply_thymio_full(self):
        """Enable all Thymio blocks"""
        for category in THYMIO_CATEGORIES:
            self.config.enable_category(category)

    def _apply_thymio_basic(self):
        """Enable only basic Thymio blocks (buttons + motors)"""
        for category in THYMIO_CATEGORIES:
            if category in {"Thymio Events", "Thymio Motors"}:
                self.config.enable_category(category)
            else:
                self.config.disable_category(category)

    def _apply_thymio_sensors(self):
        """Enable Thymio sensor-focused blocks"""
        for category in THYMIO_CATEGORIES:
            if category in {"Thymio Events", "Thymio Sensors", "Thymio Conditions", "Thymio Motors"}:
                self.config.enable_category(category)
            else:
                self.config.disable_category(category)

    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle checkbox state changes"""
        if column != 0:
            return

        block_type = item.data(0, Qt.UserRole)
        if not block_type:
            return

        is_checked = item.checkState(0) == Qt.Checked

        # Check if it's a category
        if block_type in BLOCK_REGISTRY:
            if is_checked:
                self.config.enable_category(block_type)
            else:
                self.config.disable_category(block_type)
        else:
            if is_checked:
                self.config.enable_block(block_type)
            else:
                self.config.disable_block(block_type)

        # Mark as custom if user manually changed something
        if not self.tree.signalsBlocked() and self.preset_combo.currentIndex() != 3:
            self.tree.blockSignals(True)
            self.preset_combo.setCurrentIndex(3)  # Custom
            self.tree.blockSignals(False)

        self.update_info_label()
        self.check_dependencies()

    def check_dependencies(self):
        """Check for missing dependencies and show warning"""
        # Filter to only Thymio-related dependencies
        missing = {}
        for block_type in self.config.enabled_blocks:
            if block_type in BLOCK_DEPENDENCIES:
                # Only check if this is a Thymio block
                is_thymio_block = any(
                    any(b["type"] == block_type for b in BLOCK_REGISTRY.get(cat, []))
                    for cat in THYMIO_CATEGORIES
                )
                if is_thymio_block:
                    deps = BLOCK_DEPENDENCIES[block_type]
                    missing_deps = [dep for dep in deps if dep not in self.config.enabled_blocks]
                    if missing_deps:
                        missing[block_type] = missing_deps

        if missing:
            warnings = []
            for block_type, deps in missing.items():
                block_name = self._get_block_name(block_type)
                dep_names = [self._get_block_name(d) for d in deps]
                warnings.append(f"• {block_name} requires: {', '.join(dep_names)}")

            self.warning_label.setText(
                self.tr("⚠️ Warning: Some blocks are missing dependencies:\n{0}").format("\n".join(warnings))
            )
            self.warning_label.setVisible(True)
        else:
            self.warning_label.setVisible(False)

    def update_info_label(self):
        """Update the info label with Thymio block count"""
        # Count only Thymio blocks
        thymio_blocks = 0
        for category in THYMIO_CATEGORIES:
            if category in BLOCK_REGISTRY:
                for block in BLOCK_REGISTRY[category]:
                    if block["type"] in self.config.enabled_blocks:
                        thymio_blocks += 1

        thymio_categories = sum(1 for cat in THYMIO_CATEGORIES if cat in self.config.enabled_categories)
        self.info_label.setText(self.tr("{0} Thymio blocks, {1} categories").format(thymio_blocks, thymio_categories))

    def select_all(self):
        """Select all Thymio blocks"""
        self._apply_thymio_full()
        self.load_config_to_ui()

    def select_none(self):
        """Deselect all Thymio blocks"""
        for category in THYMIO_CATEGORIES:
            self.config.disable_category(category)
        self.load_config_to_ui()

    def save_and_close(self):
        """Save configuration and close dialog"""
        # Check for dependency issues (Thymio-only)
        missing = {}
        for block_type in self.config.enabled_blocks:
            if block_type in BLOCK_DEPENDENCIES:
                is_thymio_block = any(
                    any(b["type"] == block_type for b in BLOCK_REGISTRY.get(cat, []))
                    for cat in THYMIO_CATEGORIES
                )
                if is_thymio_block:
                    deps = BLOCK_DEPENDENCIES[block_type]
                    missing_deps = [dep for dep in deps if dep not in self.config.enabled_blocks]
                    if missing_deps:
                        missing[block_type] = missing_deps

        if missing:
            response = QMessageBox.warning(
                self,
                self.tr("Missing Dependencies"),
                self.tr("Some enabled Thymio blocks are missing their dependencies. "
                "The blocks may not work correctly.\n\n"
                "Do you want to save anyway?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if response == QMessageBox.No:
                return

        # Save to file
        save_config(self.config)

        # Emit signal
        self.config_changed.emit(self.config)

        # Close dialog
        self.accept()

    def get_config(self) -> BlocklyConfig:
        """Get the current configuration"""
        return self.config
