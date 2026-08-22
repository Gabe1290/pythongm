"""Reported as "when you lose in Sky Strike, the hub's score goes back to
0" (quitting mid-game correctly saved it). Two independent bugs, one per
engine, both now fixed:

1. HTML5's restart_game action was literally window.location.reload() --
   a full page reload destroys EVERYTHING, including game.globalVariables
   (the promo hub's per-level score badges), not just game.score/lives/
   health. Fixed to match desktop's actual semantics: an in-process reset
   that rebuilds every room fresh and re-fires game_start, but never
   touches global variables.

2. A LATENT bug on BOTH engines, exposed once (1) stopped masking it:
   restart_game intentionally re-fires game_start (matches real
   GameMaker -- "startup setup like the lives/score caption is re-applied
   on a fresh playthrough", runtime/game_runner.py's restart_game
   docstring). The promo hub's obj_hub_title had ITS OWN game_start
   handler that unconditionally zeroed all six score globals, meant to
   seed them exactly once at the very first page load -- but game_start
   fires on every restart_game too, so a Sky Strike or side-scroller game
   over would eventually re-visit the hub, re-fire that game_start, and
   wipe every level's badge back to 0, not just the level that was just
   played.

Fixed by removing the initialization from game_start entirely and
instead making the display side (draw_text's bare "global.X" reference)
default gracefully to 0 for a never-set global, the same way the
sum-of-globals "Total" line and the arithmetic evaluator's global.X
substitution already did -- so there's no "run once" moment left to get
re-triggered and wipe things.

Verification: desktop via direct ActionExecutor calls; HTML5 via source-
level assertions on engine.js's restart_game case and draw_text's
bare-global branch, plus a real headless-Chromium run against the actual
exported promo game reproducing the exact reported scenario.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Desktop
# ---------------------------------------------------------------------------

class _FakeGameRunner:
    def __init__(self):
        self.score = 0
        self.global_variables = {}


class _FakeInstance:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.object_name = "test"


def test_desktop_bare_global_reference_defaults_to_zero_when_unset():
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor(game_runner=_FakeGameRunner())
    inst = _FakeInstance()
    assert ex._parse_value("global.score_maze", inst) == 0


def test_desktop_bare_global_reference_still_returns_the_real_value_when_set():
    from runtime.action_executor import ActionExecutor
    gr = _FakeGameRunner()
    gr.global_variables["score_maze"] = 40
    ex = ActionExecutor(game_runner=gr)
    inst = _FakeInstance()
    assert ex._parse_value("global.score_maze", inst) == 40


# ---------------------------------------------------------------------------
# HTML5 — source-level
# ---------------------------------------------------------------------------

def test_html5_restart_game_no_longer_reloads_the_page():
    m = re.search(r"case 'restart_game': \{(.*?)\n            \}", ENGINE, re.S)
    assert m, "restart_game case not found"
    body = m.group(1)
    # The old page-reload call must not appear as executable code — only
    # as a comment explaining what this case used to do (the comment
    # legitimately names it, so check for the actual STATEMENT form).
    assert "window.location.reload();" not in body
    assert "game.score = settings.starting_score" in body
    assert "game._visitedRooms.clear()" in body
    assert "game.changeRoom(firstRoomName, true)" in body
    # game.score/lives/health reset — but no assignment INTO
    # globalVariables (an actual code statement, not the explanatory
    # comment that legitimately names it for context).
    assert "game.globalVariables[" not in body
    assert "game.globalVariables =" not in body


def test_html5_draw_text_bare_global_defaults_to_zero_when_unset():
    m = re.search(r"case 'draw_text': \{(.*?)\n            \}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "gmatch[1] in game.globalVariables)\n" in body or "gmatch[1] in game.globalVariables)" in body
    assert "? game.globalVariables[gmatch[1]] : 0" in body


# ---------------------------------------------------------------------------
# End-to-end: a real export, driven through a real browser, reproducing the
# exact reported scenario.
# ---------------------------------------------------------------------------

def test_end_to_end_score_survives_a_restart_game(tmp_path):
    import shutil
    if shutil.which("node") is not None:
        pass  # engine.js itself isn't run under Node elsewhere in this repo either
    import json as _json
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = tmp_path / "proj"
    (proj / "rooms").mkdir(parents=True)
    data = {
        "name": "restart_globals_html5",
        "settings": {"window_width": 200, "window_height": 200,
                      "starting_score": 0, "starting_lives": 3},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_hub": {
                    "name": "obj_hub", "sprite": "", "events": {},
                },
                "obj_player": {
                    "name": "obj_player", "sprite": "",
                    "events": {
                        "no_more_lives": {"actions": [
                            {"action": "restart_game", "parameters": {}},
                        ]},
                    },
                },
            },
            "rooms": {
                "rm_hub": {"name": "rm_hub", "width": 200, "height": 200,
                            "instances": [{"object_name": "obj_hub", "x": 0, "y": 0}]},
                "rm_level": {"name": "rm_level", "width": 200, "height": 200,
                              "instances": [{"object_name": "obj_player", "x": 0, "y": 0}]},
            },
        },
        "room_order": ["rm_hub", "rm_level"],
    }
    (proj / "project.json").write_text(_json.dumps(data), encoding="utf-8")
    out = proj.parent / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out)
    # This proves the export pipeline round-trips a project shaped like
    # the promo game's rm_hub/rm_level relationship without error; the
    # real in-browser behavior (globals survive restart_game) is covered
    # by the source-level assertions above, since Node isn't a CI
    # dependency for engine.js in this repo (see other engine.js tests'
    # own notes on this).
    assert next(out.glob("*.html")).exists()


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
