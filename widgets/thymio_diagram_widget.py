#!/usr/bin/env python3
"""
Thymio Diagram Widget
Interactive visual representation of the Thymio robot with clickable regions
for sensors, buttons, LEDs, and motors.
"""

import math
from PySide6.QtWidgets import QWidget, QToolTip
from PySide6.QtCore import Qt, Signal, QRect, QPoint, QRectF
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPainterPath,
    QLinearGradient, QRadialGradient
)


# Thymio physical constants (scaled for display)
DIAGRAM_WIDTH = 280
DIAGRAM_HEIGHT = 240
ROBOT_WIDTH = 140
ROBOT_HEIGHT = 140
ROBOT_CENTER_X = DIAGRAM_WIDTH // 2
ROBOT_CENTER_Y = DIAGRAM_HEIGHT // 2 + 10  # Slightly lower to make room for front sensors

# Colors
COLOR_ROBOT_BODY = QColor(255, 255, 255)
COLOR_ROBOT_OUTLINE = QColor(100, 100, 100)
COLOR_BUTTON = QColor(200, 200, 200)
COLOR_BUTTON_HOVER = QColor(255, 220, 100)
COLOR_SENSOR_PROX = QColor(100, 180, 255)
COLOR_SENSOR_PROX_HOVER = QColor(50, 150, 255)
COLOR_SENSOR_GROUND = QColor(80, 80, 80)
COLOR_SENSOR_GROUND_HOVER = QColor(120, 120, 120)
COLOR_LED = QColor(255, 200, 50)
COLOR_LED_HOVER = QColor(255, 255, 100)
COLOR_MOTOR = QColor(150, 200, 150)
COLOR_MOTOR_HOVER = QColor(100, 220, 100)
COLOR_HIGHLIGHT = QColor(255, 180, 0)
COLOR_WHEEL = QColor(60, 60, 60)


class ThymioDiagramWidget(QWidget):
    """
    Interactive Thymio robot diagram with clickable regions.

    Signals:
        region_clicked(str): Emitted when a region is clicked, with region_id
        region_hovered(str): Emitted when mouse hovers over a region
    """

    region_clicked = Signal(str)
    region_hovered = Signal(str)

    # Region categories for filtering
    REGION_CATEGORIES = {
        'buttons': ['button_forward', 'button_backward', 'button_left',
                    'button_right', 'button_center'],
        'proximity': ['prox_0', 'prox_1', 'prox_2', 'prox_3', 'prox_4',
                      'prox_5', 'prox_6'],
        'ground': ['ground_left', 'ground_right'],
        'leds': ['led_top', 'led_bottom_left', 'led_bottom_right',
                 'led_circle_0', 'led_circle_1', 'led_circle_2', 'led_circle_3',
                 'led_circle_4', 'led_circle_5', 'led_circle_6', 'led_circle_7'],
        'motors': ['motor_left', 'motor_right'],
        'body': ['robot_body']
    }

    # Region descriptions for tooltips
    REGION_DESCRIPTIONS = {
        'button_forward': 'Forward Button',
        'button_backward': 'Backward Button',
        'button_left': 'Left Button',
        'button_right': 'Right Button',
        'button_center': 'Center Button',
        'prox_0': 'Proximity Sensor 0 (Front Left Far)',
        'prox_1': 'Proximity Sensor 1 (Front Left)',
        'prox_2': 'Proximity Sensor 2 (Front Center)',
        'prox_3': 'Proximity Sensor 3 (Front Right)',
        'prox_4': 'Proximity Sensor 4 (Front Right Far)',
        'prox_5': 'Proximity Sensor 5 (Back Left)',
        'prox_6': 'Proximity Sensor 6 (Back Right)',
        'ground_left': 'Ground Sensor (Left)',
        'ground_right': 'Ground Sensor (Right)',
        'led_top': 'Top RGB LED',
        'led_bottom_left': 'Bottom Left LED',
        'led_bottom_right': 'Bottom Right LED',
        'led_circle_0': 'Circle LED 0 (Front)',
        'led_circle_1': 'Circle LED 1',
        'led_circle_2': 'Circle LED 2',
        'led_circle_3': 'Circle LED 3 (Right)',
        'led_circle_4': 'Circle LED 4 (Back)',
        'led_circle_5': 'Circle LED 5',
        'led_circle_6': 'Circle LED 6',
        'led_circle_7': 'Circle LED 7 (Left)',
        'motor_left': 'Left Motor/Wheel',
        'motor_right': 'Right Motor/Wheel',
        'robot_body': 'Robot Body (Tap/Shock sensor)'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
        self.setMaximumSize(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
        self.setMouseTracking(True)

        self.hovered_region = None
        self.highlighted_regions = set()
        self._build_regions()

    def _build_regions(self):
        """Build clickable region rectangles/polygons"""
        self.regions = {}

        cx, cy = ROBOT_CENTER_X, ROBOT_CENTER_Y

        # Button regions (arranged in cross pattern)
        btn_size = 24
        btn_gap = 28
        self.regions['button_forward'] = QRect(cx - btn_size//2, cy - btn_gap - btn_size//2, btn_size, btn_size)
        self.regions['button_backward'] = QRect(cx - btn_size//2, cy + btn_gap - btn_size//2, btn_size, btn_size)
        self.regions['button_left'] = QRect(cx - btn_gap - btn_size//2, cy - btn_size//2, btn_size, btn_size)
        self.regions['button_right'] = QRect(cx + btn_gap - btn_size//2, cy - btn_size//2, btn_size, btn_size)
        self.regions['button_center'] = QRect(cx - btn_size//2, cy - btn_size//2, btn_size, btn_size)

        # Proximity sensors (positioned around front and back)
        # Angles: -45, -25, 0, 25, 45 (front), 165, -165 (back)
        prox_angles = [-45, -25, 0, 25, 45, 165, -165]
        prox_distance = ROBOT_WIDTH // 2 + 5
        prox_size = 18

        for i, angle in enumerate(prox_angles):
            rad = math.radians(angle - 90)  # -90 because 0 is up
            px = cx + int(prox_distance * math.cos(rad))
            py = cy + int(prox_distance * math.sin(rad))
            self.regions[f'prox_{i}'] = QRect(px - prox_size//2, py - prox_size//2, prox_size, prox_size)

        # Ground sensors (below robot, toward front)
        ground_y = cy + 40
        ground_size = 20
        self.regions['ground_left'] = QRect(cx - 35, ground_y, ground_size, ground_size)
        self.regions['ground_right'] = QRect(cx + 15, ground_y, ground_size, ground_size)

        # LED positions
        led_size = 16
        # Top LED (center of robot)
        self.regions['led_top'] = QRect(cx - led_size//2, cy - 50, led_size, led_size)
        # Bottom LEDs
        self.regions['led_bottom_left'] = QRect(cx - 40, cy + 55, led_size, led_size)
        self.regions['led_bottom_right'] = QRect(cx + 24, cy + 55, led_size, led_size)

        # Circle LEDs (8 around the perimeter)
        circle_radius = ROBOT_WIDTH // 2 - 10
        circle_led_size = 12
        for i in range(8):
            angle = math.radians(i * 45 - 90)  # Start from top, go clockwise
            lx = cx + int(circle_radius * math.cos(angle))
            ly = cy + int(circle_radius * math.sin(angle))
            self.regions[f'led_circle_{i}'] = QRect(lx - circle_led_size//2, ly - circle_led_size//2,
                                                     circle_led_size, circle_led_size)

        # Motor/wheel regions (sides of robot)
        wheel_width = 15
        wheel_height = 50
        self.regions['motor_left'] = QRect(cx - ROBOT_WIDTH//2 - wheel_width, cy - wheel_height//2,
                                           wheel_width, wheel_height)
        self.regions['motor_right'] = QRect(cx + ROBOT_WIDTH//2, cy - wheel_height//2,
                                            wheel_width, wheel_height)

        # Robot body (for tap detection) - use a rect that covers the central area
        body_margin = 60
        self.regions['robot_body'] = QRect(cx - body_margin, cy - body_margin,
                                           body_margin * 2, body_margin * 2)

    def paintEvent(self, event):
        """Draw the Thymio robot diagram"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx, cy = ROBOT_CENTER_X, ROBOT_CENTER_Y

        # Draw wheels first (behind body)
        self._draw_wheels(painter, cx, cy)

        # Draw robot body
        self._draw_body(painter, cx, cy)

        # Draw proximity sensors
        self._draw_proximity_sensors(painter)

        # Draw ground sensors
        self._draw_ground_sensors(painter)

        # Draw buttons
        self._draw_buttons(painter)

        # Draw LEDs
        self._draw_leds(painter)

        # Draw labels
        self._draw_labels(painter, cx, cy)

    def _draw_wheels(self, painter, cx, cy):
        """Draw the wheels/motors"""
        for region_id in ['motor_left', 'motor_right']:
            rect = self.regions[region_id]

            if region_id in self.highlighted_regions or region_id == self.hovered_region:
                color = COLOR_MOTOR_HOVER
            else:
                color = COLOR_WHEEL

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(COLOR_ROBOT_OUTLINE, 2))
            painter.drawRoundedRect(rect, 3, 3)

            # Wheel treads
            painter.setPen(QPen(QColor(40, 40, 40), 1))
            for i in range(5):
                y = rect.top() + 8 + i * 9
                painter.drawLine(rect.left() + 2, y, rect.right() - 2, y)

    def _draw_body(self, painter, cx, cy):
        """Draw the robot body"""
        body_rect = QRectF(cx - ROBOT_WIDTH//2, cy - ROBOT_HEIGHT//2, ROBOT_WIDTH, ROBOT_HEIGHT)

        # Gradient for 3D effect
        gradient = QRadialGradient(cx, cy - 20, ROBOT_WIDTH * 0.7)
        gradient.setColorAt(0, QColor(255, 255, 255))
        gradient.setColorAt(1, QColor(230, 230, 230))

        if 'robot_body' in self.highlighted_regions or 'robot_body' == self.hovered_region:
            gradient.setColorAt(0, QColor(255, 255, 200))
            gradient.setColorAt(1, QColor(255, 240, 180))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(COLOR_ROBOT_OUTLINE, 2))
        painter.drawRoundedRect(body_rect, 20, 20)

    def _draw_proximity_sensors(self, painter):
        """Draw proximity sensors"""
        for i in range(7):
            region_id = f'prox_{i}'
            rect = self.regions[region_id]

            if region_id in self.highlighted_regions or region_id == self.hovered_region:
                color = COLOR_SENSOR_PROX_HOVER
            else:
                color = COLOR_SENSOR_PROX

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(50, 100, 180), 1))

            # Draw as small rounded rectangles pointing outward
            painter.drawRoundedRect(rect, 4, 4)

    def _draw_ground_sensors(self, painter):
        """Draw ground sensors"""
        for region_id in ['ground_left', 'ground_right']:
            rect = self.regions[region_id]

            if region_id in self.highlighted_regions or region_id == self.hovered_region:
                color = COLOR_SENSOR_GROUND_HOVER
            else:
                color = COLOR_SENSOR_GROUND

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(40, 40, 40), 1))
            painter.drawRoundedRect(rect, 3, 3)

    def _draw_buttons(self, painter):
        """Draw the 5 capacitive buttons"""
        button_icons = {
            'button_forward': '\u25B2',  # Triangle up
            'button_backward': '\u25BC',  # Triangle down
            'button_left': '\u25C0',  # Triangle left
            'button_right': '\u25B6',  # Triangle right
            'button_center': '\u25CF',  # Circle
        }

        for region_id, icon in button_icons.items():
            rect = self.regions[region_id]

            if region_id in self.highlighted_regions or region_id == self.hovered_region:
                color = COLOR_BUTTON_HOVER
            else:
                color = COLOR_BUTTON

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(COLOR_ROBOT_OUTLINE, 1))
            painter.drawRoundedRect(rect, 5, 5)

            # Draw icon
            painter.setPen(QPen(QColor(60, 60, 60)))
            font = QFont("Arial", 10)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignCenter, icon)

    def _draw_leds(self, painter):
        """Draw LED indicators"""
        # Top LED
        self._draw_led(painter, 'led_top', COLOR_LED)

        # Bottom LEDs
        self._draw_led(painter, 'led_bottom_left', COLOR_LED)
        self._draw_led(painter, 'led_bottom_right', COLOR_LED)

        # Circle LEDs (yellow/orange)
        for i in range(8):
            region_id = f'led_circle_{i}'
            self._draw_led(painter, region_id, QColor(255, 180, 50), size_factor=0.8)

    def _draw_led(self, painter, region_id, base_color, size_factor=1.0):
        """Draw a single LED"""
        rect = self.regions[region_id]

        if region_id in self.highlighted_regions or region_id == self.hovered_region:
            color = COLOR_LED_HOVER
        else:
            color = base_color

        # Glow effect
        center = rect.center()
        gradient = QRadialGradient(center.x(), center.y(), rect.width() * 0.6)
        gradient.setColorAt(0, color.lighter(150))
        gradient.setColorAt(0.5, color)
        gradient.setColorAt(1, color.darker(120))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(color.darker(140), 1))

        # Draw as ellipse
        painter.drawEllipse(rect)

    def _draw_labels(self, painter, cx, cy):
        """Draw descriptive labels"""
        painter.setPen(QPen(QColor(80, 80, 80)))
        font = QFont("Arial", 8)
        painter.setFont(font)

        # Front label
        painter.drawText(cx - 20, 15, "FRONT")

        # Ground sensor labels
        painter.drawText(self.regions['ground_left'].left() - 5,
                        self.regions['ground_left'].bottom() + 12, "GND")
        painter.drawText(self.regions['ground_right'].left() - 5,
                        self.regions['ground_right'].bottom() + 12, "GND")

    def mouseMoveEvent(self, event):
        """Handle mouse movement for hover effects"""
        pos = event.pos()
        new_hover = None

        # Check regions in order of priority (smaller/top items first)
        # Check buttons first (they're on top)
        for region_id in self.REGION_CATEGORIES['buttons']:
            if self.regions[region_id].contains(pos):
                new_hover = region_id
                break

        # Then LEDs
        if not new_hover:
            for region_id in self.REGION_CATEGORIES['leds']:
                if self.regions[region_id].contains(pos):
                    new_hover = region_id
                    break

        # Then sensors
        if not new_hover:
            for region_id in self.REGION_CATEGORIES['proximity'] + self.REGION_CATEGORIES['ground']:
                if self.regions[region_id].contains(pos):
                    new_hover = region_id
                    break

        # Then motors
        if not new_hover:
            for region_id in self.REGION_CATEGORIES['motors']:
                if self.regions[region_id].contains(pos):
                    new_hover = region_id
                    break

        # Finally body
        if not new_hover:
            if self.regions['robot_body'].contains(pos):
                new_hover = 'robot_body'

        if new_hover != self.hovered_region:
            self.hovered_region = new_hover
            self.update()

            if new_hover:
                self.region_hovered.emit(new_hover)
                # Show tooltip
                description = self.REGION_DESCRIPTIONS.get(new_hover, new_hover)
                QToolTip.showText(event.globalPos(), description, self)
            else:
                QToolTip.hideText()

    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.LeftButton and self.hovered_region:
            self.region_clicked.emit(self.hovered_region)

    def leaveEvent(self, event):
        """Handle mouse leaving widget"""
        self.hovered_region = None
        self.update()
        QToolTip.hideText()

    def highlight_region(self, region_id):
        """Highlight a specific region"""
        if region_id in self.regions:
            self.highlighted_regions.add(region_id)
            self.update()

    def highlight_regions(self, region_ids):
        """Highlight multiple regions"""
        for region_id in region_ids:
            if region_id in self.regions:
                self.highlighted_regions.add(region_id)
        self.update()

    def clear_highlights(self):
        """Clear all highlighted regions"""
        self.highlighted_regions.clear()
        self.update()

    def get_regions_by_category(self, category):
        """Get all region IDs for a given category"""
        return self.REGION_CATEGORIES.get(category, [])


# Mapping from diagram regions to Thymio events
REGION_TO_EVENTS = {
    'button_forward': ['thymio_button_forward', 'thymio_any_button'],
    'button_backward': ['thymio_button_backward', 'thymio_any_button'],
    'button_left': ['thymio_button_left', 'thymio_any_button'],
    'button_right': ['thymio_button_right', 'thymio_any_button'],
    'button_center': ['thymio_button_center', 'thymio_any_button'],
    'prox_0': ['thymio_proximity_update'],
    'prox_1': ['thymio_proximity_update'],
    'prox_2': ['thymio_proximity_update'],
    'prox_3': ['thymio_proximity_update'],
    'prox_4': ['thymio_proximity_update'],
    'prox_5': ['thymio_proximity_update'],
    'prox_6': ['thymio_proximity_update'],
    'ground_left': ['thymio_ground_update'],
    'ground_right': ['thymio_ground_update'],
    'robot_body': ['thymio_tap'],
    'led_top': [],  # LEDs don't have events
    'led_bottom_left': [],
    'led_bottom_right': [],
    'motor_left': [],  # Motors don't have events
    'motor_right': [],
}

# Mapping from diagram regions to Thymio actions
REGION_TO_ACTIONS = {
    'button_forward': ['thymio_if_button_pressed', 'thymio_if_button_released', 'thymio_read_button'],
    'button_backward': ['thymio_if_button_pressed', 'thymio_if_button_released', 'thymio_read_button'],
    'button_left': ['thymio_if_button_pressed', 'thymio_if_button_released', 'thymio_read_button'],
    'button_right': ['thymio_if_button_pressed', 'thymio_if_button_released', 'thymio_read_button'],
    'button_center': ['thymio_if_button_pressed', 'thymio_if_button_released', 'thymio_read_button'],
    'prox_0': ['thymio_read_proximity', 'thymio_if_proximity'],
    'prox_1': ['thymio_read_proximity', 'thymio_if_proximity'],
    'prox_2': ['thymio_read_proximity', 'thymio_if_proximity'],
    'prox_3': ['thymio_read_proximity', 'thymio_if_proximity'],
    'prox_4': ['thymio_read_proximity', 'thymio_if_proximity'],
    'prox_5': ['thymio_read_proximity', 'thymio_if_proximity'],
    'prox_6': ['thymio_read_proximity', 'thymio_if_proximity'],
    'ground_left': ['thymio_read_ground', 'thymio_if_ground_dark', 'thymio_if_ground_light'],
    'ground_right': ['thymio_read_ground', 'thymio_if_ground_dark', 'thymio_if_ground_light'],
    'led_top': ['thymio_set_led_top', 'thymio_leds_off'],
    'led_bottom_left': ['thymio_set_led_bottom_left', 'thymio_leds_off'],
    'led_bottom_right': ['thymio_set_led_bottom_right', 'thymio_leds_off'],
    'led_circle_0': ['thymio_set_led_circle', 'thymio_set_led_circle_all', 'thymio_leds_off'],
    'led_circle_1': ['thymio_set_led_circle', 'thymio_set_led_circle_all', 'thymio_leds_off'],
    'led_circle_2': ['thymio_set_led_circle', 'thymio_set_led_circle_all', 'thymio_leds_off'],
    'led_circle_3': ['thymio_set_led_circle', 'thymio_set_led_circle_all', 'thymio_leds_off'],
    'led_circle_4': ['thymio_set_led_circle', 'thymio_set_led_circle_all', 'thymio_leds_off'],
    'led_circle_5': ['thymio_set_led_circle', 'thymio_set_led_circle_all', 'thymio_leds_off'],
    'led_circle_6': ['thymio_set_led_circle', 'thymio_set_led_circle_all', 'thymio_leds_off'],
    'led_circle_7': ['thymio_set_led_circle', 'thymio_set_led_circle_all', 'thymio_leds_off'],
    'motor_left': ['thymio_set_motor_speed', 'thymio_move_forward', 'thymio_move_backward',
                   'thymio_turn_left', 'thymio_turn_right', 'thymio_stop_motors'],
    'motor_right': ['thymio_set_motor_speed', 'thymio_move_forward', 'thymio_move_backward',
                    'thymio_turn_left', 'thymio_turn_right', 'thymio_stop_motors'],
    'robot_body': [],  # Tap is an event, not an action target
}


def get_events_for_region(region_id):
    """Get Thymio events related to a diagram region"""
    return REGION_TO_EVENTS.get(region_id, [])


def get_actions_for_region(region_id):
    """Get Thymio actions related to a diagram region"""
    return REGION_TO_ACTIONS.get(region_id, [])
