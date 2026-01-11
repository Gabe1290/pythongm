#!/usr/bin/env python3
"""
Thymio Robot Simulator
Provides physics simulation and sensor modeling for Thymio educational robot
"""

import math
import pygame
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass


# ============================================================================
# THYMIO PHYSICAL CONSTANTS
# ============================================================================

# Physical dimensions (in game units, scale: 10 pixels = 1 cm)
THYMIO_WIDTH = 110  # 11 cm = 110 pixels
THYMIO_HEIGHT = 110  # 11 cm = 110 pixels
THYMIO_WHEEL_BASE = 95  # 9.5 cm between wheels

# Motor specifications
MOTOR_SPEED_MAX = 500  # Maximum motor speed units
MOTOR_SPEED_TO_VELOCITY = 20.0 / 500.0  # 500 units = 20 cm/s = 2 pixels/frame at 60fps

# Sensor specifications
PROXIMITY_SENSOR_RANGE = 100  # ~10 cm = 100 pixels
PROXIMITY_SENSOR_MAX_VALUE = 4000  # Maximum sensor reading
GROUND_SENSOR_OFFSET = 40  # Distance from center to ground sensors

# Proximity sensor angles (in degrees, 0 = front)
PROXIMITY_SENSOR_ANGLES = [
    -45,  # 0: Front Left Far
    -25,  # 1: Front Left
    0,    # 2: Front Center
    25,   # 3: Front Right
    45,   # 4: Front Right Far
    165,  # 5: Back Left
    -165, # 6: Back Right
]

# Ground sensor positions relative to center
GROUND_SENSOR_POSITIONS = [
    (-20, GROUND_SENSOR_OFFSET),  # 0: Left sensor
    (20, GROUND_SENSOR_OFFSET),   # 1: Right sensor
]

# LED positions (for visualization)
LED_TOP_POSITION = (0, 0)  # Center of robot
LED_BOTTOM_LEFT_POSITION = (-25, 40)
LED_BOTTOM_RIGHT_POSITION = (25, 40)

# Circle LED positions (8 LEDs around perimeter)
CIRCLE_LED_COUNT = 8
CIRCLE_LED_RADIUS = 50


# ============================================================================
# THYMIO STATE DATA CLASSES
# ============================================================================

@dataclass
class ThymioMotorState:
    """Motor state"""
    left_target: int = 0    # -500 to 500
    right_target: int = 0   # -500 to 500
    left_speed: int = 0     # Actual speed (for future use)
    right_speed: int = 0    # Actual speed (for future use)


@dataclass
class ThymioLEDState:
    """LED state"""
    top: Tuple[int, int, int] = (0, 0, 0)           # RGB (0-32)
    bottom_left: Tuple[int, int, int] = (0, 0, 0)  # RGB (0-32)
    bottom_right: Tuple[int, int, int] = (0, 0, 0) # RGB (0-32)
    circle: List[int] = None                        # 8 LEDs (0-32)

    def __post_init__(self):
        if self.circle is None:
            self.circle = [0] * 8


@dataclass
class ThymioSensorState:
    """Sensor state"""
    proximity: List[int] = None     # 7 sensors (0-4000)
    ground_delta: List[int] = None  # 2 sensors (0-1023)
    buttons: dict = None            # forward, backward, left, right, center (0 or 1)

    def __post_init__(self):
        if self.proximity is None:
            self.proximity = [0] * 7
        if self.ground_delta is None:
            self.ground_delta = [0, 0]
        if self.buttons is None:
            self.buttons = {
                'forward': 0,
                'backward': 0,
                'left': 0,
                'right': 0,
                'center': 0
            }


# ============================================================================
# THYMIO SIMULATOR CLASS
# ============================================================================

class ThymioSimulator:
    """Simulates Thymio robot physics and sensors"""

    def __init__(self, x: float = 0, y: float = 0, angle: float = 0):
        """
        Initialize Thymio simulator

        Args:
            x: Initial X position (pixels)
            y: Initial Y position (pixels)
            angle: Initial angle in degrees (0 = facing right)
        """
        # Position and orientation
        self.x = x
        self.y = y
        self.angle = angle  # Degrees, 0 = right, 90 = down, -90 = up, 180 = left

        # Physical state
        self.motors = ThymioMotorState()
        self.leds = ThymioLEDState()
        self.sensors = ThymioSensorState()

        # Sound state
        self.current_sound_frequency = 0
        self.current_sound_duration = 0  # Frames remaining
        self.sound_playing = False

        # Timer state
        self.timer_period = [0, 0]  # Timer periods in milliseconds
        self.timer_counter = [0, 0]  # Timer counters in milliseconds

        # Collision detection
        self.radius = THYMIO_WIDTH / 2  # Circular collision approximation

        # Update tracking
        self.proximity_update_counter = 0  # Frames since last proximity update
        self.proximity_update_rate = 6     # Update every 6 frames (10 Hz at 60 FPS)

    # ========================================================================
    # MOTOR CONTROL
    # ========================================================================

    def set_motor_speed(self, left: int, right: int):
        """Set motor target speeds (-500 to 500)"""
        self.motors.left_target = max(-500, min(500, left))
        self.motors.right_target = max(-500, min(500, right))

    def get_motor_speeds(self) -> Tuple[int, int]:
        """Get current motor target speeds"""
        return (self.motors.left_target, self.motors.right_target)

    # ========================================================================
    # LED CONTROL
    # ========================================================================

    def set_led_top(self, r: int, g: int, b: int):
        """Set top RGB LED (0-32 each channel)"""
        self.leds.top = (
            max(0, min(32, r)),
            max(0, min(32, g)),
            max(0, min(32, b))
        )

    def set_led_bottom_left(self, r: int, g: int, b: int):
        """Set bottom left RGB LED"""
        self.leds.bottom_left = (
            max(0, min(32, r)),
            max(0, min(32, g)),
            max(0, min(32, b))
        )

    def set_led_bottom_right(self, r: int, g: int, b: int):
        """Set bottom right RGB LED"""
        self.leds.bottom_right = (
            max(0, min(32, r)),
            max(0, min(32, g)),
            max(0, min(32, b))
        )

    def set_led_circle(self, index: int, intensity: int):
        """Set one circle LED (0-7, intensity 0-32)"""
        if 0 <= index < 8:
            self.leds.circle[index] = max(0, min(32, intensity))

    def set_led_circle_all(self, intensities: List[int]):
        """Set all 8 circle LEDs"""
        for i in range(min(8, len(intensities))):
            self.leds.circle[i] = max(0, min(32, intensities[i]))

    def leds_off(self):
        """Turn off all LEDs"""
        self.leds.top = (0, 0, 0)
        self.leds.bottom_left = (0, 0, 0)
        self.leds.bottom_right = (0, 0, 0)
        self.leds.circle = [0] * 8

    # ========================================================================
    # SOUND CONTROL
    # ========================================================================

    def play_tone(self, frequency: int, duration: int):
        """
        Play a tone

        Args:
            frequency: Frequency in Hz
            duration: Duration in 1/60 second units (60 = 1 second)
        """
        self.current_sound_frequency = frequency
        self.current_sound_duration = duration
        self.sound_playing = duration != 0

    def stop_sound(self):
        """Stop currently playing sound"""
        self.sound_playing = False
        self.current_sound_duration = 0

    # ========================================================================
    # PHYSICS UPDATE
    # ========================================================================

    def update_physics(self, dt: float = 1/60):
        """
        Update robot position based on differential drive model

        Args:
            dt: Time step in seconds (default 1/60 for 60 FPS)
        """
        # Convert motor speeds to linear velocities (pixels per frame)
        left_velocity = self.motors.left_target * MOTOR_SPEED_TO_VELOCITY
        right_velocity = self.motors.right_target * MOTOR_SPEED_TO_VELOCITY

        # Differential drive kinematics
        # Linear velocity (forward/backward)
        linear_velocity = (left_velocity + right_velocity) / 2.0

        # Angular velocity (rotation)
        # Positive = clockwise rotation in screen coordinates
        angular_velocity_rad = (right_velocity - left_velocity) / THYMIO_WHEEL_BASE

        # Update angle (convert to degrees)
        self.angle += math.degrees(angular_velocity_rad)

        # Normalize angle to -180 to 180
        while self.angle > 180:
            self.angle -= 360
        while self.angle < -180:
            self.angle += 360

        # Update position
        angle_rad = math.radians(self.angle)
        self.x += linear_velocity * math.cos(angle_rad)
        self.y += linear_velocity * math.sin(angle_rad)

    # ========================================================================
    # SENSOR SIMULATION
    # ========================================================================

    def update_proximity_sensors(self, obstacles: List[pygame.Rect]):
        """
        Update proximity sensors by raycasting to obstacles

        Args:
            obstacles: List of obstacle rectangles to detect
        """
        for i, sensor_angle_offset in enumerate(PROXIMITY_SENSOR_ANGLES):
            # Calculate absolute sensor angle
            sensor_angle = self.angle + sensor_angle_offset
            angle_rad = math.radians(sensor_angle)

            # Raycast from robot center in sensor direction
            distance = self._raycast_distance(
                self.x, self.y,
                math.cos(angle_rad), math.sin(angle_rad),
                obstacles,
                PROXIMITY_SENSOR_RANGE
            )

            # Convert distance to sensor value (closer = higher value)
            if distance < PROXIMITY_SENSOR_RANGE:
                # Inverse relationship: closer objects = higher values
                # At 0 distance: 4000, at max range: 0
                sensor_value = int(PROXIMITY_SENSOR_MAX_VALUE * (1 - distance / PROXIMITY_SENSOR_RANGE))
            else:
                sensor_value = 0

            self.sensors.proximity[i] = sensor_value

    def update_ground_sensors(self, screen: pygame.Surface):
        """
        Update ground sensors by sampling pixel colors under robot

        Args:
            screen: Pygame surface to sample colors from
        """
        for i, (offset_x, offset_y) in enumerate(GROUND_SENSOR_POSITIONS):
            # Calculate sensor world position
            angle_rad = math.radians(self.angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Rotate offset by robot angle
            sensor_x = self.x + (offset_x * cos_a - offset_y * sin_a)
            sensor_y = self.y + (offset_x * sin_a + offset_y * cos_a)

            # Sample pixel color at sensor position
            try:
                # Ensure coordinates are within screen bounds
                sensor_x_int = int(sensor_x)
                sensor_y_int = int(sensor_y)

                if 0 <= sensor_x_int < screen.get_width() and 0 <= sensor_y_int < screen.get_height():
                    pixel_color = screen.get_at((sensor_x_int, sensor_y_int))

                    # Calculate brightness (0-255)
                    brightness = (pixel_color[0] + pixel_color[1] + pixel_color[2]) / 3

                    # Convert to ground sensor delta value
                    # Bright surface (white/table): ~1000
                    # Dark surface (black line): ~100
                    # Delta = reflected - ambient (simplified: use brightness directly)
                    self.sensors.ground_delta[i] = int(brightness * 4)  # Scale to 0-1020
                else:
                    # Out of bounds = assume white surface
                    self.sensors.ground_delta[i] = 1000
            except:
                # Error sampling = assume white surface
                self.sensors.ground_delta[i] = 1000

    def _raycast_distance(self, x: float, y: float, dx: float, dy: float,
                          obstacles: List[pygame.Rect], max_distance: float) -> float:
        """
        Cast a ray and return distance to nearest obstacle

        Args:
            x, y: Ray origin
            dx, dy: Ray direction (should be normalized)
            obstacles: List of obstacle rectangles
            max_distance: Maximum ray distance

        Returns:
            Distance to nearest obstacle, or max_distance if none hit
        """
        min_distance = max_distance

        for obstacle in obstacles:
            # Ray-rectangle intersection test
            # Use simple sampling approach: step along ray and check for collision
            step_size = 2  # pixels per step
            steps = int(max_distance / step_size)

            for step in range(steps):
                test_distance = step * step_size
                test_x = x + dx * test_distance
                test_y = y + dy * test_distance

                # Check if point is inside obstacle
                if obstacle.collidepoint(test_x, test_y):
                    min_distance = min(min_distance, test_distance)
                    break

        return min_distance

    # ========================================================================
    # BUTTON CONTROL (for simulation)
    # ========================================================================

    def set_button(self, button: str, pressed: bool):
        """Set button state (for keyboard simulation)"""
        if button in self.sensors.buttons:
            self.sensors.buttons[button] = 1 if pressed else 0

    def get_button(self, button: str) -> int:
        """Get button state (0=released, 1=pressed)"""
        return self.sensors.buttons.get(button, 0)

    # ========================================================================
    # TIMER UPDATE
    # ========================================================================

    def update_timers(self, dt_ms: float) -> Set[int]:
        """
        Update timers and return set of timers that expired

        Args:
            dt_ms: Time step in milliseconds

        Returns:
            Set of timer IDs that expired this frame (0 or 1)
        """
        expired = set()

        for i in range(2):
            if self.timer_period[i] > 0:
                self.timer_counter[i] += dt_ms
                if self.timer_counter[i] >= self.timer_period[i]:
                    self.timer_counter[i] = 0
                    expired.add(i)

        return expired

    def set_timer_period(self, timer_id: int, period_ms: int):
        """Set timer period in milliseconds"""
        if 0 <= timer_id < 2:
            self.timer_period[timer_id] = max(0, period_ms)
            self.timer_counter[timer_id] = 0

    # ========================================================================
    # SOUND UPDATE
    # ========================================================================

    def update_sound(self) -> bool:
        """
        Update sound playback state

        Returns:
            True if sound just finished this frame
        """
        if self.sound_playing and self.current_sound_duration > 0:
            self.current_sound_duration -= 1
            if self.current_sound_duration == 0:
                self.sound_playing = False
                return True  # Sound finished
        return False

    # ========================================================================
    # COLLISION DETECTION
    # ========================================================================

    def get_bounding_rect(self) -> pygame.Rect:
        """Get bounding rectangle for collision detection"""
        return pygame.Rect(
            self.x - THYMIO_WIDTH / 2,
            self.y - THYMIO_HEIGHT / 2,
            THYMIO_WIDTH,
            THYMIO_HEIGHT
        )

    def check_collision_with_obstacles(self, obstacles: List[pygame.Rect]) -> bool:
        """Check if robot collides with any obstacles"""
        robot_rect = self.get_bounding_rect()
        for obstacle in obstacles:
            if robot_rect.colliderect(obstacle):
                return True
        return False

    # ========================================================================
    # FULL UPDATE
    # ========================================================================

    def update(self, dt: float, obstacles: List[pygame.Rect], screen: pygame.Surface) -> dict:
        """
        Full update of simulator (call once per frame)

        Args:
            dt: Time step in seconds
            obstacles: List of obstacle rectangles
            screen: Pygame surface for ground sensor sampling

        Returns:
            Dictionary of events that occurred this frame
        """
        events = {
            'proximity_update': False,
            'ground_update': False,
            'timer_0': False,
            'timer_1': False,
            'sound_finished': False,
            'tap': False  # Future: detect collisions as taps
        }

        # Update physics
        self.update_physics(dt)

        # Update sensors (at appropriate rates)
        self.proximity_update_counter += 1
        if self.proximity_update_counter >= self.proximity_update_rate:
            self.proximity_update_counter = 0
            self.update_proximity_sensors(obstacles)
            self.update_ground_sensors(screen)
            events['proximity_update'] = True
            events['ground_update'] = True

        # Update timers
        dt_ms = dt * 1000  # Convert to milliseconds
        expired_timers = self.update_timers(dt_ms)
        if 0 in expired_timers:
            events['timer_0'] = True
        if 1 in expired_timers:
            events['timer_1'] = True

        # Update sound
        if self.update_sound():
            events['sound_finished'] = True

        return events

    # ========================================================================
    # RENDERING HELPERS
    # ========================================================================

    def get_render_data(self) -> dict:
        """Get data for rendering (used by renderer)"""
        return {
            'position': (self.x, self.y),
            'angle': self.angle,
            'leds': {
                'top': self.leds.top,
                'bottom_left': self.leds.bottom_left,
                'bottom_right': self.leds.bottom_right,
                'circle': self.leds.circle.copy()
            },
            'sensors': {
                'proximity': self.sensors.proximity.copy(),
                'ground': self.sensors.ground_delta.copy()
            },
            'motors': {
                'left': self.motors.left_target,
                'right': self.motors.right_target
            }
        }
