"""
Regression test: RoomCanvas clears ALL project-scoped pixmap caches on a
project change.

An audit flagged sprite_cache/origin_cache as "unbounded" — but those are keyed
by asset name (bounded by project size) and were already cleared in
set_project_info. The genuine gap was tile_pixmap_cache (keyed by background
name + tile coords): it is project-scoped like its siblings but was the one
cache never cleared, so it accumulated stale crops across project switches.
This locks in that all three clear together.

Constructs a real (offscreen) QApplication rather than using pytest-qt, so it
runs anywhere PySide6 is installed.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_set_project_info_clears_all_project_scoped_caches(_qapp):
    from editors.room_editor.room_canvas import RoomCanvas

    canvas = RoomCanvas()

    # Simulate a populated canvas from a prior project.
    canvas.sprite_cache["obj_a"] = object()
    canvas.origin_cache["obj_a"] = (3, 4)
    canvas.tile_pixmap_cache[("bg1", 0, 0, 16, 16)] = object()
    canvas._tile_layer_cache = object()
    canvas._tile_layer_dirty = False

    # Switching project must drop every project-scoped cache.
    canvas.set_project_info(None, {"assets": {}})

    assert canvas.sprite_cache == {}
    assert canvas.origin_cache == {}
    assert canvas.tile_pixmap_cache == {}, "tile_pixmap_cache not cleared on project change"
    assert canvas._tile_layer_cache is None
    assert canvas._tile_layer_dirty is True
