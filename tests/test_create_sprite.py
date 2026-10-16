"""Assets > Create Sprite: writes a blank transparent PNG, registers a
sprite asset shaped like an imported one, and opens the sprite editor.
Uses a minimal AssetsMixin double (see test_create_asset_name_validation)."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    yield QApplication.instance() or QApplication([])


class _Host:
    def __init__(self, path):
        self.current_project_path = str(path)
        self.current_project_data = {"assets": {}}
        self.opened = []
        self.added = []
        self.project_manager = SimpleNamespace(
            asset_manager=None, mark_dirty=lambda: None,
            save_project=lambda: True)
        self.asset_tree = SimpleNamespace(
            add_asset=lambda *a: self.added.append(a))

    def tr(self, text):
        return text

    def update_status(self, *_):
        pass

    def _refresh_blockly_asset_lists(self):
        pass

    def open_sprite_editor(self, name, data):
        self.opened.append((name, data))


def _host(path):
    from core.ide._assets import AssetsMixin

    class Host(AssetsMixin, _Host):
        pass

    return Host(path)


def test_create_sprite_writes_blank_png_and_opens_editor(_qapp, tmp_path):
    from PySide6.QtGui import QImage
    host = _host(tmp_path)
    host.create_asset_with_data("sprites", "spr_hero")

    png = tmp_path / "sprites" / "spr_hero.png"
    assert png.exists()
    image = QImage(str(png))
    assert (image.width(), image.height()) == (32, 32)
    assert image.pixelColor(5, 5).alpha() == 0

    data = host.current_project_data["assets"]["sprites"]["spr_hero"]
    assert data["asset_type"] == "sprite"
    assert data["file_path"] == "sprites/spr_hero.png"
    assert data["frames"] == 1 and data["animation_type"] == "single"
    assert host.opened == [("spr_hero", data)]


def test_blank_sprite_loads_in_real_sprite_editor(_qapp, tmp_path):
    from editors.sprite_editor import SpriteEditor
    host = _host(tmp_path)
    data = host._new_blank_sprite_data("spr_a")
    editor = SpriteEditor(str(tmp_path))
    try:
        editor.load_asset("spr_a", data)
        assert editor.frame_timeline.get_frame_size() == (32, 32)
        assert len(editor.frame_timeline.get_frames()) == 1
    finally:
        editor.deleteLater()


def test_assets_menu_has_create_sprite(_qapp):
    from core.ide_window import PyGameMakerIDE
    ide = PyGameMakerIDE()
    try:
        names = [a.objectName() for a in ide._extension_menus["assets"].actions()]
        assert "create_sprite" in names
        assert names.index("create_sprite") < names.index("create_object")
    finally:
        ide.deleteLater()


def test_existing_sprite_name_is_not_overwritten(_qapp, tmp_path, monkeypatch):
    import core.ide._assets as assets_mod
    monkeypatch.setattr(assets_mod.QMessageBox, "warning", lambda *a, **k: None)
    host = _host(tmp_path)
    host.create_asset_with_data("sprites", "spr_hero")
    png = tmp_path / "sprites" / "spr_hero.png"
    png.write_bytes(b"precious")
    host.opened.clear()
    host.create_asset_with_data("sprites", "spr_hero")
    assert png.read_bytes() == b"precious"
    assert host.opened == []
