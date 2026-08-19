"""HTML5 export — PWA manifest + service worker (docs/EXPORT_POLISH_PLAN.md
item 1 Phase 4). Opt-in (`pwa: True`), only meaningful alongside
`external_assets` (the single-file inline export is already fully offline
the instant it downloads -- nothing for a service worker to add). Default
export and external_assets-without-pwa must stay exactly as they were.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.HTML5.html5_exporter import HTML5Exporter  # noqa: E402


def _copy_sample(name="maze_1"):
    src = REPO_ROOT / "samples" / name
    tmp = Path(tempfile.mkdtemp(prefix="pwa_export_"))
    proj = tmp / "proj"
    shutil.copytree(src, proj)
    out = tmp / "out"
    out.mkdir()
    return proj, out


class TestPwaOffByDefault:
    def test_default_export_has_no_manifest_or_service_worker(self):
        proj, out = _copy_sample()
        assert HTML5Exporter().export(proj, out)
        assert not (out / "manifest.json").exists()
        assert not (out / "sw.js").exists()
        html = next(out.glob("*.html")).read_text(encoding="utf-8")
        assert "manifest.json" not in html
        assert "serviceWorker" not in html

    def test_pwa_without_external_assets_is_ignored(self):
        """pwa is only meaningful in folder mode -- requesting it alongside
        the default single-file mode must not produce a second file or a
        broken reference to files that don't exist."""
        proj, out = _copy_sample()
        assert HTML5Exporter().export(proj, out, {"pwa": True})
        produced = list(out.iterdir())
        assert len(produced) == 1
        assert not (out / "manifest.json").exists()

    def test_external_assets_without_pwa_still_has_no_manifest(self):
        proj, out = _copy_sample()
        assert HTML5Exporter().export(proj, out, {"external_assets": True})
        assert not (out / "manifest.json").exists()
        assert not (out / "sw.js").exists()


class TestPwaEnabled:
    def _export(self, sample="maze_1", extra_settings=None):
        proj, out = _copy_sample(sample)
        settings = {"external_assets": True, "pwa": True}
        settings.update(extra_settings or {})
        assert HTML5Exporter().export(proj, out, settings)
        return proj, out

    def test_manifest_is_valid_json_with_expected_fields(self):
        _proj, out = self._export()
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["name"] == "maze_1"
        assert manifest["display"] == "standalone"
        assert manifest["start_url"] == "./maze_1.html"
        assert len(manifest["icons"]) == 2
        sizes = {icon["sizes"] for icon in manifest["icons"]}
        assert sizes == {"192x192", "512x512"}
        for icon in manifest["icons"]:
            assert (out / icon["src"]).exists()

    def test_icons_are_the_right_pixel_dimensions(self):
        from PIL import Image
        _proj, out = self._export()
        img192 = Image.open(out / "assets" / "icons" / "icon-192.png")
        img512 = Image.open(out / "assets" / "icons" / "icon-512.png")
        assert img192.size == (192, 192)
        assert img512.size == (512, 512)

    def test_falls_back_to_generic_icon_when_no_icon_path_given(self):
        _proj, out = self._export()
        assert (out / "assets" / "icons" / "icon-512.png").exists()

    def test_uses_project_icon_path_when_provided(self, tmp_path):
        from PIL import Image
        custom_icon = tmp_path / "custom.png"
        Image.new("RGBA", (64, 64), (255, 0, 0, 255)).save(custom_icon)

        proj, out = self._export(extra_settings={"icon_path": str(custom_icon)})
        img = Image.open(out / "assets" / "icons" / "icon-192.png")
        # Corner pixel should be pure red (the custom icon), not whatever
        # the generic pygm2 icon happens to look like at that pixel.
        assert img.convert("RGBA").getpixel((0, 0)) == (255, 0, 0, 255)

    def test_html_references_manifest_and_registers_service_worker(self):
        _proj, out = self._export()
        html = next(out.glob("*.html")).read_text(encoding="utf-8")
        assert '<link rel="manifest" href="manifest.json">' in html
        assert "navigator.serviceWorker.register" in html

    def test_service_worker_caches_the_shell_and_copied_assets(self):
        _proj, out = self._export()
        sw = (out / "sw.js").read_text(encoding="utf-8")
        assert "./maze_1.html" in sw
        assert "./engine.js" in sw
        assert "./pako.min.js" in sw
        assert "./manifest.json" in sw
        # At least one real sprite file got listed for offline caching.
        assert "./assets/sprites/" in sw

    def test_service_worker_is_cache_first(self):
        _proj, out = self._export()
        sw = (out / "sw.js").read_text(encoding="utf-8")
        assert "caches.match(event.request)" in sw
        assert sw.index("caches.match") < sw.index("fetch(event.request)")

    def test_missing_icon_path_does_not_crash_export(self, tmp_path):
        """A stale/nonexistent icon_path setting must degrade gracefully
        (fall back to the generic icon), not fail the whole export."""
        proj, out = self._export(extra_settings={
            "icon_path": str(tmp_path / "does_not_exist.png")})
        assert (out / "assets" / "icons" / "icon-512.png").exists()
