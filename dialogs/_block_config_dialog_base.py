#!/usr/bin/env python3
"""
Shared base for the Blockly/Thymio block-configuration dialogs.

`BlocklyConfigDialog` and `ThymioConfigDialog` were structural clones — same
preset combo / category tree / dependency-warning / save scaffold, differing
only in which categories they show, their preset list, and how they count and
detect presets. This base holds the verified-identical behaviour; the two
dialogs subclass it and override only the genuinely divergent template hooks.

Translation note: `QObject.tr()` resolves its context from the *concrete*
runtime class (empirically verified for PySide6 6.9), so a `BlocklyConfigDialog`
/ `ThymioConfigDialog` instance still looks strings up under its own context
even though the `tr()` calls now live here — the existing .qm files keep
working unchanged. Divergent strings deliberately stay lexically inside the
subclass hooks so a future manual `lupdate` keeps them under the right context;
the shared strings move here (the project ships .ts/.qm by hand and runs no
`lupdate`, so no automated re-extraction reassigns the context).
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

from config.blockly_config import (
    BlocklyConfig, BLOCK_REGISTRY, save_config, load_config,
    BLOCK_DEPENDENCIES, is_block_implemented
)
from config.blockly_translations import (
    get_translated_category,
    get_translated_block_name,
    get_translated_block_description
)


# Thymio categories — Blockly excludes these, Thymio shows only these.
# Single-sourced here; both dialog modules re-export it for compatibility.
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


class BaseBlockConfigDialog(QDialog):
    """Common scaffold for the block-configuration dialogs.

    Subclasses must provide the template hooks marked NotImplementedError.
    """

    config_changed = Signal(BlocklyConfig)

    #: Combo index that represents the "Custom" preset (subclass overrides).
    CUSTOM_PRESET_INDEX = 0

    def __init__(self, parent=None, current_config: BlocklyConfig = None):
        super().__init__(parent)
        self.setWindowTitle(self._window_title())
        self.resize(*self._window_size())

        # Current configuration
        self.config = current_config or load_config()
        self.original_config = BlocklyConfig.from_dict(self.config.to_dict())  # Deep copy

        # Detect current language from parent or system
        self.language = self._detect_language()

        self.setup_ui()
        self.load_config_to_ui()

    # ------------------------------------------------------------------ #
    # Template hooks — subclasses override these                          #
    # ------------------------------------------------------------------ #
    def _window_title(self) -> str:
        raise NotImplementedError

    def _window_size(self) -> tuple:
        raise NotImplementedError

    def _preset_items(self) -> list:
        raise NotImplementedError

    def _tree_label_text(self) -> str:
        raise NotImplementedError

    def _tree_column0_width(self) -> int:
        raise NotImplementedError

    def _include_category(self, category: str) -> bool:
        raise NotImplementedError

    def _category_color(self, category: str):
        """Return a hex colour for the category header, or None."""
        raise NotImplementedError

    def _current_preset_index(self) -> int:
        raise NotImplementedError

    def _get_missing_dependencies(self) -> dict:
        raise NotImplementedError

    def _missing_dependencies_message(self) -> str:
        raise NotImplementedError

    def _on_revert_to_custom(self):
        """Hook: extra config state to apply when the combo reverts to Custom."""
        pass

    def update_info_label(self):
        raise NotImplementedError

    def on_preset_changed(self, text: str):
        raise NotImplementedError

    def select_all(self):
        raise NotImplementedError

    def select_none(self):
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Shared behaviour                                                    #
    # ------------------------------------------------------------------ #
    def _detect_language(self) -> str:
        """Detect current IDE language setting"""
        # Get language from the global language manager
        from core.language_manager import get_language_manager

        language_manager = get_language_manager()
        current_lang = language_manager.get_current_language()

        # Return the current language (defaults to 'en' if not set)
        return current_lang if current_lang else 'en'

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)

        # ====== Preset Selection ======
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel(self.tr("Preset:")))

        self.preset_combo = QComboBox()
        # Block signals while adding items to prevent triggering on_preset_changed
        self.preset_combo.blockSignals(True)
        self.preset_combo.addItems(self._preset_items())
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
        tree_label = QLabel(self._tree_label_text())
        tree_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(tree_label)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([self.tr("Block"), self.tr("Description")])
        self.tree.setColumnWidth(0, self._tree_column0_width())
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
        """Populate the tree widget with the categories/blocks this dialog shows"""
        # Block signals while populating to prevent on_item_changed from being triggered
        self.tree.blockSignals(True)

        self.tree.clear()
        self.category_items = {}
        self.block_items = {}

        for category, blocks in BLOCK_REGISTRY.items():
            if not self._include_category(category):
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
            color_hex = self._category_color(category)
            if color_hex:
                color = QColor(color_hex)
                category_item.setBackground(0, QBrush(color))
                category_item.setForeground(0, QBrush(Qt.white if self._is_dark_color(color_hex) else Qt.black))

            self.category_items[category] = category_item

            # Add block items
            for block in blocks:
                # Translate block name and description
                translated_name = get_translated_block_name(block["type"], self.language)
                translated_desc = get_translated_block_description(block["type"], self.language)

                # Fall back to English if translation not available
                display_name = translated_name if translated_name else block["name"]
                display_desc = translated_desc if translated_desc else block["description"]

                # Check if block is implemented
                implemented = is_block_implemented(block["type"])

                # Add marker for unimplemented blocks
                if not implemented:
                    display_name = f"⚠ {display_name}"
                    display_desc = self.tr("[Not implemented] {0}").format(display_desc)

                block_item = QTreeWidgetItem(category_item, [display_name, display_desc])
                block_item.setFlags(block_item.flags() | Qt.ItemIsUserCheckable)
                block_item.setCheckState(0, Qt.Unchecked)
                block_item.setData(0, Qt.UserRole, block["type"])

                # Style unimplemented blocks with gray/italic
                if not implemented:
                    block_item.setForeground(0, QBrush(QColor("#888888")))
                    block_item.setForeground(1, QBrush(QColor("#888888")))

                # Show dependencies as tooltip
                if block["type"] in BLOCK_DEPENDENCIES:
                    deps = BLOCK_DEPENDENCIES[block["type"]]
                    dep_names = [self._get_block_name(d) for d in deps]
                    block_item.setToolTip(0, self.tr("Requires: {0}").format(', '.join(dep_names)))
                    block_item.setToolTip(1, block["description"] + "\n" + self.tr("Requires: {0}").format(', '.join(dep_names)))

                self.block_items[block["type"]] = block_item

        # Unblock signals after populating
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
        # Block signals during loading
        self.tree.blockSignals(True)
        self.preset_combo.blockSignals(True)

        # Set checkboxes based on config
        for block_type, item in self.block_items.items():
            checked = self.config.is_block_enabled(block_type)
            item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)

        self.preset_combo.setCurrentIndex(self._current_preset_index())

        self.tree.blockSignals(False)
        self.preset_combo.blockSignals(False)

        # Update info
        self.update_info_label()
        self.check_dependencies()

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

        # Mark as custom ONLY if user manually changed something (not during load)
        # Check if tree signals are blocked - if so, we're loading, not user action
        if not self.tree.signalsBlocked() and self.preset_combo.currentIndex() != self.CUSTOM_PRESET_INDEX:
            self.tree.blockSignals(True)
            self.preset_combo.setCurrentIndex(self.CUSTOM_PRESET_INDEX)  # Custom
            self._on_revert_to_custom()
            self.tree.blockSignals(False)

        self.update_info_label()
        self.check_dependencies()

    def check_dependencies(self):
        """Check for missing dependencies and show warning"""
        self._render_dependency_warning(self._get_missing_dependencies())

    def _render_dependency_warning(self, missing: dict):
        """Render the dependency-warning label from a {block: [deps]} mapping"""
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

    def save_and_close(self):
        """Save configuration and close dialog"""
        # Check for dependency issues
        missing = self._get_missing_dependencies()
        if missing:
            response = QMessageBox.warning(
                self,
                self.tr("Missing Dependencies"),
                self._missing_dependencies_message(),
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
