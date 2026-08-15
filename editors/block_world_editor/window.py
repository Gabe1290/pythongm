#!/usr/bin/env python3
"""BlockWorldEditorWindow (docs/BLOCK_WORLD_EDITOR_PLAN.md, Tier 7d).

Phase 1: embeds the real extensions.block_world.renderer.
render_block_world_view output in a Qt widget, with a free-fly build-mode
camera. Reuses widgets.thymio_playground.PygameWidget verbatim for the
pygame-surface-to-QPixmap plumbing (it has zero Thymio-specific code)
rather than reinventing that pattern.

Phase 2 (this file): left-click place / right-click break, reusing
extensions.block_world.renderer's own picking functions (screen_ray +
pick_voxel + unproject_to_plane) -- the exact math
tools/preview_block_world.py's aim() already proves works outside a real
running game -- routed through a QUndoStack so building is reversible,
matching editors/room_undo_commands.py's established shape.

Phase 3 (this file): loads a room's existing blocks/<room>.json on open
(io.py) and saves back to it (Ctrl+S / a Save toolbar action) -- the
exact sibling-file shape load_block_world already reads at runtime, so
nothing further is needed to make a saved world playable. Also the Room
Editor toolbar entry that actually opens this window for a real project
room (see editors/room_editor/__init__.py's open_block_world_editor).

Controls: WASD fly (no gravity/collision -- build-mode, not play-mode),
middle-mouse-drag to look (yaw + pitch), wheel to pitch, Space/Shift to
step the z-layer, left-click place / right-click break (using the
palette's current block + a fixed reach), Ctrl+Z / Ctrl+Y undo/redo,
Ctrl+S save.
"""
import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QUndoStack, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStatusBar,
    QToolBar, QMessageBox,
)

import pygame

from widgets.thymio_playground import PygameWidget
from extensions.block_world.renderer import (
    render_block_world_view, clamp_pitch, draw_cell_outline, eye_z_for,
    horizon_for, march_ray, pick_voxel, screen_ray, unproject_to_plane,
)
from extensions.block_world.state import get_block, is_breakable, DEFAULT_HOTBAR
from core.logger import get_logger

from .io import load_room_blocks, save_room_blocks
from .palette import BlockPalette
from .session import BlockWorldEditSession, make_empty_room
from .undo_commands import make_set_block_command

logger = get_logger(__name__)

FPS = 60
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
MOVE_SPEED_PX_PER_SEC = 160.0
TURN_MOUSE_SENSITIVITY = 0.25    # degrees of yaw per pixel of horizontal drag
PITCH_MOUSE_SENSITIVITY = 0.25   # degrees of pitch per pixel of vertical drag
WHEEL_PITCH_STEP = 4.0
EDITOR_REACH = 8                 # cells -- build-mode reach, not a gameplay value
DEFAULT_BLOCK = DEFAULT_HOTBAR[0]

CROSSHAIR_SIZE = 7
CROSSHAIR_COLOR_ACTIVE = (235, 235, 235)
CROSSHAIR_COLOR_IDLE = (150, 150, 150)


class BlockWorldEditorWindow(QMainWindow):
    """Window hosting the Block World voxel-painter canvas.

    project_path + room_name (both required together) make this editor
    load-/save-capable against a real project's blocks/<room_name>.json;
    omitting both keeps it constructible standalone (demos, tests,
    make_empty_room()) with Save disabled."""

    def __init__(self, room=None, parent=None, project_path=None, room_name=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMinimumSize(900, 700)

        self.project_path = project_path
        self.room_name = room_name

        self.session = BlockWorldEditSession(room if room is not None else make_empty_room())

        if self.project_path and self.room_name:
            try:
                load_room_blocks(self.session.room, self.project_path, self.room_name)
            except (KeyError, ValueError, OSError) as e:
                logger.error(f"Failed to load blocks for room '{self.room_name}': {e}")
                QMessageBox.warning(
                    self, self.tr("Block World"),
                    self.tr("Could not load this room's saved blocks ({0}); "
                            "starting empty.").format(e))

        # Start in the middle of the room, standing on the ground layer.
        cx = self.session.room.width / (2 * self.session.cell_size)
        cy = self.session.room.height / (2 * self.session.cell_size)
        self.session.place(cx, cy)

        self.undo_stack = QUndoStack(self)
        self.undo_stack.cleanChanged.connect(self._update_title)

        self._held_keys = set()
        self._dragging = False
        self._drag_last = None
        self._mouse_pos = (CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)

        self._setup_ui()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_shortcuts()
        self._update_title()

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

    def _update_title(self, *_args):
        title = self.tr("Block World Editor")
        if self.room_name:
            title += f" - {self.room_name}"
        if self.can_save() and not self.undo_stack.isClean():
            title += " *"
        self.setWindowTitle(title)

    def can_save(self) -> bool:
        return bool(self.project_path and self.room_name)

    def save(self) -> bool:
        if not self.can_save():
            QMessageBox.information(
                self, self.tr("Block World"),
                self.tr("This room has no project/name to save to."))
            return False
        try:
            path = save_room_blocks(self.session.room, self.project_path, self.room_name)
        except OSError as e:
            logger.error(f"Failed to save blocks for room '{self.room_name}': {e}")
            QMessageBox.critical(
                self, self.tr("Block World"),
                self.tr("Failed to save blocks:\n{0}").format(e))
            return False
        self.undo_stack.setClean()
        self._status_label.setText(self.tr("Saved to {0}").format(path))
        logger.info(f"Block World: saved {path}")
        return True

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(5, 5, 5, 5)

        left = QVBoxLayout()
        self.canvas = PygameWidget(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.canvas.key_pressed.connect(self._on_key_pressed)
        self.canvas.key_released.connect(self._on_key_released)
        self.canvas.mouse_pressed.connect(self._on_mouse_pressed)
        self.canvas.mouse_released.connect(self._on_mouse_released)
        self.canvas.mouse_moved.connect(self._on_mouse_moved)
        self.canvas.mouse_wheel.connect(self._on_mouse_wheel)
        left.addWidget(self.canvas)

        hint = QLabel(self.tr(
            "WASD fly | middle-drag to look | wheel to pitch | "
            "Space/Shift layer up/down | left-click place | right-click break | "
            "Ctrl+Z / Ctrl+Y undo/redo"))
        hint.setStyleSheet("color: #666; font-size: 11px;")
        hint.setWordWrap(True)
        left.addWidget(hint)
        outer.addLayout(left, 1)

        right = QVBoxLayout()
        right.addWidget(QLabel(self.tr("Blocks")))
        self.palette = BlockPalette()
        self.palette.select(DEFAULT_BLOCK)
        right.addWidget(self.palette, 1)
        right_widget = QWidget()
        right_widget.setLayout(right)
        right_widget.setMaximumWidth(240)
        outer.addWidget(right_widget)

    def _setup_toolbar(self):
        toolbar = QToolBar(self.tr("Block World Editor"))
        toolbar.setMovable(False)
        save_action = toolbar.addAction(self.tr("💾 Save"))
        save_action.setToolTip(self.tr("Save blocks (Ctrl+S)"))
        save_action.triggered.connect(self.save)
        save_action.setEnabled(self.can_save())
        self.addToolBar(toolbar)

    def _setup_statusbar(self):
        self.setStatusBar(QStatusBar())
        self._status_label = QLabel()
        self.statusBar().addWidget(self._status_label)
        self._update_status()

    def _setup_shortcuts(self):
        undo_sc = QShortcut(QKeySequence.Undo, self)
        undo_sc.activated.connect(self.undo_stack.undo)
        redo_sc = QShortcut(QKeySequence.Redo, self)
        redo_sc.activated.connect(self.undo_stack.redo)
        # QKeySequence.Redo is Ctrl+Shift+Z on some platforms; also bind the
        # Ctrl+Y this repo's own Room Editor convention uses elsewhere.
        redo_sc_y = QShortcut(QKeySequence("Ctrl+Y"), self)
        redo_sc_y.activated.connect(self.undo_stack.redo)
        save_sc = QShortcut(QKeySequence.Save, self)
        save_sc.activated.connect(self.save)

    # ---- input -----------------------------------------------------------

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
        self._mouse_pos = (x, y)
        if button == Qt.MiddleButton:
            self._dragging = True
            self._drag_last = (x, y)
        elif button == Qt.LeftButton:
            self._place_block((x, y))
        elif button == Qt.RightButton:
            self._break_block((x, y))

    def _on_mouse_released(self, x, y, button):
        if button == Qt.MiddleButton:
            self._dragging = False
            self._drag_last = None

    def _on_mouse_moved(self, x, y):
        self._mouse_pos = (x, y)
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

    # ---- picking / editing -------------------------------------------------

    def _aim(self, mouse_pos):
        """(target, placement) for wherever mouse_pos is pointing -- a real
        3D voxel march against blocks, falling back to the camera's own
        floor plane over open ground. Ported from
        tools/preview_block_world.py's aim(), adapted to this session's
        room/camera instead of the preview tool's globals."""
        room = self.session.room
        camera = self.session.camera
        cell_size = self.session.cell_size
        cfg = self.session.camera_config
        layer = int(cfg["z_layer"])
        fov = math.radians(cfg.get("fov", 66))
        ox, oy = room._sprite_top_left(camera)
        px = ox + camera._cached_width / 2
        py = oy + camera._cached_height / 2
        facing = math.radians(-camera.facing_angle)
        sw, sh = CANVAS_WIDTH, CANVAS_HEIGHT
        mx, my = mouse_pos

        eye_z = eye_z_for(cfg)
        horizon = horizon_for(sh, cfg.get("pitch", 0.0))
        ray_angle, z_per_px = screen_ray(mx, my, facing, fov, sw, sh, cell_size, horizon)
        target, build = pick_voxel(room, px, py, eye_z, ray_angle, z_per_px,
                                    cell_size, EDITOR_REACH)

        if target is None:
            build = None
            ground = unproject_to_plane(mx, my, layer, px, py, eye_z, facing,
                                         fov, sw, sh, cell_size, horizon)
            if ground is not None:
                cell = (int(ground[0] // cell_size), int(ground[1] // cell_size), layer)
                within = math.hypot(ground[0] - px, ground[1] - py) / cell_size <= EDITOR_REACH
                if within and get_block(room, *cell) is None:
                    for cx, cy, *_rest in march_ray(room, px, py, ray_angle,
                                                     cell_size, EDITOR_REACH + 1):
                        if (cx, cy) == cell[:2]:
                            build = cell
                            break
                        if get_block(room, cx, cy, layer) is not None:
                            break  # a wall stands between here and there
        return target, build

    def _place_block(self, mouse_pos):
        block_type = self.palette.current_block()
        if block_type is None:
            return
        _target, placement = self._aim(mouse_pos)
        if placement is None or get_block(self.session.room, *placement) is not None:
            return
        command = make_set_block_command(self.session.room, *placement, new_type=block_type)
        self.undo_stack.push(command)
        self._update_status()

    def _break_block(self, mouse_pos):
        target, _placement = self._aim(mouse_pos)
        if target is None:
            return
        if not is_breakable(get_block(self.session.room, *target)):
            return
        command = make_set_block_command(self.session.room, *target, new_type=None)
        self.undo_stack.push(command)
        self._update_status()

    # ---- frame loop --------------------------------------------------------

    def _tick(self):
        self._apply_movement(1.0 / FPS)
        surface = self.canvas.get_surface()
        render_block_world_view(self.session.room, surface)
        self._draw_aim_overlay(surface)
        self.canvas.update_display()
        self._update_status()

    def _draw_aim_overlay(self, surface):
        target, placement = self._aim(self._mouse_pos)
        if placement is not None:
            camera = self.session.camera
            cfg = self.session.camera_config
            ox, oy = self.session.room._sprite_top_left(camera)
            draw_cell_outline(
                surface, placement,
                ox + camera._cached_width / 2, oy + camera._cached_height / 2,
                eye_z_for(cfg), math.radians(-camera.facing_angle),
                math.radians(cfg.get("fov", 66)), self.session.cell_size,
                horizon=horizon_for(CANVAS_HEIGHT, cfg.get("pitch", 0.0)))

        color = CROSSHAIR_COLOR_ACTIVE if target else CROSSHAIR_COLOR_IDLE
        mx, my = self._mouse_pos
        pygame.draw.line(surface, color, (mx - CROSSHAIR_SIZE, my), (mx + CROSSHAIR_SIZE, my))
        pygame.draw.line(surface, color, (mx, my - CROSSHAIR_SIZE), (mx, my + CROSSHAIR_SIZE))

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
            "cell {0}   layer {1}   angle {2:.0f}   pitch {3:+.0f}   "
            "block {4}   undo {5}").format(
                cell, cfg.get("z_layer", 0), camera.facing_angle % 360,
                cfg.get("pitch", 0.0), self.palette.current_block() or "-",
                self.undo_stack.count()))

    def closeEvent(self, event):
        if self.can_save() and not self.undo_stack.isClean():
            reply = QMessageBox.question(
                self, self.tr("Block World"),
                self.tr("Save changes to this room's blocks before closing?"),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save)
            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            if reply == QMessageBox.Save and not self.save():
                event.ignore()
                return
        self.timer.stop()
        self.session.close()
        super().closeEvent(event)
