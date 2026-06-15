"""Regression tests for audit findings M55 and M56 in runtime/thymio_simulator.py.

M55 — ground sensors must sample in FRONT of the robot (matching the rendered
       indicators), not 90 degrees off to the side.
M56 — differential-drive rotation sign: 'Turn Left' (right motor on, left
       stopped) must rotate the on-screen robot toward its LEFT, not its right.

These exercise pure physics/geometry; no Qt or display needed beyond a dummy
pygame surface.
"""

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from runtime.thymio_simulator import (
    ThymioSimulator,
    GROUND_SENSOR_POSITIONS,
    GROUND_SENSOR_OFFSET,
)


def _sample_positions(sim):
    """Replicate the world-space sensor positions update_ground_sensors computes."""
    angle_rad = math.radians(sim.angle)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    positions = []
    for (offset_x, offset_y) in GROUND_SENSOR_POSITIONS:
        sx = sim.x + (offset_x * cos_a - offset_y * sin_a)
        sy = sim.y + (offset_x * sin_a + offset_y * cos_a)
        positions.append((sx, sy))
    return positions


# ---------------------------------------------------------------------------
# M55: ground sensors sample in front of the robot
# ---------------------------------------------------------------------------

def test_ground_sensors_sample_in_front_facing_right():
    """Facing +x (angle 0), both ground sensors must be ahead of center on x."""
    sim = ThymioSimulator(x=100, y=100, angle=0)
    (lx, ly), (rx, ry) = _sample_positions(sim)

    # Forward axis is +x; both sample points must be GROUND_SENSOR_OFFSET ahead.
    assert lx == pytest.approx(100 + GROUND_SENSOR_OFFSET)
    assert rx == pytest.approx(100 + GROUND_SENSOR_OFFSET)
    # Lateral spread straddles the center line (left negative, right positive).
    assert ly < 100 < ry
    # And the points are NOT off to the lateral side as in the old transposed
    # constants (which would have put them at x = 80 / 120, y = 140).
    assert lx > 100 and rx > 100


def test_ground_sensors_track_heading():
    """Facing down (+y, angle 90) the sensors must lie below the robot."""
    sim = ThymioSimulator(x=100, y=100, angle=90)
    (lx, ly), (rx, ry) = _sample_positions(sim)
    # Forward is now +y, so both samples must be ahead on y.
    assert ly == pytest.approx(100 + GROUND_SENSOR_OFFSET)
    assert ry == pytest.approx(100 + GROUND_SENSOR_OFFSET)


def test_ground_sensor_constants_forward_first():
    """The constants must encode (forward, lateral) with forward = the offset."""
    for forward, lateral in GROUND_SENSOR_POSITIONS:
        assert forward == GROUND_SENSOR_OFFSET
        assert abs(lateral) == 20


def test_ground_sensor_reads_line_under_front():
    """A black line drawn under the robot's FRONT must darken the sensors."""
    surf = pygame.Surface((300, 300))
    surf.fill((255, 255, 255))
    sim = ThymioSimulator(x=100, y=100, angle=0)
    # Paint a dark patch where the front sensors actually sample.
    for (sx, sy) in _sample_positions(sim):
        surf.set_at((int(sx), int(sy)), (0, 0, 0))
    sim.update_ground_sensors(surf)
    # Dark surface -> low delta values; white default would be ~1020.
    assert sim.sensors.ground_delta[0] < 50
    assert sim.sensors.ground_delta[1] < 50


# ---------------------------------------------------------------------------
# M56: differential-drive rotation sign
# ---------------------------------------------------------------------------

def test_turn_left_rotates_toward_left_on_screen():
    """set_motor_speed(0, speed) (the Turn Left handler) must turn toward left.

    On the y-down screen, the robot's left when facing +x is -y. Running only
    the right wheel must pivot the nose toward -y, i.e. the angle must DECREASE
    (the renderer draws the body rotated by -angle, so a decreasing angle is a
    counter-clockwise / left turn on screen) and the robot must curve upward.
    """
    sim = ThymioSimulator(x=100, y=100, angle=0)
    sim.set_motor_speed(0, 300)  # right wheel only -> Turn Left
    # 10 frames keeps the cumulative rotation (~-72 deg) well clear of the
    # +/-180 wrap so the sign is unambiguous.
    for _ in range(10):
        sim.update_physics()
    assert sim.angle < 0, "Turn Left must decrease angle (turn toward -y / left)"
    assert sim.y < 100, "Turn Left must curve the robot upward (toward its left)"


def test_turn_right_rotates_toward_right_on_screen():
    """set_motor_speed(speed, 0) (Turn Right) must turn toward the robot's right."""
    sim = ThymioSimulator(x=100, y=100, angle=0)
    sim.set_motor_speed(300, 0)  # left wheel only -> Turn Right
    for _ in range(10):
        sim.update_physics()
    assert sim.angle > 0, "Turn Right must increase angle (turn toward +y / right)"
    assert sim.y > 100, "Turn Right must curve the robot downward (toward its right)"


def test_straight_drive_no_rotation():
    """Equal motor speeds must not rotate the robot (sign fix preserves this)."""
    sim = ThymioSimulator(x=100, y=100, angle=0)
    sim.set_motor_speed(300, 300)
    for _ in range(30):
        sim.update_physics()
    assert sim.angle == pytest.approx(0.0)
    assert sim.x > 100  # moved forward
    assert sim.y == pytest.approx(100.0)
