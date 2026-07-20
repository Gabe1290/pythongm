"""Draw depth order + draw-event visibility parity across the export targets.

Two long-standing divergences from the desktop runtime, both found while doing
the raycast HUD work (RAYCAST_HUD_PLAN) and fixed 2026-07-20:

1. DEPTH ORDER. GameMaker draws HIGHER depth FIRST (further back), so a LOWER
   depth ends up in front — a descending sort, which is what
   GameRoom._render_room does (`sorted(..., reverse=True)`). engine.js sorted
   ASCENDING, inverting sprite z-order; the Kivy exporter ignored `depth`
   entirely and drew in instance-creation order.

   Four bundled samples use more than one depth and were therefore visibly
   wrong on those targets: maze_3, maze_4, plateforme_3, treasure. The worst
   case is plateforme_3, whose player (depth -100) drew BEHIND the level exit
   (depth 100) instead of in front.

2. DRAW-EVENT VISIBILITY. GameMaker does not run an invisible instance's draw
   event at all; the desktop runtime gets this from render()'s early return on
   `not self.visible`. Both export targets ran the draw event regardless,
   skipping only the sprite — so a controller hidden with visible=false kept
   drawing on the exports while correctly drawing nothing on desktop.
"""
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
KIVY_SRC = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")

# Samples with more than one distinct object depth — the only ones whose
# rendering can differ under an inverted sort. Kept explicit so that adding a
# depth to another sample doesn't silently widen the blast radius unnoticed.
MULTI_DEPTH_SAMPLES = {
    "maze_3": {-10, 0, 10},
    "maze_4": {-10, -5, 0, 10},
    "plateforme_3": {-100, 0, 10, 50, 100},
    "treasure": {-2, -1, 0},
}


def _object_depths(sample):
    out = {}
    for path in sorted((REPO_ROOT / "samples" / sample / "objects").glob("*.json")):
        out[path.stem] = json.loads(path.read_text(encoding="utf-8")).get("depth", 0)
    return out


@pytest.mark.parametrize("sample,depths", sorted(MULTI_DEPTH_SAMPLES.items()))
def test_affected_samples_still_use_multiple_depths(sample, depths):
    """Pins the blast radius this fix was verified against."""
    assert set(_object_depths(sample).values()) == depths


def test_plateforme_3_player_must_draw_in_front_of_the_exit():
    """The concrete case that was inverted on both export targets."""
    depths = _object_depths("plateforme_3")
    assert depths["obj_pingus"] == -100
    assert depths["obj_sortie"] == 100
    assert depths["obj_pingus"] < depths["obj_sortie"], \
        "lower depth must be in front — the player draws over the exit"


# --- HTML5 -----------------------------------------------------------------

def test_html5_sorts_depth_descending_everywhere():
    assert ENGINE.count("sort((a, b) => b.depth - a.depth)") >= 2, \
        "both the normal draw pass and the raycast HUD pass must sort descending"
    assert "a.depth - b.depth" not in ENGINE, \
        "ascending depth sort is back — it inverts sprite z-order"


def test_html5_skips_the_draw_event_when_invisible():
    run_draw = ENGINE[ENGINE.index("runDrawEvent(ctx) {"):]
    run_draw = run_draw[:run_draw.index("\n    }")]
    assert "if (!this.visible) return;" in run_draw
    assert run_draw.index("if (!this.visible) return;") < run_draw.index("executeActions")


# --- Kivy ------------------------------------------------------------------

def test_kivy_draw_loop_sorts_descending_and_honours_visible():
    loop = KIVY_SRC[KIVY_SRC.index("# 8. DRAW EVENTS"):]
    loop = loop[:loop.index("# 9. CLEANUP")]
    assert "reverse=True" in loop, "draw events must run highest-depth-first"
    assert "getattr(i, 'depth', 0)" in loop
    assert "visible" in loop, "invisible instances must not run their draw event"


def test_kivy_orders_widgets_by_depth_on_insert():
    block = KIVY_SRC[KIVY_SRC.index("    def add_instance"):]
    block = block[:block.index("    def remove_instance")]
    # Child-widget path: children sorted ascending (children[0] draws on top).
    assert "add_widget(instance, index=idx)" in block
    assert "getattr(child, 'depth', 0) >= depth" in block
    # Fbo path (views-enabled rooms): add order is back-to-front.
    assert "_fbo.insert(idx" in block


@pytest.fixture(scope="module")
def exported_plateforme_3():
    """Export the worst-affected sample for real — catches template/format
    breakage that a source-level assertion can't."""
    from export.Kivy.kivy_exporter import KivyExporter
    from utils.project_file_merge import merge_object_file

    sample = REPO_ROOT / "samples" / "plateforme_3"
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        side = sample / "objects" / f"{name}.json"
        if side.exists():
            merge_object_file(obj, json.loads(side.read_text(encoding="utf-8")))
    for name in list(data["assets"]["rooms"]):
        side = sample / "rooms" / f"{name}.json"
        if side.exists():
            data["assets"]["rooms"][name] = json.loads(side.read_text(encoding="utf-8"))
    out = Path(tempfile.mkdtemp(prefix="kivy_depth_")) / "export"
    assert KivyExporter(data, sample, out).export()
    return out / "game"


def test_kivy_generated_objects_carry_their_depth(exported_plateforme_3):
    """depth must survive codegen — it was dropped entirely before this fix."""
    expected = _object_depths("plateforme_3")
    seen = {}
    for path in (exported_plateforme_3 / "objects").glob("*.py"):
        src = path.read_text(encoding="utf-8")
        for line in src.splitlines():
            if line.strip().startswith("self.depth = "):
                seen[path.stem] = int(line.split("=")[1].strip())
    assert seen, "no generated object declared a depth"
    # The two that matter, by module name (obj_pingus -> pingus module naming
    # varies, so match on the values actually emitted).
    assert -100 in seen.values(), "obj_pingus's depth -100 was not emitted"
    assert 100 in seen.values(), "obj_sortie's depth 100 was not emitted"
    assert set(seen.values()) <= set(expected.values())
