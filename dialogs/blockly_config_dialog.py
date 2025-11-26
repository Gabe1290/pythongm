#!/usr/bin/env python3
"""
Blockly Configuration Dialog
Allows users to customize which blocks are available
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QComboBox, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

from config.blockly_config import (
    BlocklyConfig, BLOCK_REGISTRY, PRESETS, save_config, load_config,
    BLOCK_DEPENDENCIES
)


class BlocklyConfigDialog(QDialog):
    """Dialog for configuring available Blockly blocks"""

    config_changed = Signal(BlocklyConfig)

    def __init__(self, parent=None, current_config: BlocklyConfig = None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Configure Blockly Blocks"))
        self.resize(700, 600)

        # Current configuration
        self.config = current_config or load_config()
        self.original_config = BlocklyConfig.from_dict(self.config.to_dict())  # Deep copy

        self.setup_ui()
        self.load_config_to_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)

        # ====== Preset Selection ======
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel(self.tr("Preset:")))

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            self.tr("Full (All Blocks)"),
            self.tr("Beginner (Basic Blocks)"),
            self.tr("Intermediate (More Features)"),
            self.tr("Platformer Game"),
            self.tr("Grid-based RPG"),
            self.tr("Custom")
        ])
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(self.preset_combo)

        preset_layout.addStretch()

        # Info label
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #666; font-style: italic;")
        preset_layout.addWidget(self.info_label)

        layout.addLayout(preset_layout)

        # ====== Block Tree ======
        tree_label = QLabel(self.tr("Select blocks to enable:"))
        tree_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(tree_label)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([self.tr("Block"), self.tr("Description")])
        self.tree.setColumnWidth(0, 300)
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
        """Populate the tree widget with categories and blocks"""
        self.tree.clear()
        self.category_items = {}
        self.block_items = {}

        for category, blocks in BLOCK_REGISTRY.items():
            # Create category item
            category_item = QTreeWidgetItem(self.tree, [category, self.tr("{0} blocks").format(len(blocks))])
            category_item.setFlags(category_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
            category_item.setCheckState(0, Qt.Unchecked)
            category_item.setData(0, Qt.UserRole, category)
            category_item.setExpanded(True)

            # Set category colors based on Blockly colors
            category_colors = {
                "Events": "#FFD500",
                "Movement": "#5C81A6",
                "Timing": "#FF6B6B",
                "Drawing": "#9B59B6",
                "Score/Lives/Health": "#5CA65C",
                "Instance": "#A65C81",
                "Room": "#A6745C",
                "Values": "#5C68A6",
                "Sound": "#9966FF",
                "Output": "#745CA6",
            }
            if category in category_colors:
                color_hex = category_colors[category]
                color = QColor(color_hex)
                category_item.setBackground(0, QBrush(color))
                category_item.setForeground(0, QBrush(Qt.white if self._is_dark_color(color_hex) else Qt.black))

            self.category_items[category] = category_item

            # Add block items
            for block in blocks:
                block_item = QTreeWidgetItem(category_item, [block["name"], block["description"]])
                block_item.setFlags(block_item.flags() | Qt.ItemIsUserCheckable)
                block_item.setCheckState(0, Qt.Unchecked)
                block_item.setData(0, Qt.UserRole, block["type"])

                # Show dependencies as tooltip
                if block["type"] in BLOCK_DEPENDENCIES:
                    deps = BLOCK_DEPENDENCIES[block["type"]]
                    dep_names = [self._get_block_name(d) for d in deps]
                    block_item.setToolTip(0, self.tr("Requires: {0}").format(', '.join(dep_names)))
                    block_item.setToolTip(1, block["description"] + "\n" + self.tr("Requires: {0}").format(', '.join(dep_names)))

                self.block_items[block["type"]] = block_item

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
        # Block signals during loading
        self.tree.blockSignals(True)

        # Set checkboxes based on config
        for block_type, item in self.block_items.items():
            checked = self.config.is_block_enabled(block_type)
            item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)

        # Update preset combo
        preset_index = {
            "full": 0,
            "beginner": 1,
            "intermediate": 2,
            "platformer": 3,
            "grid_rpg": 4,
        }.get(self.config.preset_name, 5)  # 5 = Custom
        self.preset_combo.setCurrentIndex(preset_index)

        self.tree.blockSignals(False)

        # Update info
        self.update_info_label()
        self.check_dependencies()

    def on_preset_changed(self, text: str):
        """Handle preset selection"""
        preset_map = {
            self.tr("Full (All Blocks)"): "full",
            self.tr("Beginner (Basic Blocks)"): "beginner",
            self.tr("Intermediate (More Features)"): "intermediate",
            self.tr("Platformer Game"): "platformer",
            self.tr("Grid-based RPG"): "grid_rpg",
        }

        if text == self.tr("Custom"):
            # Don't change config, just mark as custom
            self.config.preset_name = "custom"
            return

        preset_key = preset_map.get(text)
        if preset_key and preset_key in PRESETS:
            self.config = PRESETS[preset_key]
            self.load_config_to_ui()

    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle checkbox state changes"""
        if column != 0:
            return

        block_type = item.data(0, Qt.UserRole)
        if not block_type:
            return

        # Update config
        is_checked = item.checkState(0) == Qt.Checked

        # Check if it's a category
        if block_type in BLOCK_REGISTRY:
            # Category toggled
            if is_checked:
                self.config.enable_category(block_type)
            else:
                self.config.disable_category(block_type)
        else:
            # Individual block toggled
            if is_checked:
                self.config.enable_block(block_type)
            else:
                self.config.disable_block(block_type)

        # Mark as custom
        if self.preset_combo.currentIndex() != 5:
            self.tree.blockSignals(True)
            self.preset_combo.setCurrentIndex(5)  # Custom
            self.config.preset_name = "custom"
            self.tree.blockSignals(False)

        self.update_info_label()
        self.check_dependencies()

    def check_dependencies(self):
        """Check for missing dependencies and show warning"""
        missing = self.config.get_missing_dependencies()

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
        """Update the info label with block count"""
        total_blocks = len(self.config.enabled_blocks)
        total_categories = len(self.config.enabled_categories)
        self.info_label.setText(self.tr("{0} blocks, {1} categories").format(total_blocks, total_categories))

    def select_all(self):
        """Select all blocks"""
        self.config = BlocklyConfig.get_full()
        self.load_config_to_ui()

    def select_none(self):
        """Deselect all blocks"""
        self.config = BlocklyConfig(preset_name="custom")
        self.load_config_to_ui()

    def save_and_close(self):
        """Save configuration and close dialog"""
        # Check for dependency issues
        missing = self.config.get_missing_dependencies()
        if missing:
            response = QMessageBox.warning(
                self,
                self.tr("Missing Dependencies"),
                self.tr("Some enabled blocks are missing their dependencies. "
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
