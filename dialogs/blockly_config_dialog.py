#!/usr/bin/env python3
"""
Blockly Configuration Dialog
Allows users to customize which blocks are available

The preset combo / category tree / dependency-warning / save scaffold is
shared with ThymioConfigDialog via BaseBlockConfigDialog; only the
Blockly-specific category set, preset list and preset-detection live here.
"""

from config.blockly_config import (
    BlocklyConfig, PRESETS,
)

from dialogs._block_config_dialog_base import (
    BaseBlockConfigDialog,
    THYMIO_CATEGORIES,  # re-exported for backward compatibility
)


# Thymio categories to exclude from this dialog (they have their own ThymioConfigDialog).
# Re-exported above from the shared base so the set is single-sourced.

# Category colors based on Blockly colors
BLOCKLY_CATEGORY_COLORS = {
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


class BlocklyConfigDialog(BaseBlockConfigDialog):
    """Dialog for configuring available Blockly blocks"""

    # "Custom" is the last entry of the 11-item preset list.
    CUSTOM_PRESET_INDEX = 10

    def _window_title(self) -> str:
        return self.tr("Configure Events & Actions")

    def _window_size(self) -> tuple:
        return (700, 600)

    def _preset_items(self) -> list:
        # Note: "Thymio Robot" preset moved to separate ThymioConfigDialog
        return [
            self.tr("Full (All Blocks)"),
            self.tr("Beginner (Basic Blocks)"),
            self.tr("Intermediate (More Features)"),
            self.tr("Platformer Game"),
            self.tr("Grid-based RPG"),
            self.tr("Sokoban (Box Puzzle)"),
            self.tr("Testing (Validated Only)"),
            self.tr("Implemented Only"),
            self.tr("Code Editor"),
            self.tr("Blockly Editor"),
            self.tr("Custom")
        ]

    def _tree_label_text(self) -> str:
        return self.tr("Select blocks to enable:")

    def _tree_column0_width(self) -> int:
        return 300

    def _include_category(self, category: str) -> bool:
        # Skip Thymio categories - they have their own ThymioConfigDialog
        return category not in THYMIO_CATEGORIES

    def _category_color(self, category: str):
        return BLOCKLY_CATEGORY_COLORS.get(category)

    def _current_preset_index(self) -> int:
        # Update preset combo (Thymio preset moved to ThymioConfigDialog)
        return {
            "full": 0,
            "beginner": 1,
            "intermediate": 2,
            "platformer": 3,
            "grid_rpg": 4,
            "sokoban": 5,
            "testing": 6,
            "implemented_only": 7,
            "code_editor": 8,
            "blockly_editor": 9,
        }.get(self.config.preset_name, 10)  # 10 = Custom

    def _on_revert_to_custom(self):
        self.config.preset_name = "custom"

    def on_preset_changed(self, text: str):
        """Handle preset selection (Thymio preset moved to ThymioConfigDialog)"""
        preset_map = {
            self.tr("Full (All Blocks)"): "full",
            self.tr("Beginner (Basic Blocks)"): "beginner",
            self.tr("Intermediate (More Features)"): "intermediate",
            self.tr("Platformer Game"): "platformer",
            self.tr("Grid-based RPG"): "grid_rpg",
            self.tr("Sokoban (Box Puzzle)"): "sokoban",
            self.tr("Testing (Validated Only)"): "testing",
            self.tr("Implemented Only"): "implemented_only",
            self.tr("Code Editor"): "code_editor",
            self.tr("Blockly Editor"): "blockly_editor",
        }

        if text == self.tr("Custom"):
            # Don't change config, just mark as custom
            self.config.preset_name = "custom"
            return

        preset_key = preset_map.get(text)
        if preset_key and preset_key in PRESETS:
            # Make a copy of the preset to avoid modifying the original
            self.config = BlocklyConfig.from_dict(PRESETS[preset_key].to_dict())
            self.load_config_to_ui()

    def _get_missing_dependencies(self) -> dict:
        return self.config.get_missing_dependencies()

    def _missing_dependencies_message(self) -> str:
        return self.tr("Some enabled blocks are missing their dependencies. "
                        "The blocks may not work correctly.\n\n"
                        "Do you want to save anyway?")

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
