"""draw_sprite multi-frame support on the export targets (DOOM HUD Unit 4a).

The 'sprite' draw-queue command's subimage was honoured on desktop
(_draw_sprite) but ignored on HTML5 and Kivy, which drew the WHOLE spritesheet.
That blocks a health-reactive face icon (draw_doom_hud, Unit 4b) from
frame-swapping on two of three targets. This is a fix to the EXISTING 'sprite'
type, not a new draw-queue type. Desktop needs no change.
"""
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
KIVY_EXPORTER = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")


# --- Desktop (already correct — a guard, not a fix) ------------------------

def test_desktop_draw_sprite_already_honours_subimage():
    gr = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    body = gr[gr.index("def _draw_sprite"):]
    body = body[:body.index("\n    def ")]
    assert "subimage = cmd.get('subimage', 0)" in body
    assert "int(subimage) % len(sprite.frames)" in body


# --- HTML5 -----------------------------------------------------------------

def test_html5_sprite_crops_the_requested_frame():
    case = ENGINE[ENGINE.index("case 'sprite': {"):]
    case = case[:case.index("case 'lives'")]
    assert "makeSpriteInfo(cmd.sprite_name)" in case, "frame metadata not resolved"
    assert "info.frames" in case
    # 9-arg drawImage (source crop) when multi-frame; whole-image blit otherwise.
    assert "ctx.drawImage(img, srcX, 0, fw, fh, cmd.x || 0, cmd.y || 0, fw, fh)" in case
    assert "cmd.subimage" in case
    # single-frame path preserved
    assert "ctx.drawImage(img, cmd.x || 0, cmd.y || 0)" in case


def test_html5_srcX_selects_the_frame():
    """srcX = (subimage mod frames) * frame_width — a horizontal strip, the
    same math instance rendering uses."""
    case = ENGINE[ENGINE.index("case 'sprite': {"):]
    case = case[:case.index("case 'lives'")]
    assert "% frames) + frames) % frames * fw" in case


# --- Kivy ------------------------------------------------------------------

def test_kivy_sprite_case_crops_via_get_region():
    dq = KIVY_EXPORTER[KIVY_EXPORTER.index("elif ctype == 'sprite':"):]
    dq = dq[:dq.index("elif ctype == 'lives':")]
    assert "SPRITE_META.get(path" in dq, "frame metadata not resolved"
    assert "frames = max(1, int(meta.get('frames', 1) or 1))" in dq
    assert "tex.get_region(idx * fw, 0, fw, fh)" in dq
    assert "int(cmd.get('subimage', 0)) % frames" in dq
    # brace-doubling landmine: this is a .format() template.
    assert "SPRITE_META.get(path, {{}})" in dq


def _export(sample):
    from export.Kivy.kivy_exporter import KivyExporter
    from utils.project_file_merge import merge_object_file
    S = REPO_ROOT / "samples" / sample
    data = json.loads((S / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        side = S / "objects" / f"{name}.json"
        if side.exists():
            merge_object_file(obj, json.loads(side.read_text(encoding="utf-8")))
    for name in list(data["assets"]["rooms"]):
        side = S / "rooms" / f"{name}.json"
        if side.exists():
            data["assets"]["rooms"][name] = json.loads(side.read_text(encoding="utf-8"))
    out = Path(tempfile.mkdtemp(prefix="dqsprite_")) / "export"
    assert KivyExporter(data, S, out).export()
    return out / "game"


def test_kivy_generated_base_object_compiles_with_the_crop():
    """The {{}} must survive .format() as {} and the crop code must compile."""
    import py_compile
    game = _export("raycast_3")
    base = game / "objects" / "base_object.py"
    src = base.read_text(encoding="utf-8")
    assert "SPRITE_META.get(path, {})" in src, "brace-doubling wrong — {{}} did not become {}"
    assert "tex.get_region(idx * fw, 0, fw, fh)" in src
    py_compile.compile(str(base), doraise=True,
                       cfile=str(Path(tempfile.mkdtemp()) / "b.pyc"))
