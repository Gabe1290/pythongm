#!/usr/bin/env python3
"""Zoom/pan for :class:`ThymioPlaygroundWindow`.

Extracted verbatim from ``extensions/thymio/playground_window.py``
(``docs/PROJECT_STATUS.md``'s Thymio-extraction follow-up). A mixin --
``self`` / ``self.tr()`` / siblings (``_update_status_panel``,
``on_mouse_pressed``, ...) resolve on the concrete window via MRO.
"""
from typing import Optional, Tuple

import pygame

from extensions.thymio.editor._constants import COLOR_BACKGROUND


class CameraMixin:
    """Zoom level/camera pan state, the coordinate transforms between
    screen and world space, and the zoom/pan-triggering UI actions."""

    def _apply_zoom_and_pan(self, world_surface: pygame.Surface, display_surface: pygame.Surface):
        """Apply zoom and pan transformation to render world to display"""
        if self.zoom_level == 1.0 and self.camera_x == 0 and self.camera_y == 0:
            # No transformation needed
            display_surface.blit(world_surface, (0, 0))
            return

        if self.zoom_level < 1.0:
            # Zoomed out: the requested view exceeds the world surface, so a
            # subsurface would raise ValueError. Scale the whole world down
            # and letterbox it instead.
            scaled_w = max(1, int(self.playground_width * self.zoom_level))
            scaled_h = max(1, int(self.playground_height * self.zoom_level))
            scaled = pygame.transform.smoothscale(world_surface, (scaled_w, scaled_h))
            display_surface.fill(COLOR_BACKGROUND)
            display_surface.blit(scaled, ((self.playground_width - scaled_w) // 2,
                                          (self.playground_height - scaled_h) // 2))
            return

        # Calculate the visible area in world coordinates
        view_width = self.playground_width / self.zoom_level
        view_height = self.playground_height / self.zoom_level

        # Center of view in world coordinates
        center_x = self.playground_width / 2 + self.camera_x
        center_y = self.playground_height / 2 + self.camera_y

        # Calculate source rectangle (area of world to show)
        src_x = center_x - view_width / 2
        src_y = center_y - view_height / 2

        # Clamp to world bounds
        src_x = max(0, min(src_x, self.playground_width - view_width))
        src_y = max(0, min(src_y, self.playground_height - view_height))

        # Create source rect
        src_rect = pygame.Rect(int(src_x), int(src_y), int(view_width), int(view_height))

        # Extract the visible portion and scale it
        if src_rect.width > 0 and src_rect.height > 0:
            visible_portion = world_surface.subsurface(src_rect)
            scaled = pygame.transform.smoothscale(visible_portion, (self.playground_width, self.playground_height))
            display_surface.blit(scaled, (0, 0))
        else:
            display_surface.blit(world_surface, (0, 0))

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to world coordinates"""
        if self.zoom_level < 1.0:
            # Matches the letterboxed shrink rendering in _apply_zoom_and_pan
            offset_x = (self.playground_width - self.playground_width * self.zoom_level) / 2
            offset_y = (self.playground_height - self.playground_height * self.zoom_level) / 2
            return (int((screen_x - offset_x) / self.zoom_level),
                    int((screen_y - offset_y) / self.zoom_level))

        # Calculate visible area
        view_width = self.playground_width / self.zoom_level
        view_height = self.playground_height / self.zoom_level

        # Center of view
        center_x = self.playground_width / 2 + self.camera_x
        center_y = self.playground_height / 2 + self.camera_y

        # Top-left of visible area
        src_x = center_x - view_width / 2
        src_y = center_y - view_height / 2

        # Clamp to bounds (same as in _apply_zoom_and_pan)
        src_x = max(0, min(src_x, self.playground_width - view_width))
        src_y = max(0, min(src_y, self.playground_height - view_height))

        # Convert screen position to world position
        world_x = src_x + (screen_x / self.playground_width) * view_width
        world_y = src_y + (screen_y / self.playground_height) * view_height

        return (int(world_x), int(world_y))

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        if self.zoom_level < 1.0:
            # Matches the letterboxed shrink rendering in _apply_zoom_and_pan
            offset_x = (self.playground_width - self.playground_width * self.zoom_level) / 2
            offset_y = (self.playground_height - self.playground_height * self.zoom_level) / 2
            return (int(world_x * self.zoom_level + offset_x),
                    int(world_y * self.zoom_level + offset_y))

        # Calculate visible area
        view_width = self.playground_width / self.zoom_level
        view_height = self.playground_height / self.zoom_level

        # Center of view
        center_x = self.playground_width / 2 + self.camera_x
        center_y = self.playground_height / 2 + self.camera_y

        # Top-left of visible area
        src_x = center_x - view_width / 2
        src_y = center_y - view_height / 2

        # Clamp to bounds
        src_x = max(0, min(src_x, self.playground_width - view_width))
        src_y = max(0, min(src_y, self.playground_height - view_height))

        # Convert world position to screen position
        screen_x = ((world_x - src_x) / view_width) * self.playground_width
        screen_y = ((world_y - src_y) / view_height) * self.playground_height

        return (int(screen_x), int(screen_y))

    def zoom_in(self):
        """Zoom in by one step"""
        self.set_zoom(self.zoom_level + self.zoom_step)

    def zoom_out(self):
        """Zoom out by one step"""
        self.set_zoom(self.zoom_level - self.zoom_step)

    def set_zoom(self, level: float, center_x: Optional[int] = None, center_y: Optional[int] = None):
        """Set zoom level, optionally centering on a point"""
        old_zoom = self.zoom_level
        self.zoom_level = max(self.zoom_min, min(self.zoom_max, level))

        # Update slider without triggering signal
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(int(self.zoom_level * 100))
        self.zoom_slider.blockSignals(False)

        # Optionally adjust camera to keep a point centered
        if center_x is not None and center_y is not None and old_zoom != self.zoom_level:
            # Convert center point to world coordinates using old zoom
            world_x, world_y = self.screen_to_world(center_x, center_y)
            # The camera should pan so that this world point stays at screen position
            # This requires some math to keep the point under the cursor

        self._clamp_camera()
        self._update_zoom_label()

    def reset_view(self):
        """Reset zoom and pan to default"""
        self.zoom_level = 1.0
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(100)
        self.zoom_slider.blockSignals(False)
        self._update_zoom_label()
        self.statusbar.showMessage(self.tr("View reset to default"))

    def fit_to_window(self):
        """Fit the view to show the entire playground"""
        self.reset_view()

    def on_zoom_slider_changed(self, value: int):
        """Handle zoom slider value change"""
        self.set_zoom(value / 100.0)

    def on_mouse_wheel(self, x: int, y: int, delta: int):
        """Handle mouse wheel for zooming"""
        if delta > 0:
            # Zoom in toward cursor position
            self.set_zoom(self.zoom_level + self.zoom_step, x, y)
        elif delta < 0:
            # Zoom out
            self.set_zoom(self.zoom_level - self.zoom_step, x, y)

    def _clamp_camera(self):
        """Clamp camera position to valid bounds"""
        # Calculate maximum camera offset based on zoom
        view_width = self.playground_width / self.zoom_level
        view_height = self.playground_height / self.zoom_level

        max_offset_x = (self.playground_width - view_width) / 2
        max_offset_y = (self.playground_height - view_height) / 2

        self.camera_x = max(-max_offset_x, min(max_offset_x, self.camera_x))
        self.camera_y = max(-max_offset_y, min(max_offset_y, self.camera_y))

    def _update_zoom_label(self):
        """Update the zoom label in the UI"""
        self.zoom_label.setText(self.tr("Zoom: {0}%").format(int(self.zoom_level * 100)))
        self.pan_label.setText(self.tr("Pan: {0}, {1}").format(int(self.camera_x), int(self.camera_y)))
