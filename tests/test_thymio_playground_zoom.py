"""Regression tests for Thymio Playground zoom-out rendering.

Audit H15 (docs/FULL_AUDIT_2026-06-11.md): for zoom_level < 1.0 the view
rect exceeded the world surface, so world_surface.subsurface() raised
ValueError on every QTimer tick and the simulator view froze after a
single '-' press.
"""

import pygame
import pytest

from widgets.thymio_playground import ThymioPlaygroundWindow


@pytest.fixture
def playground(qapp):
    window = ThymioPlaygroundWindow()
    window.timer.stop()  # tests drive rendering directly
    yield window
    window.deleteLater()


def _render(window):
    display = pygame.Surface((window.playground_width, window.playground_height))
    window._apply_zoom_and_pan(window._world_surface, display)
    return display


class TestZoomOutRendering:
    def test_zoom_below_one_does_not_raise(self, playground):
        playground.zoom_level = 0.9  # one '-' press from default
        _render(playground)  # raised ValueError before the fix

    def test_minimum_zoom_does_not_raise(self, playground):
        playground.zoom_level = playground.zoom_min  # 0.25 via slider
        _render(playground)

    def test_zoom_out_action_path(self, playground):
        playground.zoom_out()  # the '-' shortcut path
        assert playground.zoom_level < 1.0
        _render(playground)

    def test_zoom_in_path_still_works(self, playground):
        playground.zoom_level = 2.0
        _render(playground)


class TestZoomOutCoordinates:
    def test_roundtrip_at_half_zoom(self, playground):
        playground.zoom_level = 0.5
        for world_pt in [(0, 0), (400, 300), (799, 599)]:
            sx, sy = playground.world_to_screen(*world_pt)
            wx, wy = playground.screen_to_world(sx, sy)
            assert abs(wx - world_pt[0]) <= 2
            assert abs(wy - world_pt[1]) <= 2

    def test_world_center_maps_to_screen_center(self, playground):
        playground.zoom_level = 0.5
        cx, cy = (playground.playground_width // 2,
                  playground.playground_height // 2)
        sx, sy = playground.world_to_screen(cx, cy)
        assert abs(sx - cx) <= 2
        assert abs(sy - cy) <= 2
