#!/usr/bin/env python3
"""
Thymio Playground Window
A standalone simulator window for testing Thymio robot programs.
Embeds pygame rendering in a Qt window.
"""

import sys
import os
from enum import Enum, auto
from typing import List, Optional, Tuple

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGroupBox, QSlider, QSpinBox,
    QSplitter, QStatusBar, QToolBar, QMessageBox, QButtonGroup
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QPoint
from PySide6.QtGui import QImage, QPixmap, QKeyEvent, QAction, QMouseEvent, QActionGroup

# Import pygame (initialize without display for embedding)
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Prevent pygame from creating its own window
import pygame

from runtime.thymio_simulator import ThymioSimulator, THYMIO_WIDTH, THYMIO_HEIGHT
from runtime.thymio_renderer import ThymioRenderer

from core.logger import get_logger
logger = get_logger(__name__)


# Playground constants
DEFAULT_PLAYGROUND_WIDTH = 800
DEFAULT_PLAYGROUND_HEIGHT = 600
FPS = 60

# Size presets (name, width, height)
SIZE_PRESETS = [
    ("Small (400x300)", 400, 300),
    ("Medium (800x600)", 800, 600),
    ("Large (1200x900)", 1200, 900),
    ("Wide (1000x500)", 1000, 500),
    ("Square (600x600)", 600, 600),
]

# Colors
COLOR_BACKGROUND = (240, 240, 240)  # Light gray
COLOR_OBSTACLE = (100, 80, 80)       # Dark red-brown
COLOR_LINE = (30, 30, 30)            # Near black for line following
COLOR_GRID = (220, 220, 220)         # Light gray grid
COLOR_SELECTION = (0, 120, 255)      # Blue selection highlight
COLOR_PREVIEW = (100, 100, 255, 128) # Semi-transparent preview

# Minimum size for obstacles/lines
MIN_ELEMENT_SIZE = 10


class EditMode(Enum):
    """Edit modes for the playground"""
    SELECT = auto()      # Select and move/delete elements
    OBSTACLE = auto()    # Place rectangular obstacles
    LINE = auto()        # Draw line segments for line following


class PygameWidget(QLabel):
    """
    Qt widget that displays a pygame surface.
    Handles keyboard and mouse input and passes it to the playground.
    """

    key_pressed = Signal(int)
    key_released = Signal(int)
    mouse_pressed = Signal(int, int, int)   # x, y, button
    mouse_released = Signal(int, int, int)  # x, y, button
    mouse_moved = Signal(int, int)          # x, y
    mouse_wheel = Signal(int, int, int)     # x, y, delta (positive=up/zoom in)

    def __init__(self, width: int, height: int, parent=None):
        super().__init__(parent)
        self.surface_width = width
        self.surface_height = height

        # Create pygame surface (off-screen rendering)
        pygame.init()
        self.surface = pygame.Surface((width, height))

        # Set fixed size
        self.setFixedSize(width, height)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

        # Style
        self.setStyleSheet("border: 2px solid #888;")

    def get_surface(self) -> pygame.Surface:
        """Get the pygame surface for drawing"""
        return self.surface

    def resize_surface(self, width: int, height: int):
        """Resize the pygame surface and widget"""
        self.surface_width = width
        self.surface_height = height
        self.surface = pygame.Surface((width, height))
        self.setFixedSize(width, height)

    def update_display(self):
        """Convert pygame surface to Qt pixmap and display"""
        # Get raw pixel data from pygame surface
        data = pygame.image.tostring(self.surface, 'RGB')

        # Create QImage from raw data
        image = QImage(data, self.surface_width, self.surface_height,
                       self.surface_width * 3, QImage.Format_RGB888)

        # Convert to pixmap and display
        pixmap = QPixmap.fromImage(image)
        self.setPixmap(pixmap)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events"""
        self.key_pressed.emit(event.key())
        event.accept()

    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release events"""
        self.key_released.emit(event.key())
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events"""
        pos = event.position().toPoint()
        self.mouse_pressed.emit(pos.x(), pos.y(), event.button())
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events"""
        pos = event.position().toPoint()
        self.mouse_released.emit(pos.x(), pos.y(), event.button())
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events"""
        pos = event.position().toPoint()
        self.mouse_moved.emit(pos.x(), pos.y())
        event.accept()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming"""
        pos = event.position().toPoint()
        # angleDelta().y() is positive for scrolling up, negative for down
        delta = event.angleDelta().y()
        self.mouse_wheel.emit(pos.x(), pos.y(), delta)
        event.accept()


class ThymioPlaygroundWindow(QMainWindow):
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

    def _create_default_obstacles(self):
        """Create default obstacle layout"""
        self.obstacles = [
            # Border walls
            pygame.Rect(0, 0, self.playground_width, 10),      # Top
            pygame.Rect(0, self.playground_height - 10, self.playground_width, 10),  # Bottom
            pygame.Rect(0, 0, 10, self.playground_height),     # Left
            pygame.Rect(self.playground_width - 10, 0, 10, self.playground_height),  # Right

            # Some interior obstacles
            pygame.Rect(200, 150, 100, 20),
            pygame.Rect(500, 150, 100, 20),
            pygame.Rect(300, 400, 200, 20),
        ]

    def _create_default_line(self):
        """Create default line-following track"""
        # Simple oval track
        center_x = self.playground_width // 2
        center_y = self.playground_height // 2
        track_width = 15

        # Horizontal lines
        self.line_rects = [
            pygame.Rect(150, center_y - track_width // 2, 500, track_width),
            pygame.Rect(150, center_y + 100 - track_width // 2, 500, track_width),
        ]

        # Vertical connections
        self.line_rects.extend([
            pygame.Rect(150 - track_width // 2, center_y, track_width, 100),
            pygame.Rect(650 - track_width // 2, center_y, track_width, 100),
        ])

    def update_simulation(self):
        """Main simulation update loop"""
        # Get pygame surface (display surface)
        display_surface = self.pygame_widget.get_surface()

        # Create a world surface at the base resolution (we'll zoom into this)
        world_surface = pygame.Surface((self.playground_width, self.playground_height))

        # Clear background
        world_surface.fill(COLOR_BACKGROUND)

        # Draw grid
        self._draw_grid(world_surface)

        # Draw line track
        for line_rect in self.line_rects:
            color = COLOR_LINE
            # Highlight selected line
            if line_rect == self.selected_line:
                pygame.draw.rect(world_surface, COLOR_SELECTION, line_rect.inflate(4, 4), 3)
            pygame.draw.rect(world_surface, color, line_rect)

        # Draw obstacles
        for obstacle in self.obstacles:
            # Highlight selected obstacle
            if obstacle == self.selected_obstacle:
                pygame.draw.rect(world_surface, COLOR_SELECTION, obstacle.inflate(4, 4), 3)
            pygame.draw.rect(world_surface, COLOR_OBSTACLE, obstacle)

        # Draw preview rectangle while drawing (in world coordinates)
        if self.is_drawing and self.draw_start and self.draw_current:
            # Convert screen coords to world coords for preview
            world_start = self.screen_to_world(*self.draw_start)
            world_current = self.screen_to_world(*self.draw_current)
            preview_rect = self._get_draw_rect(world_start, world_current)
            if preview_rect.width >= MIN_ELEMENT_SIZE and preview_rect.height >= MIN_ELEMENT_SIZE:
                # Create semi-transparent preview surface
                preview_surface = pygame.Surface((preview_rect.width, preview_rect.height), pygame.SRCALPHA)
                if self.edit_mode == EditMode.OBSTACLE:
                    preview_surface.fill((100, 80, 80, 128))
                elif self.edit_mode == EditMode.LINE:
                    preview_surface.fill((30, 30, 30, 128))
                world_surface.blit(preview_surface, (preview_rect.x, preview_rect.y))
                pygame.draw.rect(world_surface, COLOR_SELECTION, preview_rect, 2)

        # Only update physics if not paused
        if not self.paused:
            # Update Thymio simulation
            dt = 1.0 / FPS
            events = self.thymio.update(dt, self.obstacles, world_surface)

            # Handle simulation events
            if events.get('proximity_update'):
                self._check_proximity_warnings()

        # Render Thymio (always render even when paused)
        render_data = self.thymio.get_render_data()
        self.renderer.render(world_surface, render_data)

        # Apply zoom and pan to create the final display
        self._apply_zoom_and_pan(world_surface, display_surface)

        # Update Qt display
        self.pygame_widget.update_display()

        # Update status panel
        self._update_status_panel()

    def _apply_zoom_and_pan(self, world_surface: pygame.Surface, display_surface: pygame.Surface):
        """Apply zoom and pan transformation to render world to display"""
        if self.zoom_level == 1.0 and self.camera_x == 0 and self.camera_y == 0:
            # No transformation needed
            display_surface.blit(world_surface, (0, 0))
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

    def _draw_grid(self, surface: pygame.Surface):
        """Draw a subtle background grid"""
        grid_size = 50
        for x in range(0, self.playground_width, grid_size):
            pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, self.playground_height))
        for y in range(0, self.playground_height, grid_size):
            pygame.draw.line(surface, COLOR_GRID, (0, y), (self.playground_width, y))

    # ========================================================================
    # ZOOM AND PAN METHODS
    # ========================================================================

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to world coordinates"""
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
        self.zoom_label.setText(self.tr(f"Zoom: {int(self.zoom_level * 100)}%"))
        self.pan_label.setText(self.tr(f"Pan: {int(self.camera_x)}, {int(self.camera_y)}"))

    def _update_status_panel(self):
        """Update the status panel with current robot state"""
        # Motors
        left, right = self.thymio.get_motor_speeds()
        self.left_motor_label.setText(f"L: {left}")
        self.right_motor_label.setText(f"R: {right}")

        # Proximity sensors
        for i, label in enumerate(self.prox_labels):
            value = self.thymio.sensors.proximity[i]
            names = ["FL", "L", "C", "R", "FR", "BL", "BR"]
            label.setText(f"Prox {names[i]}: {value}")

            # Color code based on value
            if value > 2000:
                label.setStyleSheet("color: red; font-size: 10px;")
            elif value > 500:
                label.setStyleSheet("color: orange; font-size: 10px;")
            else:
                label.setStyleSheet("color: green; font-size: 10px;")

        # Ground sensors
        gl = self.thymio.sensors.ground_delta[0]
        gr = self.thymio.sensors.ground_delta[1]
        self.ground_left_label.setText(f"Ground L: {gl}")
        self.ground_right_label.setText(f"Ground R: {gr}")

        # Color code ground sensors
        self.ground_left_label.setStyleSheet(
            "color: red;" if gl < 300 else "color: green;"
        )
        self.ground_right_label.setStyleSheet(
            "color: red;" if gr < 300 else "color: green;"
        )

        # Position
        self.pos_label.setText(f"X: {int(self.thymio.x)}, Y: {int(self.thymio.y)}")
        self.angle_label.setText(f"Angle: {int(self.thymio.angle)}°")

        # LEDs
        r, g, b = self.thymio.leds.top
        if r > 0 or g > 0 or b > 0:
            self.led_top_label.setText(f"LED: ({r},{g},{b})")
            self.led_top_label.setStyleSheet(
                f"background-color: rgb({r*8}, {g*8}, {b*8}); padding: 2px;"
            )
        else:
            self.led_top_label.setText(self.tr("LED: Off"))
            self.led_top_label.setStyleSheet("")

        # Zoom info
        self.zoom_label.setText(self.tr(f"Zoom: {int(self.zoom_level * 100)}%"))
        self.pan_label.setText(f"Pan: {int(self.camera_x)}, {int(self.camera_y)}")

    def _check_proximity_warnings(self):
        """Check for proximity warnings and update status bar"""
        front_center = self.thymio.sensors.proximity[2]
        if front_center > 3000:
            self.statusbar.showMessage(self.tr("Warning: Obstacle very close!"))
        elif front_center > 2000:
            self.statusbar.showMessage(self.tr("Obstacle detected ahead"))

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

    def reset_robot(self):
        """Reset robot to center position"""
        self.thymio.x = self.playground_width // 2
        self.thymio.y = self.playground_height // 2
        self.thymio.angle = -90  # Facing up
        self.thymio.set_motor_speed(0, 0)
        self.thymio.leds_off()
        self.statusbar.showMessage(self.tr("Robot reset to center"))
        logger.info("Thymio reset to center position")

    def reset_world(self):
        """Reset world to default obstacles and lines"""
        self.obstacles = []
        self.line_rects = []
        self._create_default_obstacles()
        self._create_default_line()
        self.selected_obstacle = None
        self.selected_line = None
        self.undo_stack = []
        self.reset_robot()
        self.statusbar.showMessage(self.tr("World reset to default"))
        logger.info("Thymio Playground world reset")

    def clear_obstacles(self):
        """Clear all interior obstacles (keep walls)"""
        # Store interior obstacles for undo
        interior_obstacles = self.obstacles[4:]
        if interior_obstacles:
            for obs in interior_obstacles:
                self._push_undo('delete_obstacle', obs)
            # Keep only the border walls (first 4)
            self.obstacles = self.obstacles[:4]
            self.selected_obstacle = None
            self.statusbar.showMessage(self.tr("Interior obstacles cleared"))
        else:
            self.statusbar.showMessage(self.tr("No interior obstacles to clear"))

    def toggle_sensors(self):
        """Toggle sensor visualization"""
        self.renderer.toggle_sensors()
        state = "on" if self.renderer.show_sensors else "off"
        self.statusbar.showMessage(self.tr(f"Sensor visualization: {state}"))

    def toggle_pause(self):
        """Toggle simulation pause"""
        self.paused = not self.paused
        self.pause_action.setChecked(self.paused)
        state = "paused" if self.paused else "running"
        self.statusbar.showMessage(self.tr(f"Simulation {state}"))

    # ========================================================================
    # PLAYGROUND SIZE METHODS
    # ========================================================================

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

        # Resize pygame widget
        self.pygame_widget.resize_surface(width, height)

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
            self.tr(f"Playground resized to {width}x{height}")
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

    # ========================================================================
    # EDIT MODE METHODS
    # ========================================================================

    def set_edit_mode(self, mode: EditMode):
        """Set the current edit mode"""
        self.edit_mode = mode
        self.is_drawing = False
        self.draw_start = None
        self.draw_current = None
        self.selected_obstacle = None
        self.selected_line = None

        mode_names = {
            EditMode.SELECT: "Select",
            EditMode.OBSTACLE: "Obstacle",
            EditMode.LINE: "Line"
        }
        self.edit_mode_label.setText(self.tr(f"Mode: {mode_names[mode]}"))
        self.statusbar.showMessage(self.tr(f"Edit mode: {mode_names[mode]}"))

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

    def _push_undo(self, action_type: str, data):
        """Push an action to the undo stack"""
        self.undo_stack.append((action_type, data))
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)

    def undo(self):
        """Undo the last action"""
        if not self.undo_stack:
            self.statusbar.showMessage(self.tr("Nothing to undo"))
            return

        action_type, data = self.undo_stack.pop()

        if action_type == 'add_obstacle':
            if data in self.obstacles:
                self.obstacles.remove(data)
                self.statusbar.showMessage(self.tr("Undid obstacle addition"))
        elif action_type == 'add_line':
            if data in self.line_rects:
                self.line_rects.remove(data)
                self.statusbar.showMessage(self.tr("Undid line addition"))
        elif action_type == 'delete_obstacle':
            self.obstacles.append(data)
            self.statusbar.showMessage(self.tr("Undid obstacle deletion"))
        elif action_type == 'delete_line':
            self.line_rects.append(data)
            self.statusbar.showMessage(self.tr("Undid line deletion"))

    def delete_selected(self):
        """Delete the currently selected element"""
        if self.selected_obstacle:
            if self.selected_obstacle in self.obstacles:
                self.obstacles.remove(self.selected_obstacle)
                self._push_undo('delete_obstacle', self.selected_obstacle)
                self.statusbar.showMessage(self.tr("Obstacle deleted"))
            self.selected_obstacle = None
        elif self.selected_line:
            if self.selected_line in self.line_rects:
                self.line_rects.remove(self.selected_line)
                self._push_undo('delete_line', self.selected_line)
                self.statusbar.showMessage(self.tr("Line segment deleted"))
            self.selected_line = None

    def clear_lines(self):
        """Clear all line segments"""
        if self.line_rects:
            # Store for potential undo
            for line in self.line_rects:
                self._push_undo('delete_line', line)
            self.line_rects = []
            self.selected_line = None
            self.statusbar.showMessage(self.tr("All line segments cleared"))
        else:
            self.statusbar.showMessage(self.tr("No line segments to clear"))

    def closeEvent(self, event):
        """Handle window close"""
        self.timer.stop()
        self.running = False
        logger.info("Thymio Playground window closed")
        event.accept()
