"""GM Set-Font alignment: import as canonical `halign`, tolerate legacy `align`.

GM's action_font carries a horizontal-align menu (0=left, 1=center, 2=right)
under the key `align`. Neither the runtime (reads `halign`/`valign`) nor the
events-panel metadata spoke that key, so any GM center/right font alignment was
silently ignored on import (it landed on `align`, which nothing read).

- The importer now converts `align` → `halign` (gmk_converter._convert_font_align).
- The runtime tolerates a raw `align` as a `halign` fallback for projects
  imported before the converter fix (execute_set_draw_font_action).
- maze_4's shipped data was normalised from `align: "0"` to `halign: "left"`.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# --- importer conversion --------------------------------------------------

def test_convert_font_align_maps_gm_menu():
    from importers.gmk_converter import _convert_font_align
    assert _convert_font_align("0") == "left"
    assert _convert_font_align("1") == "center"
    assert _convert_font_align("2") == "right"
    assert _convert_font_align(1) == "center"        # raw int form
    assert _convert_font_align("center") == "center"  # already named -> passthrough
    assert _convert_font_align("bogus") == "left"     # unknown -> runtime default


def test_converter_emits_halign_not_align_end_to_end():
    """A real GM Set-Font action converts to set_draw_font with `halign`, no
    `align` — exercised through the actual _convert_single_action path."""
    from importers.gmk_converter import GmkConverter
    from importers.gmk_parser import GmkAction
    conv = GmkConverter.__new__(GmkConverter)  # no full project needed
    act = GmkAction(
        library_id=1, action_id=525, function_name="action_font",
        argument_count=2, argument_types=[1, 0],
        argument_values=["score_font", "1"],   # font, GM align=center
    )
    result = conv._convert_single_action(act)
    assert result["action"] == "set_draw_font"
    assert result["parameters"].get("halign") == "center"
    assert "align" not in result["parameters"]


# --- runtime fallback -----------------------------------------------------

def _executor_and_instance():
    from runtime.action_executor import ActionExecutor
    from types import SimpleNamespace
    ex = ActionExecutor(game_runner=None)
    inst = SimpleNamespace(object_name="obj_t", x=0, y=0,
                           draw_font=None, draw_halign="left", draw_valign="top")
    return ex, inst


def test_runtime_reads_legacy_align_when_no_halign():
    ex, inst = _executor_and_instance()
    ex.execute_set_draw_font_action(inst, {"font": "", "align": "1"})
    assert inst.draw_halign == "center"


def test_runtime_prefers_explicit_halign_over_align():
    ex, inst = _executor_and_instance()
    ex.execute_set_draw_font_action(inst, {"halign": "right", "align": "0"})
    assert inst.draw_halign == "right"


def test_runtime_canonical_halign_still_works():
    ex, inst = _executor_and_instance()
    ex.execute_set_draw_font_action(inst, {"font": "", "halign": "center"})
    assert inst.draw_halign == "center"


# --- sample data hygiene --------------------------------------------------

def test_maze_4_sample_uses_canonical_halign():
    for path in ("samples/maze_4/objects/controller_main.json",
                 "samples/maze_4/project.json"):
        blob = (REPO_ROOT / path).read_text(encoding="utf-8")
        data = json.loads(blob)
        assert '"align"' not in blob, f"{path} still carries legacy GM align key"
        assert "halign" in blob        # normalised form present
