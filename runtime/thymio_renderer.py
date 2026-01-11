#!/usr/bin/env python3
"""
Thymio Robot Renderer
Provides visual rendering for simulated Thymio robot
"""

import math
import pygame
from typing import Tuple, List


# ============================================================================
# RENDERING CONSTANTS
# ============================================================================

# Colors
COLOR_THYMIO_BODY = (240, 240, 240)  # Light gray
COLOR_THYMIO_OUTLINE = (100, 100, 100)  # Dark gray
COLOR_SENSOR_RAY = (255, 100, 100, 128)  # Semi-transparent red
COLOR_GROUND_SENSOR = (100, 255, 100, 200)  # Semi-transparent green

# Sizes
THYMIO_WIDTH = 110
THYMIO_HEIGHT = 110
LED_SIZE = 12
CIRCLE_LED_SIZE = 8
CIRCLE_LED_RADIUS = 50

# Proximity sensor visualization
SENSOR_RAY_LENGTH = 100
SENSOR_RAY_WIDTH = 2

# Ground sensor visualization
GROUND_SENSOR_SIZE = 10


class ThymioRenderer:
    """Renders Thymio robot with LEDs and sensor feedback"""

    def __init__(self):
        """Initialize renderer"""
        self.show_sensors = True  # Toggle sensor visualization
        self.show_collision_box = False  # Toggle collision box

        # Pre-render robot body (cache for performance)
        self.body_surface = None
        self._render_body_surface()

    def _render_body_surface(self):
        """Pre-render robot body shape"""
        # Create surface for robot body
        size = int(THYMIO_WIDTH * 1.2)  # Extra space for rotation
        self.body_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        center = size // 2

        # Draw robot body (simplified rectangle with rounded corners)
        body_rect = pygame.Rect(
            center - THYMIO_WIDTH // 2,
            center - THYMIO_HEIGHT // 2,
            THYMIO_WIDTH,
            THYMIO_HEIGHT
        )

        # Draw body
        pygame.draw.rect(self.body_surface, COLOR_THYMIO_BODY, body_rect, border_radius=15)
        pygame.draw.rect(self.body_surface, COLOR_THYMIO_OUTLINE, body_rect, width=3, border_radius=15)

        # Draw front indicator (small triangle at front)
        front_x = center + THYMIO_WIDTH // 2 - 10
        front_y = center
        triangle_points = [
            (front_x, front_y - 8),
            (front_x, front_y + 8),
            (front_x + 10, front_y)
        ]
        pygame.draw.polygon(self.body_surface, COLOR_THYMIO_OUTLINE, triangle_points)

    def render(self, screen: pygame.Surface, thymio_data: dict):
        """
        Render Thymio robot on screen

        Args:
            screen: Pygame surface to render on
            thymio_data: Dictionary from ThymioSimulator.get_render_data()
        """
        x, y = thymio_data['position']
        angle = thymio_data['angle']

        # Render sensor rays (if enabled)
        if self.show_sensors:
            self._render_proximity_sensors(screen, x, y, angle, thymio_data['sensors']['proximity'])
            self._render_ground_sensors(screen, x, y, angle, thymio_data['sensors']['ground'])

        # Render robot body
        self._render_body(screen, x, y, angle)

        # Render LEDs
        self._render_leds(screen, x, y, angle, thymio_data['leds'])

        # Render collision box (if enabled)
        if self.show_collision_box:
            self._render_collision_box(screen, x, y)

    def _render_body(self, screen: pygame.Surface, x: float, y: float, angle: float):
        """Render robot body with rotation"""
        # Rotate body surface
        rotated_body = pygame.transform.rotate(self.body_surface, -angle)  # Negative for correct rotation
        rotated_rect = rotated_body.get_rect(center=(int(x), int(y)))

        # Draw rotated body
        screen.blit(rotated_body, rotated_rect)

    def _render_leds(self, screen: pygame.Surface, x: float, y: float, angle: float, leds: dict):
        """Render all LEDs"""
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Top LED (center of robot)
        self._draw_led(screen, x, y, leds['top'], LED_SIZE)

        # Bottom LEDs
        # Left
        left_x = x + (-25 * cos_a - 40 * sin_a)
        left_y = y + (-25 * sin_a + 40 * cos_a)
        self._draw_led(screen, left_x, left_y, leds['bottom_left'], LED_SIZE // 2)

        # Right
        right_x = x + (25 * cos_a - 40 * sin_a)
        right_y = y + (25 * sin_a + 40 * cos_a)
        self._draw_led(screen, right_x, right_y, leds['bottom_right'], LED_SIZE // 2)

        # Circle LEDs (8 LEDs around perimeter)
        for i in range(8):
            led_angle = angle + (i * 45)  # 45 degrees apart
            led_angle_rad = math.radians(led_angle)
            led_x = x + CIRCLE_LED_RADIUS * math.cos(led_angle_rad)
            led_y = y + CIRCLE_LED_RADIUS * math.sin(led_angle_rad)

            intensity = leds['circle'][i]
            if intensity > 0:
                # Circle LEDs are orange/yellow
                color = (
                    int(255 * intensity / 32),  # Red
                    int(200 * intensity / 32),  # Green
                    0  # Blue
                )
                self._draw_led(screen, led_x, led_y, color, CIRCLE_LED_SIZE)

    def _draw_led(self, screen: pygame.Surface, x: float, y: float, color: Tuple[int, int, int], size: int):
        """Draw a single LED with glow effect"""
        r, g, b = color

        # Skip if LED is off
        if r == 0 and g == 0 and b == 0:
            return

        # Convert 0-32 range to 0-255 for RGB
        if all(c <= 32 for c in (r, g, b)):
            r = int(r * 255 / 32)
            g = int(g * 255 / 32)
            b = int(b * 255 / 32)

        # Draw glow (larger, semi-transparent circle)
        glow_color = (r, g, b, 64)  # Semi-transparent
        glow_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (size * 3 // 2, size * 3 // 2), size * 3 // 2)
        screen.blit(glow_surface, (int(x - size * 3 // 2), int(y - size * 3 // 2)))

        # Draw LED (solid circle)
        pygame.draw.circle(screen, (r, g, b), (int(x), int(y)), size // 2)

    def _render_proximity_sensors(self, screen: pygame.Surface, x: float, y: float,
                                   angle: float, sensor_values: List[int]):
        """Render proximity sensor rays"""
        # Sensor angles (relative to robot)
        sensor_angles = [-45, -25, 0, 25, 45, 165, -165]

        for i, sensor_angle_offset in enumerate(sensor_angles):
            sensor_value = sensor_values[i]

            # Only draw if sensor detects something
            if sensor_value > 100:  # Threshold for visibility
                sensor_angle = angle + sensor_angle_offset
                sensor_angle_rad = math.radians(sensor_angle)

                # Calculate ray end point based on sensor value
                # Higher value = shorter ray (closer obstacle)
                ray_length = SENSOR_RAY_LENGTH * (1 - sensor_value / 4000)

                end_x = x + ray_length * math.cos(sensor_angle_rad)
                end_y = y + ray_length * math.sin(sensor_angle_rad)

                # Draw ray with color intensity based on sensor value
                intensity = min(255, sensor_value // 16)
                color = (intensity, 0, 0, 128)  # Red, semi-transparent

                # Create surface for transparent line
                ray_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                pygame.draw.line(ray_surface, color, (int(x), int(y)), (int(end_x), int(end_y)), SENSOR_RAY_WIDTH)
                screen.blit(ray_surface, (0, 0))

    def _render_ground_sensors(self, screen: pygame.Surface, x: float, y: float,
                                angle: float, sensor_values: List[int]):
        """Render ground sensor indicators"""
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Ground sensor positions
        sensor_positions = [(-20, 40), (20, 40)]  # Left, Right

        for i, (offset_x, offset_y) in enumerate(sensor_positions):
            # Calculate sensor world position
            sensor_x = x + (offset_x * cos_a - offset_y * sin_a)
            sensor_y = y + (offset_x * sin_a + offset_y * cos_a)

            # Color based on sensor value
            # High value (bright surface) = green
            # Low value (dark surface) = red
            sensor_value = sensor_values[i]
            if sensor_value < 300:
                # Dark surface (on line)
                color = (255, 0, 0, 200)  # Red
            else:
                # Light surface (off line)
                color = (0, 255, 0, 200)  # Green

            # Draw sensor indicator
            sensor_surface = pygame.Surface((GROUND_SENSOR_SIZE * 2, GROUND_SENSOR_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.circle(sensor_surface, color, (GROUND_SENSOR_SIZE, GROUND_SENSOR_SIZE), GROUND_SENSOR_SIZE)
            screen.blit(sensor_surface, (int(sensor_x - GROUND_SENSOR_SIZE), int(sensor_y - GROUND_SENSOR_SIZE)))

    def _render_collision_box(self, screen: pygame.Surface, x: float, y: float):
        """Render collision bounding box (for debugging)"""
        rect = pygame.Rect(
            int(x - THYMIO_WIDTH // 2),
            int(y - THYMIO_HEIGHT // 2),
            THYMIO_WIDTH,
            THYMIO_HEIGHT
        )
        pygame.draw.rect(screen, (255, 0, 255), rect, 2)  # Magenta outline

    # ========================================================================
    # TOGGLE FUNCTIONS
    # ========================================================================

    def toggle_sensors(self):
        """Toggle sensor visualization on/off"""
        self.show_sensors = not self.show_sensors

    def toggle_collision_box(self):
        """Toggle collision box visualization on/off"""
        self.show_collision_box = not self.show_collision_box
