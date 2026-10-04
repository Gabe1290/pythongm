#!/usr/bin/env python3
"""Simulation stepping/default world layout for :class:`ThymioPlaygroundWindow`.

Extracted verbatim from ``extensions/thymio/playground_window.py``
(``docs/PROJECT_STATUS.md``'s Thymio-extraction follow-up). A mixin --
``self`` / ``self.tr()`` / siblings (``screen_to_world``, ``_get_draw_rect``,
``_apply_zoom_and_pan``, ``_update_status_panel``, ``_check_proximity_warnings``,
...) resolve on the concrete window via MRO.
"""
import pygame

from core.logger import get_logger
from extensions.thymio.editor._constants import (
    COLOR_BACKGROUND, COLOR_GRID, COLOR_LINE, COLOR_OBSTACLE,
    COLOR_SELECTION, MIN_ELEMENT_SIZE, FPS, EditMode,
)

logger = get_logger(__name__)


class SimulationMixin:
    """The default obstacle/line layout, the per-frame simulation update
    (drawing the world, stepping the simulator, applying zoom/pan), and the
    robot/world reset and pause actions."""

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

        # Reuse world surface (cleared each frame instead of reallocated)
        world_surface = self._world_surface
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

    def _draw_grid(self, surface: pygame.Surface):
        """Draw a subtle background grid"""
        grid_size = 50
        for x in range(0, self.playground_width, grid_size):
            pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, self.playground_height))
        for y in range(0, self.playground_height, grid_size):
            pygame.draw.line(surface, COLOR_GRID, (0, y), (self.playground_width, y))

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

    def toggle_pause(self):
        """Toggle simulation pause"""
        self.paused = not self.paused
        self.pause_action.setChecked(self.paused)
        state = self.tr("paused") if self.paused else self.tr("running")
        self.statusbar.showMessage(self.tr("Simulation {0}").format(state))
