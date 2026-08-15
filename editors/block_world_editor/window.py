#!/usr/bin/env python3
"""BlockWorldEditorWindow -- Phase 1 of Tier 7d
(docs/BLOCK_WORLD_EDITOR_PLAN.md): embeds the real
extensions.block_world.renderer.render_block_world_view output in a Qt
widget, with a free-fly build-mode camera. No place/break editing yet
(that's Phase 2) -- this phase exists to prove the
pygame-surface-in-a-QWidget pipeline against the real renderer before
anything is built on top of it.

Reuses widgets.thymio_playground.PygameWidget verbatim for the
pygame-surface-to-QPixmap plumbing (it has zero Thymio-specific code --
see its class body) rather than reinventing that pattern, per the plan
doc's own "getting a pygame surface onto a Qt canvas is already a solved
problem in this codebase" note.

Controls: WASD fly (no gravity/collision -- this is a build-mode camera,
matching tools/preview_block_world.py's own "press C to fly through
walls" debug-camera precedent), middle-mouse-drag to look (yaw + pitch),
wheel to pitch, Space/Shift to step the current z-layer up/down. Look is
deliberately on the MIDDLE button, not left -- Phase 2 gives left/right
click their own jobs (place/break), so look needs a button of its own
that can never collide with an editing click.
"""
import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QStatusBar

import pygame

from widgets.thymio_playground import PygameWidget
from extensions.block_world.renderer import render_block_world_view, clamp_pitch
from core.logger import get_logger

from .session import BlockWorldEditSession, make_empty_room

logger = get_logger(__name__)

FPS = 60
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
MOVE_SPEED_PX_PER_SEC = 160.0
TURN_MOUSE_SENSITIVITY = 0.25    # degrees of yaw per pixel of horizontal drag
PITCH_MOUSE_SENSITIVITY = 0.25   # degrees of pitch per pixel of vertical drag
WHEEL_PITCH_STEP = 4.0


class BlockWorldEditorWindow(QMainWindow):
    """Standalone window hosting the Block World voxel-painter canvas.
    Phase 3 wires a menu entry that opens this against a real project
    room; until then it's constructible (and testable) against any
    GameRoom, including a bare one from make_empty_room()."""

    def __init__(self, room=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(self.tr("Block World Editor"))
        self.setMinimumSize(900, 700)

        self.session = BlockWorldEditSession(room if room is not None else make_empty_room())
        # Start in the middle of the room, standing on the ground layer.
        cx = self.session.room.width / (2 * self.session.cell_size)
        cy = self.session.room.height / (2 * self.session.cell_size)
        self.session.place(cx, cy)

        self._held_keys = set()
        self._dragging = False
        self._drag_last = None

        self._setup_ui()
        self._setup_statusbar()

        if pygame.display.get_surface() is None:
            # extensions/block_world/renderer.py's _load_texture calls
            # convert_alpha(), which needs an active display mode -- see
            # tools/preview_block_world.py's save_shots() for the same
            # requirement in a headless context.
            pygame.display.set_mode((1, 1))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000 // FPS)

        logger.info("Block World editor window created")

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(5, 5, 5, 5)

        self.canvas = PygameWidget(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.canvas.key_pressed.connect(self._on_key_pressed)
        self.canvas.key_released.connect(self._on_key_released)
        self.canvas.mouse_pressed.connect(self._on_mouse_pressed)
        self.canvas.mouse_released.connect(self._on_mouse_released)
        self.canvas.mouse_moved.connect(self._on_mouse_moved)
        self.canvas.mouse_wheel.connect(self._on_mouse_wheel)
        layout.addWidget(self.canvas)

        hint = QLabel(self.tr(
            "WASD fly | drag with middle mouse button to look | wheel to pitch | "
            "Space/Shift to step layer up/down"))
        hint.setStyleSheet("color: #666; font-size: 11px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

    def _setup_statusbar(self):
        self.setStatusBar(QStatusBar())
        self._status_label = QLabel()
        self.statusBar().addWidget(self._status_label)
        self._update_status()

    # ---- input ---------------------------------------------------------

    def _on_key_pressed(self, key):
        self._held_keys.add(key)
        if key == Qt.Key_Space:
            self._nudge_layer(1)
        elif key == Qt.Key_Shift:
            self._nudge_layer(-1)

    def _on_key_released(self, key):
        self._held_keys.discard(key)

    def _nudge_layer(self, delta):
        cfg = self.session.camera_config
        cfg["z_layer"] = max(0, int(cfg.get("z_layer", 0)) + delta)

    def _on_mouse_pressed(self, x, y, button):
        if button == Qt.MiddleButton:
            self._dragging = True
            self._drag_last = (x, y)

    def _on_mouse_released(self, x, y, button):
        if button == Qt.MiddleButton:
            self._dragging = False
            self._drag_last = None

    def _on_mouse_moved(self, x, y):
        if not self._dragging or self._drag_last is None:
            return
        last_x, last_y = self._drag_last
        dx, dy = x - last_x, y - last_y
        self._drag_last = (x, y)
        self.session.camera.facing_angle = (
            self.session.camera.facing_angle - dx * TURN_MOUSE_SENSITIVITY) % 360
        cfg = self.session.camera_config
        cfg["pitch"] = clamp_pitch(cfg.get("pitch", 0.0) - dy * PITCH_MOUSE_SENSITIVITY)

    def _on_mouse_wheel(self, x, y, delta):
        cfg = self.session.camera_config
        step = WHEEL_PITCH_STEP if delta > 0 else -WHEEL_PITCH_STEP
        cfg["pitch"] = clamp_pitch(cfg.get("pitch", 0.0) + step)

    # ---- frame loop ------------------------------------------------------

    def _tick(self):
        self._apply_movement(1.0 / FPS)
        render_block_world_view(self.session.room, self.canvas.get_surface())
        self.canvas.update_display()
        self._update_status()

    def _apply_movement(self, dt):
        camera = self.session.camera
        rad = math.radians(camera.facing_angle)
        fwd = (math.cos(rad), -math.sin(rad))
        dx = dy = 0.0
        if Qt.Key_W in self._held_keys:
            dx += fwd[0]; dy += fwd[1]
        if Qt.Key_S in self._held_keys:
            dx -= fwd[0]; dy -= fwd[1]
        if Qt.Key_A in self._held_keys:
            dx += fwd[1]; dy -= fwd[0]
        if Qt.Key_D in self._held_keys:
            dx -= fwd[1]; dy += fwd[0]
        if dx or dy:
            mag = math.hypot(dx, dy)
            step = MOVE_SPEED_PX_PER_SEC * dt / mag
            camera.x += dx * step
            camera.y += dy * step

    def _update_status(self):
        cfg = self.session.camera_config
        camera = self.session.camera
        cell_size = self.session.cell_size
        cell = (int(camera.x // cell_size), int(camera.y // cell_size))
        self._status_label.setText(self.tr(
            "cell {0}   layer {1}   angle {2:.0f}   pitch {3:+.0f}").format(
                cell, cfg.get("z_layer", 0), camera.facing_angle % 360,
                cfg.get("pitch", 0.0)))

    def closeEvent(self, event):
        self.timer.stop()
        self.session.close()
        super().closeEvent(event)
