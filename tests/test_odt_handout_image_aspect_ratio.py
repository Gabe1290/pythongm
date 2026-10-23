"""A very wide, short image (e.g. a cropped toolbar screenshot) embedded in
a handout .md via ![alt](path.png "NN%") rendered badly vertically
stretched in the generated .odt. Root cause: md_to_html emitted a bare HTML
`width="NN%"` attribute with no height -- fine for ordinary, roughly
page-shaped screenshots (LibreOffice's HTML import scales those
proportionally on its own), but not for an extreme aspect ratio. Found by
actually converting one to PDF via headless LibreOffice and looking at the
rendered page, not assumed.

Fix: compute both dimensions from the image's real pixel size and emit a
CSS `style="width:...cm;height:...cm"` instead (plain HTML width/height
attributes don't accept "cm" units at all -- tried first, produced a
near-invisible broken-image-icon-sized picture instead of a stretched one).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_image_size_cm_preserves_aspect_ratio(tmp_path):
    from PIL import Image
    import generate_tutorial_handouts_odt as g

    # A wide, short strip -- the toolbar-crop shape that triggered the bug.
    wide = tmp_path / "wide.png"
    Image.new("RGBA", (400, 47), (0, 0, 0, 0)).save(wide)
    width_cm, height_cm = g._image_size_cm(str(wide), 55)
    assert abs(width_cm - g.PAGE_CONTENT_WIDTH_CM * 55 / 100) < 1e-9
    assert abs(height_cm / width_cm - 47 / 400) < 1e-6

    # An ordinary, roughly page-shaped screenshot -- must also stay
    # proportional, not just the extreme case.
    normal = tmp_path / "normal.png"
    Image.new("RGBA", (1161, 865), (0, 0, 0, 0)).save(normal)
    width_cm2, height_cm2 = g._image_size_cm(str(normal), 65)
    assert abs(height_cm2 / width_cm2 - 865 / 1161) < 1e-6


def test_md_to_html_image_uses_css_style_not_bare_percent_attributes(tmp_path):
    from PIL import Image
    import generate_tutorial_handouts_odt as g

    img = tmp_path / "shot.png"
    Image.new("RGBA", (400, 47), (0, 0, 0, 0)).save(img)
    md = '![A screenshot](shot.png "55%")\n'
    html = g.md_to_html(md, src_dir=str(tmp_path))

    assert '<img src="data:image/png;base64,' in html
    # The old, buggy form: a bare width attribute with no height at all.
    assert 'width="55%"' not in html
    # The fix: both dimensions pinned via CSS, in a unit <img> width/height
    # HTML attributes don't actually support.
    assert 'style="width:' in html
    assert "cm;height:" in html
    assert "cm\"" in html  # the style attribute closes cleanly
