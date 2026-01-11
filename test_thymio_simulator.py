#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Thymio Simulator
Interactive test of Thymio robot physics and rendering
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from runtime.thymio_simulator import ThymioSimulator
from runtime.thymio_renderer import ThymioRenderer

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BACKGROUND = (50, 50, 50)
COLOR_OBSTACLE = (100, 50, 50)
COLOR_LINE = (20, 20, 20)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Thymio Simulator Test - Arrow Keys: Move, Space: Stop, S: Toggle Sensors")
clock = pygame.time.Clock()

# Create Thymio simulator and renderer
thymio = ThymioSimulator(x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2, angle=0)
renderer = ThymioRenderer()

# Create some test obstacles
obstacles = [
    pygame.Rect(50, 50, 100, 20),     # Top left wall
    pygame.Rect(650, 50, 100, 20),    # Top right wall
    pygame.Rect(50, 530, 100, 20),    # Bottom left wall
    pygame.Rect(650, 530, 100, 20),   # Bottom right wall
    pygame.Rect(300, 200, 200, 20),   # Center obstacle
]

# Create a test line for ground sensors
line_rect = pygame.Rect(100, SCREEN_HEIGHT // 2 - 10, 600, 20)

# Instructions
font = pygame.font.Font(None, 24)
instructions = [
    "Arrow Keys: Control Thymio buttons",
    "Space: Stop motors",
    "S: Toggle sensor visualization",
    "C: Toggle collision box",
    "1-8: Toggle circle LEDs",
    "R/G/B: Set top LED color",
    "ESC: Quit"
]

def draw_background():
    """Draw background with obstacles and line"""
    screen.fill(COLOR_BACKGROUND)

    # Draw obstacles
    for obstacle in obstacles:
        pygame.draw.rect(screen, COLOR_OBSTACLE, obstacle)

    # Draw test line
    pygame.draw.rect(screen, COLOR_LINE, line_rect)

def draw_instructions():
    """Draw instructions on screen"""
    y_offset = 10
    for instruction in instructions:
        text = font.render(instruction, True, (255, 255, 255))
        screen.blit(text, (10, y_offset))
        y_offset += 25

def draw_status():
    """Draw Thymio status info"""
    y_offset = SCREEN_HEIGHT - 120

    # Motor speeds
    left_speed, right_speed = thymio.get_motor_speeds()
    status_lines = [
        f"Position: ({int(thymio.x)}, {int(thymio.y)})",
        f"Angle: {int(thymio.angle)}°",
        f"Motors: L={left_speed}, R={right_speed}",
        f"Prox Center: {thymio.sensors.proximity[2]}",
        f"Ground L/R: {thymio.sensors.ground_delta[0]}/{thymio.sensors.ground_delta[1]}",
    ]

    for line in status_lines:
        text = font.render(line, True, (200, 200, 200))
        screen.blit(text, (10, y_offset))
        y_offset += 22

# Main loop
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # Button simulation
            elif event.key == pygame.K_UP:
                thymio.set_button('forward', True)
                thymio.set_motor_speed(200, 200)
                thymio.set_led_top(0, 32, 0)  # Green
            elif event.key == pygame.K_DOWN:
                thymio.set_button('backward', True)
                thymio.set_motor_speed(-200, -200)
                thymio.set_led_top(32, 16, 0)  # Orange
            elif event.key == pygame.K_LEFT:
                thymio.set_button('left', True)
                thymio.set_motor_speed(0, 300)
                thymio.set_led_top(0, 0, 32)  # Blue
            elif event.key == pygame.K_RIGHT:
                thymio.set_button('right', True)
                thymio.set_motor_speed(300, 0)
                thymio.set_led_top(32, 0, 32)  # Magenta
            elif event.key == pygame.K_SPACE:
                thymio.set_button('center', True)
                thymio.set_motor_speed(0, 0)
                thymio.set_led_top(32, 0, 0)  # Red

            # Toggle visualizations
            elif event.key == pygame.K_s:
                renderer.toggle_sensors()
            elif event.key == pygame.K_c:
                renderer.toggle_collision_box()

            # Circle LED control (keys 1-8)
            elif pygame.K_1 <= event.key <= pygame.K_8:
                led_index = event.key - pygame.K_1
                current = thymio.leds.circle[led_index]
                thymio.set_led_circle(led_index, 0 if current > 0 else 32)

            # Top LED color control
            elif event.key == pygame.K_r:
                thymio.set_led_top(32, 0, 0)  # Red
            elif event.key == pygame.K_g:
                thymio.set_led_top(0, 32, 0)  # Green
            elif event.key == pygame.K_b:
                thymio.set_led_top(0, 0, 32)  # Blue

        elif event.type == pygame.KEYUP:
            # Release buttons
            if event.key == pygame.K_UP:
                thymio.set_button('forward', False)
            elif event.key == pygame.K_DOWN:
                thymio.set_button('backward', False)
            elif event.key == pygame.K_LEFT:
                thymio.set_button('left', False)
            elif event.key == pygame.K_RIGHT:
                thymio.set_button('right', False)
            elif event.key == pygame.K_SPACE:
                thymio.set_button('center', False)

    # Update simulator
    events = thymio.update(dt, obstacles, screen)

    # Check for events
    if events['proximity_update']:
        # Check front sensor for obstacle
        if thymio.sensors.proximity[2] > 2000:
            print(f"⚠️  Obstacle detected! Distance: {thymio.sensors.proximity[2]}")

    if events['ground_update']:
        # Check if on dark line
        if thymio.sensors.ground_delta[0] < 300 or thymio.sensors.ground_delta[1] < 300:
            print(f"📍 On line! L={thymio.sensors.ground_delta[0]}, R={thymio.sensors.ground_delta[1]}")

    # Draw everything
    draw_background()

    # Render Thymio
    render_data = thymio.get_render_data()
    renderer.render(screen, render_data)

    # Draw UI
    draw_instructions()
    draw_status()

    # Update display
    pygame.display.flip()

# Cleanup
pygame.quit()
print("Test complete!")
