#!/usr/bin/env python3
"""
Playground Runner - Runs a playground simulation with Thymio robots executing
linked object code. Embeds pygame in a Qt window.
"""

import math
import os
from typing import List

# Set SDL driver for off-screen rendering before importing pygame
if os.environ.get('SDL_VIDEODRIVER') not in ('x11', 'windows', 'cocoa'):
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap, QKeyEvent, QMouseEvent

from runtime.thymio_simulator import ThymioSimulator
from runtime.thymio_renderer import ThymioRenderer
from runtime.action_executor import ActionExecutor
from runtime.thymio_action_handlers import register_thymio_actions

from core.logger import get_logger
logger = get_logger(__name__)


FPS = 60


class _PygameCanvas(QLabel):
    """Qt label that displays a pygame surface and forwards key/mouse events.

    Mouse positions are emitted in surface coordinates (the QLabel is fixed-size
    and contains the surface 1:1, so widget-local coords == surface coords).
    """

    key_pressed = Signal(int)
    key_released = Signal(int)
    mouse_pressed = Signal(int, int, int)   # qt_button, x, y
    mouse_released = Signal(int, int, int)  # qt_button, x, y

    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        pygame.init()
        self.surface = pygame.Surface((width, height))
        self.setFixedSize(width, height)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("border: 1px solid #888;")

    def get_surface(self):
        return self.surface

    def update_display(self):
        data = pygame.image.tostring(self.surface, 'RGB')
        image = QImage(data, self.surface.get_width(),
                       self.surface.get_height(),
                       self.surface.get_width() * 3,
                       QImage.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(image))

    def keyPressEvent(self, event: QKeyEvent):
        # Ignore OS key auto-repeat: a held key otherwise re-fires the button
        # event (and now set_button) tens of times per second.
        if event.isAutoRepeat():
            event.accept()
            return
        self.key_pressed.emit(event.key())
        event.accept()

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            event.accept()
            return
        self.key_released.emit(event.key())
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        self.mouse_pressed.emit(event.button().value, pos.x(), pos.y())
        self.setFocus()  # keep keyboard focus after a click
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        self.mouse_released.emit(event.button().value, pos.x(), pos.y())
        event.accept()


class _FakeInstance:
    """Minimal stand-in for GameInstance to satisfy action handlers"""

    def __init__(self, name, x, y, simulator, object_data, action_executor):
        self.object_name = name
        self._original_object_name = name
        self.x = x
        self.y = y
        self.xstart = x
        self.ystart = y
        self.rotation = 0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.visible = True
        self.depth = 0
        self.hspeed = 0.0
        self.vspeed = 0.0
        self.gravity = 0.0
        self.friction = 0.0
        self.image_index = 0.0
        self.image_speed = 1.0
        self.to_destroy = False
        self.alarm = [-1] * 12
        self.keys_pressed = set()
        self.is_thymio = True
        self.thymio_simulator = simulator
        self.object_data = object_data
        self._cached_object_data = object_data
        self.action_executor = action_executor
        self.variables = {}
        self._variables = {}  # some handlers use this
        self._pending_destroy = False
        # Room control flags
        self.restart_room_flag = False
        self.next_room_flag = False
        self.previous_room_flag = False
        self.restart_game_flag = False
        self.goto_room_target = None


class PlaygroundRunnerWindow(QMainWindow):
    """
    Runs a playground simulation. Walls become obstacles, robots run their
    linked objects' code.
    """

    def __init__(self, playground_data: dict, project_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Playground - Running"))

        self.playground_data = playground_data
        self.project_data = project_data or {}

        # Arena
        arena = playground_data.get('arena', {})
        self.arena_w = int(arena.get('width', 400))
        self.arena_h = int(arena.get('height', 400))

        # Build obstacle list (axis-aligned bounding boxes of walls)
        self.obstacles = self._build_obstacles(playground_data.get('walls', []))

        # Shared Thymio renderer (also exposes hit_test_button for mouse clicks).
        # Half-scale so multiple robots fit comfortably in a small playground arena.
        self.thymio_renderer = ThymioRenderer(scale=0.5)

        # Tracks Thymio button presses originating from the mouse:
        # {qt_button_int: (instance, button_name)}
        self._thymio_mouse_presses = {}

        # Create ActionExecutor (shared across all robots)
        self.action_executor = ActionExecutor(game_runner=None)
        try:
            register_thymio_actions(self.action_executor)
        except Exception as e:
            logger.warning(f"Could not register Thymio actions: {e}")

        # Create a fake instance for each robot
        self.instances: List[_FakeInstance] = []
        self._create_robots(playground_data.get('robots', []))

        # UI
        self._build_ui()

        # Trigger create events for each robot
        for inst in self.instances:
            events = (inst.object_data or {}).get('events', {})
            if 'create' in events:
                try:
                    self.action_executor.execute_event(inst, 'create', events)
                except Exception as e:
                    logger.error(f"create event failed for {inst.object_name}: {e}")

        # Simulation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.paused = False
        self.timer.start(1000 // FPS)

        logger.info(f"PlaygroundRunner: {len(self.instances)} robot(s), "
                    f"{len(self.obstacles)} obstacles")

    def _build_obstacles(self, walls):
        """Convert walls to axis-aligned bounding boxes (approximation for rotated walls)"""
        obstacles = []
        for w in walls:
            cx, cy = w['x'], w['y']
            l1, l2 = w.get('l1', 10), w.get('l2', 10)
            angle = w.get('angle', 0)
            # Compute AABB of rotated rectangle
            cos_a = abs(math.cos(angle))
            sin_a = abs(math.sin(angle))
            bbox_w = l1 * cos_a + l2 * sin_a
            bbox_h = l1 * sin_a + l2 * cos_a
            rect = pygame.Rect(
                int(cx - bbox_w / 2), int(cy - bbox_h / 2),
                int(bbox_w), int(bbox_h))
            obstacles.append(rect)
        return obstacles

    def _create_robots(self, robots_data):
        """Create a fake instance + simulator for each robot"""
        objects = self.project_data.get('assets', {}).get('objects', {})
        for rd in robots_data:
            name = rd.get('linked_object') or rd.get('name', 'Thymio')
            # Convert editor angle (radians, 0 = right) to simulator angle (degrees, -90 = up)
            angle_deg = math.degrees(rd.get('angle', 0)) - 90
            sim = ThymioSimulator(
                x=rd.get('x', 100),
                y=rd.get('y', 100),
                angle=angle_deg,
            )
            obj_data = objects.get(rd.get('linked_object', ''), {}) if rd.get('linked_object') else {}
            inst = _FakeInstance(
                name=name,
                x=rd.get('x', 100),
                y=rd.get('y', 100),
                simulator=sim,
                object_data=obj_data,
                action_executor=self.action_executor,
            )
            self.instances.append(inst)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Status / info
        info_row = QHBoxLayout()
        self.status_label = QLabel(
            self.tr("Running: {} robots, {} walls").format(
                len(self.instances), len(self.obstacles)))
        info_row.addWidget(self.status_label)
        info_row.addStretch()
        self.pause_btn = QPushButton(self.tr("Pause"))
        self.pause_btn.clicked.connect(self._toggle_pause)
        info_row.addWidget(self.pause_btn)
        reset_btn = QPushButton(self.tr("Reset"))
        reset_btn.clicked.connect(self._reset)
        info_row.addWidget(reset_btn)
        layout.addLayout(info_row)

        # Pygame canvas
        self.canvas = _PygameCanvas(self.arena_w, self.arena_h)
        self.canvas.key_pressed.connect(self._on_key_pressed)
        self.canvas.key_released.connect(self._on_key_released)
        self.canvas.mouse_pressed.connect(self._on_mouse_pressed)
        self.canvas.mouse_released.connect(self._on_mouse_released)
        layout.addWidget(self.canvas)

        # Hint
        hint = QLabel(self.tr(
            "Arrow keys / Space = all robots; click a robot's button = that robot only. "
            "The linked object's code runs automatically."))
        hint.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(hint)

        self.resize(self.arena_w + 40, self.arena_h + 100)
        self.canvas.setFocus()

    # ─── Button event mapping ───────────────────────────────────

    _KEY_EVENT_MAP = {
        Qt.Key_Up: 'thymio_button_forward',
        Qt.Key_Down: 'thymio_button_backward',
        Qt.Key_Left: 'thymio_button_left',
        Qt.Key_Right: 'thymio_button_right',
        Qt.Key_Space: 'thymio_button_center',
    }

    def _on_key_pressed(self, key):
        event_name = self._KEY_EVENT_MAP.get(key)
        if not event_name:
            return
        button = event_name[len('thymio_button_'):]
        # Trigger button event on every Thymio
        for inst in self.instances:
            # Set the held button state so state-polling code (get_button /
            # thymio_if_button_pressed) reads 1, mirroring the mouse path.
            if inst.thymio_simulator is not None:
                inst.thymio_simulator.set_button(button, True)
            events = (inst.object_data or {}).get('events', {})
            if event_name in events:
                try:
                    self.action_executor.execute_event(inst, event_name, events)
                except Exception as e:
                    logger.error(f"Event {event_name} failed: {e}")
            if 'thymio_any_button' in events:
                try:
                    self.action_executor.execute_event(inst, 'thymio_any_button', events)
                except Exception as e:
                    logger.error(f"thymio_any_button failed: {e}")

    def _on_key_released(self, key):
        event_name = self._KEY_EVENT_MAP.get(key)
        if not event_name:
            return
        button = event_name[len('thymio_button_'):]
        for inst in self.instances:
            if inst.thymio_simulator is not None:
                inst.thymio_simulator.set_button(button, False)

    # ─── Mouse → Thymio button hit-testing ──────────────────────

    def _on_mouse_pressed(self, qt_button, x, y):
        """Click on a Thymio's button → fire that robot's button event only."""
        if qt_button != Qt.LeftButton.value:
            return
        for inst in self.instances:
            sim = inst.thymio_simulator
            if sim is None:
                continue
            hit = self.thymio_renderer.hit_test_button(sim.x, sim.y, sim.angle, x, y)
            if not hit:
                continue
            sim.set_button(hit, True)
            self._thymio_mouse_presses[qt_button] = (inst, hit)

            event_name = f"thymio_button_{hit}"
            events = (inst.object_data or {}).get('events', {})
            if event_name in events:
                try:
                    self.action_executor.execute_event(inst, event_name, events)
                except Exception as e:
                    logger.error(f"Event {event_name} failed: {e}")
            if 'thymio_any_button' in events:
                try:
                    self.action_executor.execute_event(inst, 'thymio_any_button', events)
                except Exception as e:
                    logger.error(f"thymio_any_button failed: {e}")
            return

    def _on_mouse_released(self, qt_button, x, y):
        press = self._thymio_mouse_presses.pop(qt_button, None)
        if press is None:
            return
        inst, btn_name = press
        if inst.thymio_simulator:
            inst.thymio_simulator.set_button(btn_name, False)

    # ─── Simulation loop ────────────────────────────────────────

    def _tick(self):
        if self.paused:
            self._render()
            return

        dt = 1.0 / FPS
        for inst in self.instances:
            sim = inst.thymio_simulator
            try:
                thymio_events = sim.update(dt, self.obstacles, self.canvas.get_surface())
            except Exception as e:
                logger.error(f"simulator.update failed: {e}")
                continue

            # Sync position back
            inst.x = sim.x
            inst.y = sim.y
            inst.rotation = (sim.angle + 90) % 360  # simulator uses -90 = up

            # Dispatch sensor/timer events
            events = (inst.object_data or {}).get('events', {})
            for key, ev_name in (
                ('proximity_update', 'thymio_proximity_update'),
                ('ground_update', 'thymio_ground_update'),
                ('timer_0', 'thymio_timer_0'),
                ('timer_1', 'thymio_timer_1'),
                ('sound_finished', 'thymio_sound_finished'),
            ):
                if thymio_events.get(key) and ev_name in events:
                    try:
                        self.action_executor.execute_event(inst, ev_name, events)
                    except Exception as e:
                        logger.error(f"Event {ev_name} failed: {e}")

            # Execute step event every frame
            if 'step' in events:
                try:
                    self.action_executor.execute_event(inst, 'step', events)
                except Exception as e:
                    logger.error(f"step event failed: {e}")

        self._render()

    def _render(self):
        surface = self.canvas.get_surface()
        surface.fill((240, 240, 240))

        # Walls (rotated rectangles)
        for w in self.playground_data.get('walls', []):
            self._draw_wall(surface, w)

        # Robots
        for inst in self.instances:
            self._draw_robot(surface, inst)

        self.canvas.update_display()

    def _draw_wall(self, surface, w):
        """Draw a rotated wall"""
        l1 = w.get('l1', 10)
        l2 = w.get('l2', 10)
        angle = w.get('angle', 0)
        cx = w['x']
        cy = w['y']
        # Compute corners
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        hx, hy = l1 / 2, l2 / 2
        corners = [
            (-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy),
        ]
        pts = []
        for lx, ly in corners:
            wx = cx + lx * cos_a - ly * sin_a
            wy = cy + lx * sin_a + ly * cos_a
            pts.append((int(wx), int(wy)))
        # Color from named palette
        color = self._resolve_color(w.get('color', 'wall'))
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, (0, 0, 0), pts, 1)

    def _draw_robot(self, surface, inst):
        """Draw a Thymio robot using the shared ThymioRenderer.

        This matches the in-game appearance and exposes the 5 buttons for clicking.
        """
        sim = inst.thymio_simulator
        if sim is None:
            return
        self.thymio_renderer.render(surface, sim.get_render_data())

    def _resolve_color(self, name):
        for c in self.playground_data.get('colors', []):
            if c.get('name') == name:
                return (int(c['r'] * 255), int(c['g'] * 255), int(c['b'] * 255))
        return (120, 120, 120)

    # ─── Control buttons ────────────────────────────────────────

    def _toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.setText(self.tr("Resume") if self.paused else self.tr("Pause"))

    def _reset(self):
        """Reset all robots to a fully fresh starting state.

        Rebuild instances and simulators from scratch (same path as init) so
        ALL state resets — not just pose/motors but LEDs, sound, sensors,
        timers, the proximity counter, and any dynamic instance variables.
        The old reset restored only pose + motors, leaving the rest stale.
        """
        self.instances = []
        self._thymio_mouse_presses.clear()
        self._create_robots(self.playground_data.get('robots', []))
        # Re-run create events on the fresh instances
        for inst in self.instances:
            events = (inst.object_data or {}).get('events', {})
            if 'create' in events:
                try:
                    self.action_executor.execute_event(inst, 'create', events)
                except Exception as e:
                    logger.error(f"reset/create failed: {e}")

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)
