#!/usr/bin/env python3
"""Tests for the room canvas instance-dimming overlay.

Regression: the Tile Palette dimming overlay (instances rendered at 20% so
tiles painted under them stay visible) also fired while *placing objects*,
because the dim was driven solely by "a Tile Palette window is open/focused".
Objects dropped onto the canvas appeared at 20% opacity. The dim must stay off
whenever an object is selected for placement.

These only need a QApplication (no pytest-qt / qtbot), so they run wherever
PySide6 is installed.
"""

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def canvas(_qapp):
    from editors.room_editor.room_canvas import RoomCanvas
    return RoomCanvas()


def test_no_dim_when_no_palette_active(canvas):
    """Default state: palette not active -> no dim."""
    assert canvas._should_dim_instances() is False


def test_dim_when_painting_tiles(canvas):
    """Tile Palette active and no object selected -> dim instances."""
    canvas.set_tile_palette_active(True)
    assert canvas.current_object_type is None
    assert canvas._should_dim_instances() is True


def test_no_dim_when_placing_objects(canvas):
    """Object selected for placement -> never dim, even with palette active."""
    canvas.set_tile_palette_active(True)
    canvas.set_current_object_type("obj_player")
    assert canvas._should_dim_instances() is False


def test_dim_returns_after_clearing_object_selection(canvas):
    """Switching from object placement back to tile painting re-enables dim."""
    canvas.set_tile_palette_active(True)
    canvas.set_current_object_type("obj_player")
    assert canvas._should_dim_instances() is False
    # Selecting a tile clears the object type (set_current_tile does this)
    canvas.set_current_tile({
        "background_name": "bg", "tile_x": 0, "tile_y": 0,
        "width": 32, "height": 32,
    })
    assert canvas.current_object_type is None
    assert canvas._should_dim_instances() is True
