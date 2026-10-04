#!/usr/bin/env python3
"""Playground resize (size presets + custom size) for
:class:`ThymioPlaygroundWindow`.

Extracted verbatim from ``extensions/thymio/playground_window.py``
(``docs/PROJECT_STATUS.md``'s Thymio-extraction follow-up). A mixin --
``self`` / ``self.tr()`` / siblings (``reset_view``) resolve on the
concrete window via MRO.
"""
import pygame

from core.logger import get_logger

logger = get_logger(__name__)


class ResizeMixin:
    """The size-preset/custom-size UI handlers and the actual playground
    resize (surface reallocation, border-wall regeneration, clamping
    existing elements to the new bounds)."""

    def on_size_preset_changed(self, index: int):
        """Handle size preset selection"""
        data = self.size_preset_combo.currentData()
        if data:
            width, height = data
            self.width_spinbox.blockSignals(True)
            self.height_spinbox.blockSignals(True)
            self.width_spinbox.setValue(width)
            self.height_spinbox.setValue(height)
            self.width_spinbox.blockSignals(False)
            self.height_spinbox.blockSignals(False)
            self.resize_playground(width, height)

    def on_custom_size_changed(self):
        """Handle custom size spinbox changes - set preset to Custom"""
        # Check if current values match any preset
        w = self.width_spinbox.value()
        h = self.height_spinbox.value()

        # Find matching preset or set to Custom
        matched = False
        for i in range(1, self.size_preset_combo.count()):
            data = self.size_preset_combo.itemData(i)
            if data and data[0] == w and data[1] == h:
                self.size_preset_combo.blockSignals(True)
                self.size_preset_combo.setCurrentIndex(i)
                self.size_preset_combo.blockSignals(False)
                matched = True
                break

        if not matched:
            self.size_preset_combo.blockSignals(True)
            self.size_preset_combo.setCurrentIndex(0)  # Custom
            self.size_preset_combo.blockSignals(False)

    def apply_custom_size(self):
        """Apply the current custom size from spinboxes"""
        width = self.width_spinbox.value()
        height = self.height_spinbox.value()
        self.resize_playground(width, height)

    def resize_playground(self, width: int, height: int):
        """Resize the playground to new dimensions"""
        old_width = self.playground_width
        old_height = self.playground_height

        if width == old_width and height == old_height:
            return

        # Update size
        self.playground_width = width
        self.playground_height = height

        # Resize pygame widget and reusable world surface
        self.pygame_widget.resize_surface(width, height)
        self._world_surface = pygame.Surface((width, height))

        # Reposition Thymio if outside new bounds
        margin = 50
        if self.thymio.x > width - margin:
            self.thymio.x = width // 2
        if self.thymio.y > height - margin:
            self.thymio.y = height // 2

        # Regenerate border walls
        self._update_border_walls()

        # Remove obstacles and lines outside new bounds
        self._clamp_elements_to_bounds()

        # Reset view
        self.reset_view()

        self.statusbar.showMessage(
            self.tr("Playground resized to {0}x{1}").format(width, height)
        )
        logger.info(f"Playground resized from {old_width}x{old_height} to {width}x{height}")

    def _update_border_walls(self):
        """Update border wall obstacles for current playground size"""
        # Remove old border walls (first 4)
        if len(self.obstacles) >= 4:
            self.obstacles = self.obstacles[4:]

        # Add new border walls at the beginning
        border_walls = [
            pygame.Rect(0, 0, self.playground_width, 10),  # Top
            pygame.Rect(0, self.playground_height - 10, self.playground_width, 10),  # Bottom
            pygame.Rect(0, 0, 10, self.playground_height),  # Left
            pygame.Rect(self.playground_width - 10, 0, 10, self.playground_height),  # Right
        ]
        self.obstacles = border_walls + self.obstacles

    def _clamp_elements_to_bounds(self):
        """Remove or clamp elements outside playground bounds"""
        # Remove obstacles outside bounds (keep border walls)
        valid_obstacles = self.obstacles[:4]  # Keep borders
        for obstacle in self.obstacles[4:]:
            if (obstacle.right <= self.playground_width and
                obstacle.bottom <= self.playground_height):
                valid_obstacles.append(obstacle)
        self.obstacles = valid_obstacles

        # Remove lines outside bounds
        valid_lines = []
        for line in self.line_rects:
            if (line.right <= self.playground_width and
                line.bottom <= self.playground_height):
                valid_lines.append(line)
        self.line_rects = valid_lines

        # Clear selection if element was removed
        if self.selected_obstacle and self.selected_obstacle not in self.obstacles:
            self.selected_obstacle = None
        if self.selected_line and self.selected_line not in self.line_rects:
            self.selected_line = None
