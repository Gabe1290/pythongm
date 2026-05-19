#!/usr/bin/env python3
"""
Thymio Configuration Dialog
Allows users to customize which Thymio blocks are available.
This is a separate window from the standard BlocklyConfigDialog.

The preset combo / category tree / dependency-warning / save scaffold is
shared with BlocklyConfigDialog via BaseBlockConfigDialog; only the
Thymio-specific category set, preset list and preset-detection live here.
"""

from config.blockly_config import (
    BLOCK_REGISTRY, BLOCK_DEPENDENCIES,
)

from dialogs._block_config_dialog_base import (
    BaseBlockConfigDialog,
    THYMIO_CATEGORIES,  # re-exported for backward compatibility
)


# Thymio-specific categories are single-sourced in the shared base and
# re-exported above.

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


class ThymioConfigDialog(BaseBlockConfigDialog):
    """Dialog for configuring available Thymio blocks"""

    # "Custom" is the last entry of the 4-item Thymio preset list.
    CUSTOM_PRESET_INDEX = 3

    def _window_title(self) -> str:
        return self.tr("Configure Thymio Events & Actions")

    def _window_size(self) -> tuple:
        return (600, 500)

    def _preset_items(self) -> list:
        return [
            self.tr("Thymio Full (All Thymio Blocks)"),
            self.tr("Thymio Basic (Buttons + Motors)"),
            self.tr("Thymio Sensors"),
            self.tr("Custom")
        ]

    def _tree_label_text(self) -> str:
        return self.tr("Select Thymio blocks to enable:")

    def _tree_column0_width(self) -> int:
        return 250

    def _include_category(self, category: str) -> bool:
        # Only show Thymio categories
        return category in THYMIO_CATEGORIES

    def _category_color(self, category: str):
        return THYMIO_CATEGORY_COLORS.get(category)

    def _current_preset_index(self) -> int:
        # Check if it matches a known Thymio preset
        if self._is_thymio_full():
            return 0
        elif self._is_thymio_basic():
            return 1
        elif self._is_thymio_sensors():
            return 2
        else:
            return 3  # Custom

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

    def _get_missing_dependencies(self) -> dict:
        """Compute missing dependencies, filtered to Thymio blocks only"""
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
        return missing

    def _missing_dependencies_message(self) -> str:
        return self.tr("Some enabled Thymio blocks are missing their dependencies. "
                        "The blocks may not work correctly.\n\n"
                        "Do you want to save anyway?")

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
