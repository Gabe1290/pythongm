#!/usr/bin/env python3
"""
Thymio Playground Window
A standalone simulator window for testing Thymio robot programs.
Embeds pygame rendering in a Qt window.

Split into mixins (``docs/PROJECT_STATUS.md``'s Thymio-extraction follow-up,
"splitting widgets/thymio_playground.py into smaller modules") following the
exact pattern ``core/ide_window.py`` used for its own File 2 split
(``docs/POST_1_0_REFACTOR.md``): each ``extensions/thymio/editor/_*.py``
defines one ``*Mixin`` class; methods moved verbatim, so ``self`` /
``self.tr()`` and every signal/slot wiring keep resolving on the concrete
window via MRO. This file stays the shell -- ``__init__``/``setup_ui``/
``_create_control_panel``/``setup_toolbar``/``setup_statusbar``/
``closeEvent`` -- and the class composes every mixin. Shared constants
(``EditMode``, colors, size presets, ...) live in ``extensions/thymio/
editor/_constants.py`` rather than here, since several mixins need them and
importing them back from this module at mixin-import time would be a
circular import (this module is still mid-import at that point).
"""

import os
from typing import List, Optional, Tuple

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QSpinBox,
    QStatusBar, QToolBar
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QAction, QActionGroup

# Import pygame for the playground
# Note: We need 'dummy' driver for embedded rendering in Qt, but we must NOT
# override SDL_VIDEODRIVER if running in a game subprocess (which needs 'x11')
# The game runner sets SDL_VIDEODRIVER before importing, so we check for that
_original_sdl_driver = os.environ.get('SDL_VIDEODRIVER')
if _original_sdl_driver not in ('x11', 'windows', 'cocoa'):
    # Only set dummy if not already set to a real display driver
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame

from extensions.thymio.simulator import ThymioSimulator
from extensions.thymio.renderer import ThymioRenderer
from widgets.pygame_widget import PygameWidget

from extensions.thymio.editor._constants import (
    DEFAULT_PLAYGROUND_WIDTH, DEFAULT_PLAYGROUND_HEIGHT, FPS,
    SIZE_PRESETS, EditMode,
)
from extensions.thymio.editor._camera import CameraMixin
from extensions.thymio.editor._simulation import SimulationMixin
from extensions.thymio.editor._status import StatusMixin
from extensions.thymio.editor._input import InputMixin
from extensions.thymio.editor._resize import ResizeMixin
from extensions.thymio.editor._undo import UndoMixin

from core.logger import get_logger
logger = get_logger(__name__)


class ThymioPlaygroundWindow(CameraMixin, SimulationMixin, StatusMixin,
                              InputMixin, ResizeMixin, UndoMixin, QMainWindow):
    """
    Standalone Thymio Playground window.
    Features:
    - Interactive Thymio robot simulation
    - Keyboard controls for buttons
    - Obstacle visualization
    - Sensor feedback display
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Free the window (pygame surfaces, simulator, undo stack) when closed.
        # Without this, being parented to the long-lived IDE kept every closed
        # instance alive until IDE exit (closeEvent already stops the timer) (L4).
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(self.tr("Thymio Playground"))
        self.setMinimumSize(900, 700)

        # Playground size (instance variables, not constants)
        self.playground_width = DEFAULT_PLAYGROUND_WIDTH
        self.playground_height = DEFAULT_PLAYGROUND_HEIGHT

        # Initialize simulator and renderer
        self.thymio = ThymioSimulator(
            x=self.playground_width // 2,
            y=self.playground_height // 2,
            angle=-90  # Facing up
        )
        self.renderer = ThymioRenderer()

        # Obstacles list
        self.obstacles: List[pygame.Rect] = []
        self._create_default_obstacles()

        # Line track
        self.line_rects: List[pygame.Rect] = []
        self._create_default_line()

        # State
        self.running = True
        self.paused = False

        # Edit mode state
        self.edit_mode = EditMode.SELECT
        self.is_drawing = False
        self.draw_start: Optional[Tuple[int, int]] = None
        self.draw_current: Optional[Tuple[int, int]] = None
        self.selected_obstacle: Optional[pygame.Rect] = None
        self.selected_line: Optional[pygame.Rect] = None

        # Undo stack (stores tuples of (action_type, data))
        self.undo_stack: List[Tuple[str, any]] = []
        self.max_undo = 50

        # Reusable world surface (avoids allocating a new Surface every frame)
        self._world_surface = pygame.Surface((self.playground_width, self.playground_height))

        # Zoom and pan state
        self.zoom_level = 1.0
        self.zoom_min = 0.25
        self.zoom_max = 4.0
        self.zoom_step = 0.1
        self.camera_x = 0.0  # Camera offset (pan) in world coordinates
        self.camera_y = 0.0
        self.is_panning = False
        self.pan_start: Optional[Tuple[int, int]] = None
        self.pan_start_camera: Optional[Tuple[float, float]] = None

        # Setup UI
        self.setup_ui()
        self.setup_toolbar()
        self.setup_statusbar()

        # Start update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(1000 // FPS)

        logger.info("Thymio Playground window created")

    def setup_ui(self):
        """Setup the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Left: Pygame display
        left_panel = QVBoxLayout()

        # Pygame widget
        self.pygame_widget = PygameWidget(self.playground_width, self.playground_height)
        self.pygame_widget.key_pressed.connect(self.on_key_pressed)
        self.pygame_widget.key_released.connect(self.on_key_released)
        self.pygame_widget.mouse_pressed.connect(self.on_mouse_pressed)
        self.pygame_widget.mouse_released.connect(self.on_mouse_released)
        self.pygame_widget.mouse_moved.connect(self.on_mouse_moved)
        self.pygame_widget.mouse_wheel.connect(self.on_mouse_wheel)
        left_panel.addWidget(self.pygame_widget)

        # Instructions
        instructions = QLabel(self.tr(
            "Robot: Arrow keys = buttons, Space = stop, R = reset | "
            "Edit: Click+drag to draw, Delete = remove | "
            "Zoom: +/- or scroll, Middle-drag to pan, Home = reset view"
        ))
        instructions.setStyleSheet("color: #666; font-size: 11px;")
        instructions.setWordWrap(True)
        left_panel.addWidget(instructions)

        main_layout.addLayout(left_panel, 1)

        # Right: Control panel
        right_panel = self._create_control_panel()
        main_layout.addWidget(right_panel)

    def _create_control_panel(self) -> QWidget:
        """Create the right-side control panel with collapsible sections"""
        from PySide6.QtWidgets import QToolBox, QComboBox

        panel = QWidget()
        panel.setFixedWidth(200)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Use QToolBox for collapsible sections
        toolbox = QToolBox()
        toolbox.setStyleSheet("""
            QToolBox::tab {
                background: #e0e0e0;
                border-radius: 4px;
                padding: 4px;
                font-weight: bold;
            }
            QToolBox::tab:selected {
                background: #c0c0c0;
            }
        """)

        # ===== ROBOT STATUS SECTION =====
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(4, 4, 4, 4)
        status_layout.setSpacing(2)

        # Position (compact)
        self.pos_label = QLabel("X: 400, Y: 300")
        self.angle_label = QLabel(self.tr("Angle: -90°"))
        status_layout.addWidget(self.pos_label)
        status_layout.addWidget(self.angle_label)

        # Motors (compact, single line)
        motor_layout = QHBoxLayout()
        self.left_motor_label = QLabel(self.tr("L: 0"))
        self.right_motor_label = QLabel(self.tr("R: 0"))
        motor_layout.addWidget(QLabel(self.tr("Motors:")))
        motor_layout.addWidget(self.left_motor_label)
        motor_layout.addWidget(self.right_motor_label)
        motor_layout.addStretch()
        status_layout.addLayout(motor_layout)

        # LED status (compact)
        self.led_top_label = QLabel(self.tr("LED: Off"))
        status_layout.addWidget(self.led_top_label)

        # Keep sensor labels for internal use but don't display them
        self.prox_labels = [QLabel() for _ in range(7)]
        self.ground_left_label = QLabel()
        self.ground_right_label = QLabel()

        toolbox.addItem(status_widget, self.tr("Robot Status"))

        # ===== VIEW SECTION =====
        view_widget = QWidget()
        view_layout = QVBoxLayout(view_widget)
        view_layout.setContentsMargins(4, 4, 4, 4)
        view_layout.setSpacing(4)

        # Zoom slider with label
        self.zoom_label = QLabel(self.tr("Zoom: 100%"))
        view_layout.addWidget(self.zoom_label)

        zoom_slider_layout = QHBoxLayout()
        zoom_slider_layout.addWidget(QLabel("-"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(25, 400)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        zoom_slider_layout.addWidget(self.zoom_slider)
        zoom_slider_layout.addWidget(QLabel("+"))
        view_layout.addLayout(zoom_slider_layout)

        self.pan_label = QLabel(self.tr("Pan: 0, 0"))
        view_layout.addWidget(self.pan_label)

        toolbox.addItem(view_widget, self.tr("View"))

        # ===== SIZE SECTION =====
        size_widget = QWidget()
        size_layout = QVBoxLayout(size_widget)
        size_layout.setContentsMargins(4, 4, 4, 4)
        size_layout.setSpacing(4)

        # Size preset combo box
        self.size_preset_combo = QComboBox()
        self.size_preset_combo.addItem(self.tr("Custom"), None)
        for name, w, h in SIZE_PRESETS:
            self.size_preset_combo.addItem(name, (w, h))
        self.size_preset_combo.setCurrentIndex(2)  # Default: Medium
        self.size_preset_combo.currentIndexChanged.connect(self.on_size_preset_changed)
        size_layout.addWidget(self.size_preset_combo)

        # Custom size (compact horizontal)
        size_custom_layout = QHBoxLayout()
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(200, 2000)
        self.width_spinbox.setValue(self.playground_width)
        self.width_spinbox.setSingleStep(50)
        self.width_spinbox.editingFinished.connect(self.on_custom_size_changed)

        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(200, 1500)
        self.height_spinbox.setValue(self.playground_height)
        self.height_spinbox.setSingleStep(50)
        self.height_spinbox.editingFinished.connect(self.on_custom_size_changed)

        size_custom_layout.addWidget(self.width_spinbox)
        size_custom_layout.addWidget(QLabel("×"))
        size_custom_layout.addWidget(self.height_spinbox)
        size_layout.addLayout(size_custom_layout)

        self.apply_size_btn = QPushButton(self.tr("Apply"))
        self.apply_size_btn.clicked.connect(self.apply_custom_size)
        size_layout.addWidget(self.apply_size_btn)

        toolbox.addItem(size_widget, self.tr("Size"))

        # ===== EDIT MODE SECTION =====
        edit_widget = QWidget()
        edit_layout = QVBoxLayout(edit_widget)
        edit_layout.setContentsMargins(4, 4, 4, 4)
        edit_layout.setSpacing(4)

        self.edit_mode_label = QLabel(self.tr("Mode: Select"))
        edit_layout.addWidget(self.edit_mode_label)

        edit_help = QLabel(self.tr(
            "Click: select | Drag: draw"
        ))
        edit_help.setStyleSheet("font-size: 9px; color: #666;")
        edit_help.setWordWrap(True)
        edit_layout.addWidget(edit_help)

        toolbox.addItem(edit_widget, self.tr("Edit"))

        layout.addWidget(toolbox)

        # ===== ACTION BUTTONS (always visible) =====
        button_layout = QVBoxLayout()
        button_layout.setSpacing(4)

        reset_btn = QPushButton(self.tr("Reset Robot"))
        reset_btn.clicked.connect(self.reset_robot)
        button_layout.addWidget(reset_btn)

        reset_world_btn = QPushButton(self.tr("Reset World"))
        reset_world_btn.clicked.connect(self.reset_world)
        button_layout.addWidget(reset_world_btn)

        toggle_sensors_btn = QPushButton(self.tr("Toggle Sensors"))
        toggle_sensors_btn.clicked.connect(self.toggle_sensors)
        button_layout.addWidget(toggle_sensors_btn)

        layout.addLayout(button_layout)

        return panel

    def setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Edit mode actions (mutually exclusive)
        edit_group = QActionGroup(self)
        edit_group.setExclusive(True)

        self.select_action = QAction(self.tr("Select"), self)
        self.select_action.setCheckable(True)
        self.select_action.setChecked(True)
        self.select_action.setToolTip(self.tr("Select mode - click to select elements, Delete to remove"))
        self.select_action.triggered.connect(lambda: self.set_edit_mode(EditMode.SELECT))
        edit_group.addAction(self.select_action)
        toolbar.addAction(self.select_action)

        self.obstacle_action = QAction(self.tr("Obstacle"), self)
        self.obstacle_action.setCheckable(True)
        self.obstacle_action.setToolTip(self.tr("Draw rectangular obstacles - click and drag"))
        self.obstacle_action.triggered.connect(lambda: self.set_edit_mode(EditMode.OBSTACLE))
        edit_group.addAction(self.obstacle_action)
        toolbar.addAction(self.obstacle_action)

        self.line_action = QAction(self.tr("Line"), self)
        self.line_action.setCheckable(True)
        self.line_action.setToolTip(self.tr("Draw line track segments - click and drag"))
        self.line_action.triggered.connect(lambda: self.set_edit_mode(EditMode.LINE))
        edit_group.addAction(self.line_action)
        toolbar.addAction(self.line_action)

        toolbar.addSeparator()

        # Undo action
        undo_action = QAction(self.tr("Undo"), self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        toolbar.addAction(undo_action)

        # Clear actions
        clear_obstacles_action = QAction(self.tr("Clear Obstacles"), self)
        clear_obstacles_action.triggered.connect(self.clear_obstacles)
        toolbar.addAction(clear_obstacles_action)

        clear_lines_action = QAction(self.tr("Clear Lines"), self)
        clear_lines_action.triggered.connect(self.clear_lines)
        toolbar.addAction(clear_lines_action)

        toolbar.addSeparator()

        # Pause/Resume action
        self.pause_action = QAction(self.tr("Pause"), self)
        self.pause_action.setCheckable(True)
        self.pause_action.triggered.connect(self.toggle_pause)
        toolbar.addAction(self.pause_action)

        # Reset action
        reset_action = QAction(self.tr("Reset Robot"), self)
        reset_action.triggered.connect(self.reset_robot)
        toolbar.addAction(reset_action)

        toolbar.addSeparator()

        # Toggle sensors
        sensors_action = QAction(self.tr("Sensors"), self)
        sensors_action.setCheckable(True)
        sensors_action.setChecked(True)
        sensors_action.triggered.connect(self.toggle_sensors)
        toolbar.addAction(sensors_action)

        toolbar.addSeparator()

        # Zoom controls
        zoom_in_action = QAction(self.tr("Zoom In (+)"), self)
        zoom_in_action.setShortcut("+")
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction(self.tr("Zoom Out (-)"), self)
        zoom_out_action.setShortcut("-")
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

        reset_view_action = QAction(self.tr("Reset View"), self)
        reset_view_action.setShortcut("Home")
        reset_view_action.triggered.connect(self.reset_view)
        toolbar.addAction(reset_view_action)

        fit_view_action = QAction(self.tr("Fit to Window"), self)
        fit_view_action.setShortcut("F")
        fit_view_action.triggered.connect(self.fit_to_window)
        toolbar.addAction(fit_view_action)

    def setup_statusbar(self):
        """Setup the status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage(self.tr("Ready - Use arrow keys to control Thymio"))

    def closeEvent(self, event):
        """Handle window close"""
        self.timer.stop()
        self.running = False
        logger.info("Thymio Playground window closed")
        event.accept()
