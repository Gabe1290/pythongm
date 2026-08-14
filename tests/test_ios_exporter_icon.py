"""iOS export app icon wiring (TODO.md: "iOS exporter has no app icon").

export/ios/ios_exporter.py never touched an app icon at all — exported
games shipped with Xcode's blank default. This covers the fix: an
`icon_path` export setting (same pattern as exe/macos_exporter.py's), and
a fallback to PyGameMaker's own bundled `resources/ios/AppIcon.appiconset`
so exported games aren't icon-less even without a user-supplied image.

No macOS/Xcode/kivy-ios dependency here — `_populate_appiconset` and
`_find_appiconset_dir` are pure filesystem + Pillow logic, testable on any
platform, same tier as this repo's "no Node.js in CI" HTML5 structural
tests.
"""
import sys
from pathlib import Path

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.ios.ios_exporter import iOSExporter  # noqa: E402

DEFAULT_APPICONSET = REPO_ROOT / "resources" / "ios" / "AppIcon.appiconset"


def _make_source_image(path: Path, size=(200, 100), mode='RGBA'):
    img = Image.new(mode, size, (10, 20, 30, 128) if mode == 'RGBA' else (10, 20, 30))
    img.save(path)
    return path


def test_default_appiconset_dir_points_at_bundled_resources():
    exporter = iOSExporter()
    assert exporter._default_appiconset_dir() == DEFAULT_APPICONSET
    assert DEFAULT_APPICONSET.is_dir()


def test_populate_appiconset_without_icon_path_copies_bundled_default(tmp_path):
    exporter = iOSExporter()
    exporter.export_settings = {}
    dest = tmp_path / "AppIcon.appiconset"

    assert exporter._populate_appiconset(dest) is True

    for item in DEFAULT_APPICONSET.iterdir():
        copy = dest / item.name
        assert copy.exists()
        assert copy.read_bytes() == item.read_bytes()


def test_populate_appiconset_with_icon_path_resizes_every_slot(tmp_path):
    source = _make_source_image(tmp_path / "my_icon.png")
    exporter = iOSExporter()
    exporter.export_settings = {'icon_path': str(source)}
    dest = tmp_path / "AppIcon.appiconset"

    assert exporter._populate_appiconset(dest) is True

    # Contents.json is copied verbatim from the bundled manifest.
    assert (dest / "Contents.json").read_bytes() == \
        (DEFAULT_APPICONSET / "Contents.json").read_bytes()

    for filename, size_pt, scale in iOSExporter._APPICON_SPECS:
        px = round(size_pt * scale)
        out_path = dest / filename
        assert out_path.exists(), filename
        with Image.open(out_path) as im:
            assert im.size == (px, px), filename
            # App Store icons must not carry an alpha channel.
            assert im.mode == 'RGB', filename


def test_populate_appiconset_flattens_transparency_onto_white(tmp_path):
    # A fully transparent source pixel must land on opaque white, not black.
    source = tmp_path / "transparent.png"
    Image.new('RGBA', (64, 64), (0, 0, 0, 0)).save(source)
    exporter = iOSExporter()
    exporter.export_settings = {'icon_path': str(source)}
    dest = tmp_path / "AppIcon.appiconset"

    exporter._populate_appiconset(dest)

    with Image.open(dest / "Icon-1024.png") as im:
        assert im.getpixel((0, 0)) == (255, 255, 255)


def test_populate_appiconset_falls_back_when_icon_path_missing(tmp_path):
    exporter = iOSExporter()
    exporter.export_settings = {'icon_path': str(tmp_path / "does_not_exist.png")}
    dest = tmp_path / "AppIcon.appiconset"

    # Must not raise — falls back to the bundled default instead.
    assert exporter._populate_appiconset(dest) is True
    assert (dest / "Icon-1024.png").read_bytes() == \
        (DEFAULT_APPICONSET / "Icon-1024.png").read_bytes()


def test_populate_appiconset_falls_back_on_unreadable_image(tmp_path):
    bogus = tmp_path / "not_an_image.png"
    bogus.write_bytes(b"this is not a png")
    exporter = iOSExporter()
    exporter.export_settings = {'icon_path': str(bogus)}
    dest = tmp_path / "AppIcon.appiconset"

    assert exporter._populate_appiconset(dest) is True
    assert (dest / "Icon-1024.png").read_bytes() == \
        (DEFAULT_APPICONSET / "Icon-1024.png").read_bytes()


def test_find_appiconset_dir_locates_existing_nested_folder(tmp_path):
    # Mirrors a kivy-ios-generated project shipping its own placeholder
    # AppIcon.appiconset somewhere under the per-app subdirectory.
    proj_dir = tmp_path / "MyGame-ios"
    nested = proj_dir / "MyGame" / "Images.xcassets" / "AppIcon.appiconset"
    nested.mkdir(parents=True)
    (nested / "Contents.json").write_text("{}")

    exporter = iOSExporter()
    found = exporter._find_appiconset_dir(proj_dir)
    assert found == nested


def test_find_appiconset_dir_returns_none_when_absent(tmp_path):
    proj_dir = tmp_path / "MyGame-ios"
    proj_dir.mkdir()
    exporter = iOSExporter()
    assert exporter._find_appiconset_dir(proj_dir) is None


def test_install_app_icon_uses_existing_template_location(tmp_path):
    proj_dir = tmp_path / "MyGame-ios"
    nested = proj_dir / "MyGame" / "Images.xcassets" / "AppIcon.appiconset"
    nested.mkdir(parents=True)

    exporter = iOSExporter()
    exporter.export_settings = {}
    exporter._xcode_proj_dir = proj_dir
    exporter._app_name = "MyGame"

    exporter._install_app_icon(tmp_path)

    assert (nested / "Icon-1024.png").exists()
    assert (nested / "Contents.json").exists()


def test_install_app_icon_creates_conventional_location_when_template_lacks_one(tmp_path):
    proj_dir = tmp_path / "MyGame-ios"
    proj_dir.mkdir()

    exporter = iOSExporter()
    exporter.export_settings = {}
    exporter._xcode_proj_dir = proj_dir
    exporter._app_name = "MyGame"

    exporter._install_app_icon(tmp_path)

    fallback = proj_dir / "MyGame" / "Images.xcassets" / "AppIcon.appiconset"
    assert (fallback / "Icon-1024.png").exists()


def test_install_app_icon_never_raises_even_on_unexpected_state(tmp_path):
    # No _xcode_proj_dir/_app_name set at all (defensive: a future ordering
    # bug must not turn an icon failure into a whole-export failure).
    exporter = iOSExporter()
    exporter.export_settings = {}
    exporter._install_app_icon(tmp_path)  # must not raise
