"""
Regression tests for asset-name path-traversal hardening in ProjectManager.

Asset names are dict keys taken straight from a project.json. They are used to
build per-asset filenames (rooms/<name>.json, etc.) on both load (read) and
save (write). A maliciously-crafted *shared* project whose asset keys contain
".." would otherwise read/write outside the project directory. _safe_asset_path
blocks that while leaving legitimate names (plain identifiers) untouched.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _make_pm():
    with patch('PySide6.QtCore.QTimer'):
        from core.project_manager import ProjectManager
        pm = ProjectManager(asset_manager=MagicMock())
        pm.auto_save_timer = MagicMock()
        return pm


class TestSafeAssetPath:

    def test_plain_name_ok(self, tmp_path):
        from core.project_manager import _safe_asset_path
        assert _safe_asset_path(tmp_path, "room1") == (tmp_path / "room1.json").resolve()

    def test_custom_suffix(self, tmp_path):
        from core.project_manager import _safe_asset_path
        assert _safe_asset_path(tmp_path, "spr", ".png") == (tmp_path / "spr.png").resolve()

    @pytest.mark.parametrize("evil", [
        "../../../../tmp/evil",
        "../escape",
        "/abs/escape",
    ])
    def test_traversal_blocked(self, tmp_path, evil):
        from core.project_manager import _safe_asset_path
        assert _safe_asset_path(tmp_path, evil) is None

    def test_subdir_within_base_allowed(self, tmp_path):
        # A name with an inner ".." that still resolves inside base is fine.
        from core.project_manager import _safe_asset_path
        assert _safe_asset_path(tmp_path, "sub/../room1") == (tmp_path / "room1.json").resolve()


class TestSaveDoesNotEscape:

    def test_malicious_room_name_not_written_outside(self, project_dir):
        pm = _make_pm()
        pm.load_project(project_dir)

        evil = "../../../../" + "pwned_room"
        pm.current_project_data['assets']['rooms'] = {
            evil: {'name': evil, 'instances': [{'object': 'o', 'x': 1, 'y': 1}]},
            'good_room': {'name': 'good_room', 'instances': []},
        }

        assert pm.save_project() is True
        # The good room saved normally; the malicious one wrote nothing outside.
        assert (project_dir / "rooms" / "good_room.json").exists()
        assert not (project_dir.parent / "pwned_room.json").exists()
        assert not (project_dir.parent.parent / "pwned_room.json").exists()

    def test_malicious_sprite_name_not_written_outside(self, project_dir):
        pm = _make_pm()
        pm.load_project(project_dir)
        (project_dir / "sprites").mkdir(exist_ok=True)

        evil = "../../../../pwned_sprite"
        pm.current_project_data['assets']['sprites'] = {
            evil: {'name': evil, 'frames': []},
        }

        assert pm.save_project() is True
        assert not (project_dir.parent / "pwned_sprite.json").exists()


class TestLoadDoesNotEscape:

    def test_malicious_room_name_skipped_on_load(self, project_dir, tmp_path):
        # Plant a file at the location a "../" room name would resolve to, then
        # confirm the loader never reads through the traversal into it.
        outside = tmp_path / "secret.json"
        outside.write_text(json.dumps({"instances": [{"leaked": True}]}), encoding="utf-8")

        # project_dir is tmp_path/"test_project"; "../secret" from rooms/ climbs
        # to tmp_path/secret.json.
        evil = "../../secret"
        pdata = json.loads((project_dir / "project.json").read_text(encoding="utf-8"))
        pdata['assets']['rooms'] = {evil: {'name': evil}}
        (project_dir / "project.json").write_text(json.dumps(pdata), encoding="utf-8")

        pm = _make_pm()
        assert pm.load_project(project_dir) is True
        # The traversal name was skipped — no leaked instance data merged in.
        room = pm.current_project_data['assets']['rooms'].get(evil, {})
        assert not room.get('instances')


@pytest.fixture
def project_dir(temp_project_dir):
    return temp_project_dir
