"""HTML5 export — external_assets option (docs/EXPORT_POLISH_PLAN.md item
1): opt-in folder export with real sprite/sound files instead of base64
data URIs, default off. The default (inline, single-file) export must
stay byte-for-byte the same shape it always was -- these tests pin both
sides: default unchanged, opt-in produces the new folder layout.
"""
import base64
import gzip
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.HTML5.html5_exporter import HTML5Exporter, _copy_asset_file  # noqa: E402


def _copy_sample(name="maze_1"):
    src = REPO_ROOT / "samples" / name
    tmp = Path(tempfile.mkdtemp(prefix="ext_assets_"))
    proj = tmp / "proj"
    shutil.copytree(src, proj)
    out = tmp / "out"
    out.mkdir()
    return proj, out


def _embedded_arrays(html):
    """The three decompressData(...) calls in document order:
    (gameData, spritesData, soundsData). Same technique
    test_export_message_localization.py already established -- gameData
    is gzip+base64 compressed, so asserting on the raw HTML text alone
    proves nothing."""
    matches = re.findall(r'decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert len(matches) == 3, "expected gameData, spritesData, soundsData"
    return [json.loads(gzip.decompress(base64.b64decode(m)).decode("utf-8"))
            for m in matches]


class TestDefaultExportUnchanged:
    def test_still_exactly_one_file_with_no_assets_folder(self):
        proj, out = _copy_sample()
        assert HTML5Exporter().export(proj, out)
        produced = list(out.iterdir())
        assert len(produced) == 1, f"expected exactly one file, got {produced}"
        assert produced[0].suffix == ".html"

    def test_sprites_are_still_inline_data_uris(self):
        proj, out = _copy_sample()
        assert HTML5Exporter().export(proj, out)
        html = next(out.glob("*.html")).read_text(encoding="utf-8")
        _game_data, sprites_data, _sounds_data = _embedded_arrays(html)
        assert sprites_data, "sample has no sprites to check"
        for value in sprites_data.values():
            assert value.startswith("data:"), value


class TestExternalAssetsMode:
    def _export(self, sample="maze_1"):
        proj, out = _copy_sample(sample)
        assert HTML5Exporter().export(proj, out, {"external_assets": True})
        return proj, out

    def test_produces_a_folder_not_one_file(self):
        _proj, out = self._export()
        names = {p.name for p in out.iterdir()}
        assert "engine.js" in names
        assert "pako.min.js" in names
        assert (out / "assets" / "sprites").is_dir()
        assert any((out / "assets" / "sprites").iterdir()), \
            "sprite files should have been copied"

    def test_html_references_scripts_by_src_not_inline(self):
        _proj, out = self._export()
        html = next(out.glob("*.html")).read_text(encoding="utf-8")
        assert '<script src="engine.js"></script>' in html
        assert '<script src="pako.min.js"></script>' in html
        # The full engine source must NOT also be duplicated inline --
        # spot-check with a distinctive, unlikely-to-appear-elsewhere
        # substring from engine.js itself.
        engine_js = (out / "engine.js").read_text(encoding="utf-8")
        marker = engine_js.strip().splitlines()[0]
        assert html.count(marker) == 0

    def test_sprite_values_are_relative_paths_not_data_uris(self):
        _proj, out = self._export()
        html = next(out.glob("*.html")).read_text(encoding="utf-8")
        _game_data, sprites_data, _sounds_data = _embedded_arrays(html)
        assert sprites_data, "sample has no sprites to check"
        for name, value in sprites_data.items():
            assert not value.startswith("data:"), f"{name} still inline"
            assert value.startswith("assets/sprites/"), value
            assert (out / value).exists(), f"{value} was not actually written"

    def test_copied_sprite_bytes_match_the_source_file(self):
        proj, out = self._export()
        html = next(out.glob("*.html")).read_text(encoding="utf-8")
        _game_data, sprites_data, _sounds_data = _embedded_arrays(html)
        project_data = json.loads((proj / "project.json").read_text(encoding="utf-8"))
        for sprite_name, rel_url in sprites_data.items():
            sprite_info = project_data["assets"]["sprites"][sprite_name]
            source_bytes = (proj / sprite_info["file_path"]).read_bytes()
            assert (out / rel_url).read_bytes() == source_bytes

    def test_writes_a_hosting_readme(self):
        _proj, out = self._export()
        readme = out / "README-hosting.txt"
        assert readme.exists()
        text = readme.read_text(encoding="utf-8")
        assert "file://" in text
        assert "http.server" in text

    def test_still_produces_valid_html(self):
        _proj, out = self._export()
        html_files = list(out.glob("*.html"))
        assert len(html_files) == 1


class TestCopyAssetFile:
    def test_preserves_extension_and_sanitizes_name(self, tmp_path):
        src = tmp_path / "src.PNG"
        src.write_bytes(b"\x89PNG fake")
        dest_dir = tmp_path / "dest"
        url = _copy_asset_file(src, dest_dir, "spr:weird/name", "assets/sprites")
        assert url == "assets/sprites/spr_weird_name.png"
        assert (dest_dir / "spr_weird_name.png").read_bytes() == b"\x89PNG fake"

    def test_two_names_colliding_after_sanitization_do_not_overwrite_each_other(self, tmp_path):
        src_a = tmp_path / "a.png"
        src_a.write_bytes(b"AAAA")
        src_b = tmp_path / "b.png"
        src_b.write_bytes(b"BBBB")
        dest_dir = tmp_path / "dest"

        # Both sanitize to "spr_x" -- must not silently clobber one another.
        url_a = _copy_asset_file(src_a, dest_dir, "spr:x", "assets/sprites")
        url_b = _copy_asset_file(src_b, dest_dir, "spr<x", "assets/sprites")

        assert url_a != url_b
        assert (dest_dir / Path(url_a).name).read_bytes() == b"AAAA"
        assert (dest_dir / Path(url_b).name).read_bytes() == b"BBBB"
