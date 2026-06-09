"""
Regression tests for archive path-traversal (Zip Slip) hardening.

Two surfaces:
  1. ProjectCompressor.decompress_project — rejects zip members that resolve
     outside the target dir (defense-in-depth; modern CPython extractall
     already strips ".." but we fail loudly instead of silently flattening).
  2. ResourcePackager import_* — destinations are built from untrusted
     package.json asset names and written via zipf.open (which, unlike
     extractall, does NOT sanitize), so a name like "../../x" could escape the
     project. _safe_join now blocks that.
"""

import json
import zipfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.project_compression import ProjectCompressor
from utils.resource_packager import ResourcePackager


class TestDecompressZipSlip:

    def test_malicious_member_is_rejected(self, tmp_path):
        zip_path = tmp_path / "evil.zip"
        with zipfile.ZipFile(zip_path, "w") as z:
            z.writestr("../../escaped.txt", "pwned")
            z.writestr("project.json", "{}")

        out = tmp_path / "out"
        result = ProjectCompressor.decompress_project(zip_path, out)

        assert result is False  # traversal caught -> reported as failure
        # Nothing extracted outside the target dir.
        assert not (tmp_path / "escaped.txt").exists()
        assert not (tmp_path.parent / "escaped.txt").exists()

    def test_legitimate_archive_extracts(self, tmp_path):
        zip_path = tmp_path / "good.zip"
        with zipfile.ZipFile(zip_path, "w") as z:
            z.writestr("project.json", '{"name": "ok"}')
            z.writestr("rooms/room1.json", "{}")

        out = tmp_path / "out"
        result = ProjectCompressor.decompress_project(zip_path, out)

        assert result is True
        assert (out / "project.json").exists()
        assert (out / "rooms" / "room1.json").exists()

    def test_roundtrip_compress_then_decompress(self, tmp_path):
        proj = tmp_path / "proj"
        (proj / "rooms").mkdir(parents=True)
        (proj / "project.json").write_text('{"name": "rt"}', encoding="utf-8")
        (proj / "rooms" / "r.json").write_text("{}", encoding="utf-8")

        zip_path = tmp_path / "rt.zip"
        assert ProjectCompressor.compress_project(proj, zip_path) is True

        out = tmp_path / "out"
        assert ProjectCompressor.decompress_project(zip_path, out) is True
        assert (out / "project.json").read_text(encoding="utf-8") == '{"name": "rt"}'


class TestSafeJoin:

    def test_normal_name_ok(self, tmp_path):
        dest = ResourcePackager._safe_join(tmp_path, "sprites", "player.png")
        assert dest == (tmp_path / "sprites" / "player.png").resolve()

    @pytest.mark.parametrize("evil", [
        "../../../etc/passwd",   # deep climb above base
        "../../outside",         # exactly clears the 'sprites' segment + base
        "/tmp/abs_escape",       # absolute path resets the join
    ])
    def test_traversal_rejected(self, tmp_path, evil):
        with pytest.raises(ValueError):
            ResourcePackager._safe_join(tmp_path, "sprites", f"{evil}.png")

    def test_in_bounds_normalization_is_allowed(self, tmp_path):
        # "sprites/../player.png" normalizes to base/player.png — still inside
        # base, so it is NOT a traversal and must be accepted.
        dest = ResourcePackager._safe_join(tmp_path, "sprites", "../player.png")
        assert dest == (tmp_path / "player.png").resolve()


class TestImportObjectTraversal:

    def _make_project(self, tmp_path):
        proj = tmp_path / "project"
        (proj / "sprites").mkdir(parents=True)
        (proj / "project.json").write_text(
            json.dumps({"name": "target", "assets": {"objects": {}, "sprites": {}}}),
            encoding="utf-8",
        )
        return proj

    def test_malicious_sprite_name_cannot_escape(self, tmp_path):
        proj = self._make_project(tmp_path)
        evil_name = "../../../../pwned_sprite"

        pkg = tmp_path / "evil.gmobj"
        with zipfile.ZipFile(pkg, "w") as z:
            z.writestr("package.json", json.dumps({
                "type": "object",
                "object": {"name": "obj1"},
                "dependencies": {"sprites": {evil_name: {"name": evil_name}}},
            }))
            # The crafted member matching the constructed path.
            z.writestr(f"sprites/{evil_name}.png", b"\x89PNG fake")

        result = ResourcePackager.import_object(pkg, proj)

        assert result is None  # traversal blocked -> import fails
        # No file written outside the project tree.
        assert not (tmp_path / "pwned_sprite.png").exists()
        assert not (tmp_path.parent / "pwned_sprite.png").exists()

    def test_benign_import_still_works(self, tmp_path):
        proj = self._make_project(tmp_path)

        pkg = tmp_path / "ok.gmobj"
        with zipfile.ZipFile(pkg, "w") as z:
            z.writestr("package.json", json.dumps({
                "type": "object",
                "object": {"name": "obj1", "sprite": "spr1"},
                "dependencies": {"sprites": {"spr1": {"name": "spr1"}}},
            }))
            z.writestr("sprites/spr1.png", b"\x89PNG fake")

        result = ResourcePackager.import_object(pkg, proj)

        assert result == "obj1"
        assert (proj / "sprites" / "spr1.png").exists()
