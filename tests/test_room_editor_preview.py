"""
Regression test: the RoomEditor exposes generate_room_preview() so the IDE
properties panel's Preview frame can render the room being edited, and the
preview is a FAITHFUL thumbnail of the editor canvas — backgrounds, tiles,
instances and foreground layers — not a simplified re-render.

Before this, RoomEditor had no generate_room_preview method, so the panel's
update_room_preview() fell through to the "Preview Not Available" text — the
preview frame never showed the room. And the standalone RoomPreviewGenerator
it would have used drew only the background colour + instances, dropping tiles
and multi-layer backgrounds. This locks in that:
  * generate_room_preview exists and returns a non-null QPixmap sized to fit,
  * it renders the live canvas (edits/instances are reflected),
  * tiles placed on the canvas actually appear in the preview.

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


def _make_editor(tmp_path):
    from editors.room_editor import RoomEditor
    editor = RoomEditor(str(tmp_path))
    editor.asset_name = "room_test"
    editor.current_room_properties.update({
        'width': 640,
        'height': 480,
        'background_color': '#334455',
    })
    editor.room_canvas.set_room_properties(640, 480, '#334455', '')
    return editor


def test_generate_room_preview_returns_pixmap(_qapp, tmp_path):
    editor = _make_editor(tmp_path)

    pixmap = editor.generate_room_preview(200, 150)

    assert pixmap is not None
    assert not pixmap.isNull(), "preview frame would show nothing"
    # Fits within the requested bounds while preserving the 640x480 aspect ratio.
    assert 0 < pixmap.width() <= 200
    assert 0 < pixmap.height() <= 150


def test_generate_room_preview_reflects_live_instances(_qapp, tmp_path):
    from editors.room_editor.object_instance import ObjectInstance

    editor = _make_editor(tmp_path)

    # Nothing placed yet — the live data the preview draws from is empty.
    assert editor.get_data().get('instances') == []

    # Place an instance directly on the canvas (as clicking would).
    editor.room_canvas.instances.append(ObjectInstance("obj_player", 32, 32))

    data = editor.get_data()
    assert len(data.get('instances', [])) == 1, "canvas edit not seen by preview data"

    # Preview still renders cleanly with an unresolved-sprite instance present.
    pixmap = editor.generate_room_preview(200, 150)
    assert not pixmap.isNull()


def test_generate_room_preview_includes_tiles(_qapp, tmp_path):
    """A tile placed on the canvas must appear in the preview (tiles and all)."""
    from PySide6.QtGui import QPixmap, QColor
    from PySide6.QtCore import Qt

    editor = _make_editor(tmp_path)
    canvas = editor.room_canvas

    # Baseline (no tiles): the top-left corner shows the background colour.
    base = editor.generate_room_preview(200, 150).toImage()
    bg = QColor('#334455')
    base_px = base.pixelColor(4, 4)
    assert abs(base_px.red() - bg.red()) < 20 and abs(base_px.blue() - bg.blue()) < 20, \
        "baseline corner is not the background colour"

    # Place a solid red 64x64 tile at the origin. Pre-seed the crop cache so
    # get_tile_pixmap resolves it without needing a real background image file.
    tile = {'x': 0, 'y': 0, 'width': 64, 'height': 64,
            'background_name': 'bg', 'tile_x': 0, 'tile_y': 0, 'depth': 1000000}
    red_tile = QPixmap(64, 64)
    red_tile.fill(QColor('#FF0000'))
    canvas.tile_pixmap_cache[('bg', 0, 0, 64, 64)] = red_tile
    canvas.tiles.append(tile)
    canvas._tile_layer_dirty = True

    assert editor.get_data().get('tiles'), "tile not present in live data"

    with_tile = editor.generate_room_preview(200, 150).toImage()
    tile_px = with_tile.pixelColor(4, 4)  # inside the scaled tile footprint
    assert tile_px.red() > 150 and tile_px.green() < 100 and tile_px.blue() < 100, \
        f"tile not rendered into preview (got {tile_px.getRgb()})"


def test_generate_room_preview_never_raises_without_project(_qapp, tmp_path):
    editor = _make_editor(tmp_path)
    # No project.json on disk and no IDE parent — must degrade gracefully,
    # not raise, so the panel can always call it.
    pixmap = editor.generate_room_preview(200, 150)
    assert pixmap is not None
