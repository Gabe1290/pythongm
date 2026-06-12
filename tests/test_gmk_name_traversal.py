"""Regression tests for GMK-import path traversal (audit H10).

docs/FULL_AUDIT_2026-06-11.md: GmkConverter interpolated resource names
read verbatim from the untrusted .gmk binary into every output path
(objects/rooms/sprites/sounds/backgrounds) with no guard, so a crafted
name like '../../../x' escaped the chosen output directory and wrote
attacker-controlled bytes anywhere relative to it. Same class as the
traversals already fixed in utils/resource_packager.py and
core/project_manager.py.

The tests run the real GmkConverter methods on an instance created
without __init__ (constructing one requires a parsed .gmk binary).
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from importers.gmk_converter import GmkConverter


def _converter(tmp_path):
    conv = GmkConverter.__new__(GmkConverter)
    conv.output_dir = tmp_path / "project"
    for subdir in ("objects", "rooms", "sprites", "sounds", "backgrounds"):
        (conv.output_dir / subdir).mkdir(parents=True, exist_ok=True)
    return conv


class TestSafeOutputPath:

    def test_plain_name_resolves_under_subdir(self, tmp_path):
        conv = _converter(tmp_path)
        dest = conv._safe_output_path("sprites", "spr_player.png")
        assert dest == (conv.output_dir / "sprites" / "spr_player.png").resolve()

    def test_traversal_name_rejected(self, tmp_path):
        conv = _converter(tmp_path)
        with pytest.raises(ValueError):
            conv._safe_output_path("objects", "../../../evil.json")

    def test_absolute_name_rejected(self, tmp_path):
        conv = _converter(tmp_path)
        outside = tmp_path / "outside" / "evil.png"
        with pytest.raises(ValueError):
            conv._safe_output_path("sprites", str(outside))

    def test_inbounds_normalization_allowed(self, tmp_path):
        # Mirrors ResourcePackager._safe_join: only paths that climb above
        # the base are rejected, in-bounds '..' normalization is fine.
        conv = _converter(tmp_path)
        dest = conv._safe_output_path("sprites", "sub/../ok.png")
        assert dest == (conv.output_dir / "sprites" / "ok.png").resolve()


class TestWriteSitesGuarded:

    def test_object_write_with_traversal_name_writes_nothing(self, tmp_path):
        conv = _converter(tmp_path)
        planted = tmp_path / "evil.json"

        with pytest.raises(ValueError):
            conv._write_object_file("../../evil", {"name": "evil"})

        assert not planted.exists()
        # Nothing leaked outside the project dir either
        stray = [p for p in tmp_path.rglob("*.json")
                 if "project" not in p.parts]
        assert stray == []

    def test_object_write_with_safe_name_succeeds(self, tmp_path):
        conv = _converter(tmp_path)
        conv._write_object_file("obj_player", {"name": "obj_player"})

        out = conv.output_dir / "objects" / "obj_player.json"
        assert out.exists()
        assert json.loads(out.read_text(encoding="utf-8"))["name"] == "obj_player"
