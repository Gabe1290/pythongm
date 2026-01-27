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

# Thymio body colors (realistic Thymio II colors)
COLOR_THYMIO_BODY = (248, 248, 245)       # Off-white body
COLOR_THYMIO_BODY_DARK = (230, 230, 225)  # Slightly darker for depth
COLOR_THYMIO_OUTLINE = (180, 180, 180)    # Light gray outline
COLOR_THYMIO_WHEEL = (50, 50, 50)         # Dark wheels
COLOR_THYMIO_WHEEL_HUB = (80, 80, 80)     # Wheel hub
COLOR_THYMIO_SENSOR_HOUSING = (200, 80, 60)   # Orange-red sensor housing (front)
COLOR_THYMIO_BUTTON_INACTIVE = (220, 220, 215)  # Button when not pressed
COLOR_THYMIO_BUTTON_OUTLINE = (150, 150, 145)   # Button outline

# Sensor visualization colors
COLOR_SENSOR_RAY = (255, 100, 100, 128)   # Semi-transparent red
COLOR_GROUND_SENSOR = (100, 255, 100, 200)  # Semi-transparent green

# Sizes (based on real Thymio proportions - approximately 110x110mm)
THYMIO_WIDTH = 110   # Width (side to side)
THYMIO_HEIGHT = 110  # Height (front to back)
LED_SIZE = 10
CIRCLE_LED_SIZE = 6
CIRCLE_LED_RADIUS = 38

# Wheel dimensions
WHEEL_WIDTH = 12
WHEEL_HEIGHT = 35
WHEEL_OFFSET_X = 50  # Distance from center to wheel

# Button dimensions
BUTTON_SIZE = 14
BUTTON_CENTER_SIZE = 18

# Proximity sensor visualization
SENSOR_RAY_LENGTH = 100
SENSOR_RAY_WIDTH = 2

# Ground sensor visualization
GROUND_SENSOR_SIZE = 8


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
        """Pre-render robot body shape to look like a Thymio II robot (top-down view)

        Robot orientation: facing RIGHT (0 degrees)
        - Front of robot is on the RIGHT side
        - Back of robot is on the LEFT side
        - Left wheel is at TOP
        - Right wheel is at BOTTOM
        """
        # Create surface for robot body (extra space for rotation)
        size = int(THYMIO_WIDTH * 1.5)
        self.body_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        cx = size // 2  # Center x
        cy = size // 2  # Center y

        # Thymio dimensions (roughly 110x110mm, but slightly wider than deep)
        body_w = 50   # Half-width (left-right from center)
        body_h = 45   # Half-height (front-back from center)

        # ====== Draw Wheels (black rectangles on sides) ======
        wheel_w = 8
        wheel_h = 28
        wheel_offset = 42  # Distance from center to wheel

        # Top wheel (left side of robot when facing right)
        pygame.draw.rect(self.body_surface, COLOR_THYMIO_WHEEL,
                        (cx - wheel_h//2, cy - wheel_offset - wheel_w//2, wheel_h, wheel_w),
                        border_radius=2)
        # Bottom wheel (right side of robot)
        pygame.draw.rect(self.body_surface, COLOR_THYMIO_WHEEL,
                        (cx - wheel_h//2, cy + wheel_offset - wheel_w//2, wheel_h, wheel_w),
                        border_radius=2)

        # ====== Draw Main Body ======
        # Thymio shape: rounded rectangle with curved front
        # Use multiple shapes to create the characteristic look

        # Main body rectangle (slightly rounded)
        main_rect = pygame.Rect(cx - body_h, cy - body_w, body_h * 2 - 10, body_w * 2)
        pygame.draw.rect(self.body_surface, COLOR_THYMIO_BODY, main_rect, border_radius=12)

        # Front curved section (semicircle on right side)
        front_center_x = cx + body_h - 15
        pygame.draw.circle(self.body_surface, COLOR_THYMIO_BODY,
                          (front_center_x, cy), body_w - 5)

        # Draw outline
        pygame.draw.rect(self.body_surface, COLOR_THYMIO_OUTLINE, main_rect, width=2, border_radius=12)
        pygame.draw.arc(self.body_surface, COLOR_THYMIO_OUTLINE,
                       (front_center_x - body_w + 5, cy - body_w + 5, (body_w-5)*2, (body_w-5)*2),
                       -math.pi/2, math.pi/2, 2)

        # ====== Front IR Sensor Band (orange/red curved strip) ======
        # This is the distinctive orange front of the Thymio
        sensor_band_color = (220, 100, 70)  # Orange-red

        # Draw arc for sensor housing
        for i in range(5):
            # 5 front sensors spread across the front
            angle = math.radians(-40 + i * 20)  # -40, -20, 0, 20, 40 degrees
            sensor_x = cx + body_h + 3 + int(8 * math.cos(angle))
            sensor_y = cy + int(35 * math.sin(angle))
            pygame.draw.circle(self.body_surface, sensor_band_color, (sensor_x, sensor_y), 7)
            pygame.draw.circle(self.body_surface, (180, 70, 50), (sensor_x, sensor_y), 7, 1)

        # ====== Draw 5 Arrow Buttons on top ======
        btn_color = (230, 230, 225)
        btn_outline = (180, 180, 175)
        btn_size = 10
        btn_center_x = cx - 5  # Buttons slightly toward back

        # Center button (circle)
        pygame.draw.circle(self.body_surface, btn_color, (btn_center_x, cy), 8)
        pygame.draw.circle(self.body_surface, btn_outline, (btn_center_x, cy), 8, 1)

        # Forward button (triangle pointing right/front)
        fwd_x = btn_center_x + 18
        pygame.draw.polygon(self.body_surface, btn_color, [
            (fwd_x + 8, cy),
            (fwd_x - 4, cy - 7),
            (fwd_x - 4, cy + 7)
        ])
        pygame.draw.polygon(self.body_surface, btn_outline, [
            (fwd_x + 8, cy),
            (fwd_x - 4, cy - 7),
            (fwd_x - 4, cy + 7)
        ], 1)

        # Backward button (triangle pointing left/back)
        bwd_x = btn_center_x - 18
        pygame.draw.polygon(self.body_surface, btn_color, [
            (bwd_x - 8, cy),
            (bwd_x + 4, cy - 7),
            (bwd_x + 4, cy + 7)
        ])
        pygame.draw.polygon(self.body_surface, btn_outline, [
            (bwd_x - 8, cy),
            (bwd_x + 4, cy - 7),
            (bwd_x + 4, cy + 7)
        ], 1)

        # Left button (triangle pointing up)
        left_y = cy - 18
        pygame.draw.polygon(self.body_surface, btn_color, [
            (btn_center_x, left_y - 8),
            (btn_center_x - 7, left_y + 4),
            (btn_center_x + 7, left_y + 4)
        ])
        pygame.draw.polygon(self.body_surface, btn_outline, [
            (btn_center_x, left_y - 8),
            (btn_center_x - 7, left_y + 4),
            (btn_center_x + 7, left_y + 4)
        ], 1)

        # Right button (triangle pointing down)
        right_y = cy + 18
        pygame.draw.polygon(self.body_surface, btn_color, [
            (btn_center_x, right_y + 8),
            (btn_center_x - 7, right_y - 4),
            (btn_center_x + 7, right_y - 4)
        ])
        pygame.draw.polygon(self.body_surface, btn_outline, [
            (btn_center_x, right_y + 8),
            (btn_center_x - 7, right_y - 4),
            (btn_center_x + 7, right_y - 4)
        ], 1)

        # ====== Back sensors (2 rear IR sensors) ======
        back_sensor_color = (150, 60, 50)
        # Back left
        pygame.draw.circle(self.body_surface, back_sensor_color, (cx - body_h + 5, cy - 25), 4)
        # Back right
        pygame.draw.circle(self.body_surface, back_sensor_color, (cx - body_h + 5, cy + 25), 4)

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

        # Top LED (center of robot body)
        self._draw_led(screen, x, y, leds['top'], LED_SIZE)

        # Bottom LEDs (underneath, near ground sensors at front)
        # These illuminate the ground
        # Left ground LED
        left_offset = (40, -12)  # Forward and left
        left_x = x + (left_offset[0] * cos_a - left_offset[1] * sin_a)
        left_y = y + (left_offset[0] * sin_a + left_offset[1] * cos_a)
        self._draw_led(screen, left_x, left_y, leds['bottom_left'], LED_SIZE // 2)

        # Right ground LED
        right_offset = (40, 12)  # Forward and right
        right_x = x + (right_offset[0] * cos_a - right_offset[1] * sin_a)
        right_y = y + (right_offset[0] * sin_a + right_offset[1] * cos_a)
        self._draw_led(screen, right_x, right_y, leds['bottom_right'], LED_SIZE // 2)

        # Circle LEDs (8 LEDs around the top edge of the robot)
        # On real Thymio, these form an arc around the curved front
        # Positioned from back-left around front to back-right
        circle_led_radius = 42
        circle_led_angles = [135, 90, 45, 22, 0, -22, -45, -90]  # Around the robot

        for i, led_angle_offset in enumerate(circle_led_angles):
            led_angle = angle + led_angle_offset
            led_angle_rad = math.radians(led_angle)
            led_x = x + circle_led_radius * math.cos(led_angle_rad)
            led_y = y + circle_led_radius * math.sin(led_angle_rad)

            intensity = leds['circle'][i]
            if intensity > 0:
                # Circle LEDs are orange/yellow (Thymio's signature color)
                color = (
                    int(255 * intensity / 32),  # Red
                    int(180 * intensity / 32),  # Green (slightly less for orange)
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
        """Render proximity sensor rays from Thymio's IR sensors"""
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Sensor configurations: (direction_angle, distance_from_center, side_offset)
        # Thymio has 5 front sensors and 2 back sensors
        # Angles are relative to robot's forward direction (0° = straight ahead)
        sensor_configs = [
            (-40, 48, -28),   # prox.horizontal[0] - front far-left
            (-20, 52, -14),   # prox.horizontal[1] - front left
            (0, 55, 0),       # prox.horizontal[2] - front center
            (20, 52, 14),     # prox.horizontal[3] - front right
            (40, 48, 28),     # prox.horizontal[4] - front far-right
            (155, -42, -22),  # prox.horizontal[5] - back left
            (-155, -42, 22),  # prox.horizontal[6] - back right
        ]

        for i, (sensor_angle_offset, forward_offset, side_offset) in enumerate(sensor_configs):
            sensor_value = sensor_values[i]

            # Calculate sensor start position (on robot body edge)
            start_x = x + (forward_offset * cos_a - side_offset * sin_a)
            start_y = y + (forward_offset * sin_a + side_offset * cos_a)

            # Only draw if sensor detects something
            if sensor_value > 100:  # Threshold for visibility
                sensor_angle = angle + sensor_angle_offset
                sensor_angle_rad = math.radians(sensor_angle)

                # Calculate ray end point based on sensor value
                # Higher value = closer obstacle = shorter ray
                ray_length = SENSOR_RAY_LENGTH * (1 - sensor_value / 4500)
                ray_length = max(ray_length, 15)  # Minimum visible length

                end_x = start_x + ray_length * math.cos(sensor_angle_rad)
                end_y = start_y + ray_length * math.sin(sensor_angle_rad)

                # Draw ray with color intensity based on sensor value
                # Orange-red color matching Thymio's sensor housing
                intensity = min(255, 120 + sensor_value // 25)
                color = (intensity, int(intensity * 0.35), 0, 140)

                # Create surface for transparent line
                ray_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                pygame.draw.line(ray_surface, color, (int(start_x), int(start_y)),
                               (int(end_x), int(end_y)), 3)
                screen.blit(ray_surface, (0, 0))

    def _render_ground_sensors(self, screen: pygame.Surface, x: float, y: float,
                                angle: float, sensor_values: List[int]):
        """Render ground sensor indicators at front of robot"""
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Ground sensor positions (at front underside of robot)
        # (forward_offset, side_offset) - positive forward is front, positive side is right
        sensor_positions = [(48, -12), (48, 12)]  # Left, Right at front

        for i, (forward, side) in enumerate(sensor_positions):
            # Calculate sensor world position
            sensor_x = x + (forward * cos_a - side * sin_a)
            sensor_y = y + (forward * sin_a + side * cos_a)

            # Color based on sensor value
            # High value (bright/reflective surface) = green
            # Low value (dark/absorbing surface) = red
            sensor_value = sensor_values[i]
            if sensor_value < 300:
                # Dark surface (on line)
                color = (255, 60, 60, 200)  # Red
            else:
                # Light surface (off line)
                color = (60, 255, 60, 200)  # Green

            # Draw sensor indicator as a small rounded square
            size = GROUND_SENSOR_SIZE
            sensor_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.rect(sensor_surface, color, (0, 0, size * 2, size * 2), border_radius=3)
            screen.blit(sensor_surface, (int(sensor_x - size), int(sensor_y - size)))

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
