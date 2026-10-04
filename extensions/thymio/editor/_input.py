#!/usr/bin/env python3
"""Keyboard/mouse input and edit-mode selection for
:class:`ThymioPlaygroundWindow`.

Extracted verbatim from ``extensions/thymio/playground_window.py``
(``docs/PROJECT_STATUS.md``'s Thymio-extraction follow-up). A mixin --
``self`` / ``self.tr()`` / siblings (``screen_to_world``, ``_clamp_camera``,
``_update_zoom_label``, ``_push_undo``, ``reset_robot``, ``toggle_pause``,
``delete_selected``, ``zoom_in``/``zoom_out``/``reset_view``/
``fit_to_window``, ...) resolve on the concrete window via MRO.
"""
from typing import Tuple

import pygame
from PySide6.QtCore import Qt

from extensions.thymio.editor._constants import EditMode, MIN_ELEMENT_SIZE


class InputMixin:
    """Keyboard shortcuts, mouse press/release/move (drawing, panning,
    selecting), and the current edit-mode state."""

    def set_edit_mode(self, mode: EditMode):
        """Set the current edit mode"""
        self.edit_mode = mode
        self.is_drawing = False
        self.draw_start = None
        self.draw_current = None
        self.selected_obstacle = None
        self.selected_line = None

        mode_names = {
            EditMode.SELECT: self.tr("Select"),
            EditMode.OBSTACLE: self.tr("Obstacle"),
            EditMode.LINE: self.tr("Line")
        }
        self.edit_mode_label.setText(self.tr("Mode: {0}").format(mode_names[mode]))
        self.statusbar.showMessage(self.tr("Edit mode: {0}").format(mode_names[mode]))

    def on_key_pressed(self, key: int):
        """Handle key press"""
        if key == Qt.Key_Up:
            self.thymio.set_button('forward', True)
            self.thymio.set_motor_speed(200, 200)
            self.thymio.set_led_top(0, 32, 0)  # Green
            self.statusbar.showMessage(self.tr("Moving forward"))

        elif key == Qt.Key_Down:
            self.thymio.set_button('backward', True)
            self.thymio.set_motor_speed(-200, -200)
            self.thymio.set_led_top(32, 16, 0)  # Orange
            self.statusbar.showMessage(self.tr("Moving backward"))

        elif key == Qt.Key_Left:
            self.thymio.set_button('left', True)
            self.thymio.set_motor_speed(-150, 150)
            self.thymio.set_led_top(0, 0, 32)  # Blue
            self.statusbar.showMessage(self.tr("Turning left"))

        elif key == Qt.Key_Right:
            self.thymio.set_button('right', True)
            self.thymio.set_motor_speed(150, -150)
            self.thymio.set_led_top(32, 0, 32)  # Magenta
            self.statusbar.showMessage(self.tr("Turning right"))

        elif key == Qt.Key_Space:
            self.thymio.set_button('center', True)
            self.thymio.set_motor_speed(0, 0)
            self.thymio.set_led_top(32, 0, 0)  # Red
            self.statusbar.showMessage(self.tr("Stopped"))

        elif key == Qt.Key_R:
            self.reset_robot()

        elif key == Qt.Key_P:
            self.toggle_pause()

        elif key == Qt.Key_Delete or key == Qt.Key_Backspace:
            self.delete_selected()

        elif key == Qt.Key_Escape:
            # Deselect and cancel drawing
            self.selected_obstacle = None
            self.selected_line = None
            self.is_drawing = False
            self.draw_start = None
            self.draw_current = None
            self.statusbar.showMessage(self.tr("Selection cleared"))

        # Zoom controls
        elif key == Qt.Key_Plus or key == Qt.Key_Equal:
            self.zoom_in()
        elif key == Qt.Key_Minus:
            self.zoom_out()
        elif key == Qt.Key_Home:
            self.reset_view()
        elif key == Qt.Key_F:
            self.fit_to_window()

    def on_key_released(self, key: int):
        """Handle key release"""
        if key == Qt.Key_Up:
            self.thymio.set_button('forward', False)
        elif key == Qt.Key_Down:
            self.thymio.set_button('backward', False)
        elif key == Qt.Key_Left:
            self.thymio.set_button('left', False)
        elif key == Qt.Key_Right:
            self.thymio.set_button('right', False)
        elif key == Qt.Key_Space:
            self.thymio.set_button('center', False)

    def on_mouse_pressed(self, x: int, y: int, button: int):
        """Handle mouse press in pygame area"""
        # Middle mouse button for panning
        if button == Qt.MiddleButton:
            self.is_panning = True
            self.pan_start = (x, y)
            self.pan_start_camera = (self.camera_x, self.camera_y)
            return

        if button != Qt.LeftButton:
            return

        # Convert screen coordinates to world coordinates
        world_x, world_y = self.screen_to_world(x, y)

        if self.edit_mode == EditMode.SELECT:
            # Try to select an obstacle or line (using world coordinates)
            self._select_element_at(world_x, world_y)
        elif self.edit_mode in (EditMode.OBSTACLE, EditMode.LINE):
            # Start drawing (store screen coords, convert during drawing)
            self.is_drawing = True
            self.draw_start = (x, y)
            self.draw_current = (x, y)

    def on_mouse_released(self, x: int, y: int, button: int):
        """Handle mouse release in pygame area"""
        # End panning
        if button == Qt.MiddleButton:
            self.is_panning = False
            self.pan_start = None
            self.pan_start_camera = None
            return

        if button != Qt.LeftButton:
            return

        if self.is_drawing and self.draw_start:
            # Convert screen coordinates to world coordinates
            world_start = self.screen_to_world(*self.draw_start)
            world_end = self.screen_to_world(x, y)

            # Create rect in world coordinates
            rect = self._get_draw_rect(world_start, world_end)

            # Only add if big enough (in world units)
            if rect.width >= MIN_ELEMENT_SIZE and rect.height >= MIN_ELEMENT_SIZE:
                if self.edit_mode == EditMode.OBSTACLE:
                    self.obstacles.append(rect)
                    self._push_undo('add_obstacle', rect)
                    self.statusbar.showMessage(self.tr("Obstacle added"))
                elif self.edit_mode == EditMode.LINE:
                    self.line_rects.append(rect)
                    self._push_undo('add_line', rect)
                    self.statusbar.showMessage(self.tr("Line segment added"))
            else:
                self.statusbar.showMessage(self.tr("Element too small - drag to create larger area"))

        self.is_drawing = False
        self.draw_start = None
        self.draw_current = None

    def on_mouse_moved(self, x: int, y: int):
        """Handle mouse move in pygame area"""
        # Handle panning with middle mouse button
        if self.is_panning and self.pan_start and self.pan_start_camera:
            # Calculate delta in screen pixels
            dx = x - self.pan_start[0]
            dy = y - self.pan_start[1]

            # Convert to world units (inverse of zoom)
            world_dx = -dx / self.zoom_level
            world_dy = -dy / self.zoom_level

            # Update camera position
            self.camera_x = self.pan_start_camera[0] + world_dx
            self.camera_y = self.pan_start_camera[1] + world_dy

            self._clamp_camera()
            self._update_zoom_label()
            return

        if self.is_drawing:
            self.draw_current = (x, y)

    def _select_element_at(self, x: int, y: int):
        """Try to select an element at the given coordinates"""
        self.selected_obstacle = None
        self.selected_line = None

        # Check obstacles (skip border walls - first 4)
        for obstacle in reversed(self.obstacles[4:]):  # Check in reverse for top-most
            if obstacle.collidepoint(x, y):
                self.selected_obstacle = obstacle
                self.statusbar.showMessage(self.tr("Obstacle selected - press Delete to remove"))
                return

        # Check line segments
        for line in reversed(self.line_rects):
            if line.collidepoint(x, y):
                self.selected_line = line
                self.statusbar.showMessage(self.tr("Line segment selected - press Delete to remove"))
                return

        self.statusbar.showMessage(self.tr("No element selected"))

    def _get_draw_rect(self, start: Tuple[int, int], end: Tuple[int, int]) -> pygame.Rect:
        """Create a pygame Rect from two corner points"""
        x1, y1 = start
        x2, y2 = end

        # Calculate rect from any two corners
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        return pygame.Rect(left, top, width, height)
