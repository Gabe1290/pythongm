"""Regression tests for Thymio simulator geometry (audits M55, M56).

M55: ground sensors sampled 40px to the robot's lateral side (offsets
transposed for the rotation formula) instead of in front, disagreeing with the
front-mounted rendered indicators and breaking line following.

M56: the differential-drive rotation used the y-up "(right - left)" sign, so in
the y-down screen frame "Turn Left" (right wheel only) rotated the robot right.
"""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest

pygame = pytest.importorskip("pygame")

from runtime.thymio_simulator import (
    ThymioSimulator, GROUND_SENSOR_POSITIONS, GROUND_SENSOR_OFFSET,
)


def test_ground_sensor_offsets_are_forward_first():
    # Forward component (GROUND_SENSOR_OFFSET) must be first for the rotation
    # formula; lateral offsets second.
    for forward, lateral in GROUND_SENSOR_POSITIONS:
        assert forward == GROUND_SENSOR_OFFSET
        assert lateral in (-20, 20)


def test_ground_sensor_samples_in_front():
    pygame.init()
    surface = pygame.Surface((300, 300))
    surface.fill((255, 255, 255))  # white table
    # Paint a black patch in FRONT of a robot at (150,150) facing +x (right):
    # front is +x, so x in [180..200], y around 150.
    for x in range(175, 205):
        for y in range(120, 180):
            surface.set_at((x, y), (0, 0, 0))

    sim = ThymioSimulator(x=150, y=150, angle=0)
    sim.update_ground_sensors(surface)

    # Both front ground sensors sit over the black patch -> dark reading.
    assert sim.sensors.ground_delta[0] < 200
    assert sim.sensors.ground_delta[1] < 200


def test_turn_left_rotates_left_on_screen():
    # execute_thymio_turn_left issues set_motor_speed(0, 300) (right wheel).
    # In the y-down screen frame, that must curve the robot toward its LEFT,
    # i.e. the angle decreases (toward -y / up when facing +x).
    sim = ThymioSimulator(x=100, y=100, angle=0)
    sim.set_motor_speed(0, 300)
    for _ in range(10):
        sim.update_physics(dt=1 / 60)
    assert sim.angle < 0, f"turn-left should decrease angle, got {sim.angle}"


def test_turn_right_rotates_opposite():
    sim = ThymioSimulator(x=100, y=100, angle=0)
    sim.set_motor_speed(300, 0)  # left wheel only -> turn right
    for _ in range(10):
        sim.update_physics(dt=1 / 60)
    assert sim.angle > 0
