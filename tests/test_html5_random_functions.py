"""HTML5 export — irandom()/random()/choose() were unsupported in every
numeric-parameter path, with two different failure shapes depending on
which one authored code happened to go through.

Found via the promo game's Sky Strike level: enemy planes (spawned via
create_instance with `x: "irandom(448) + 4"`) never appeared at all, and
ground targets (`x: "irandom(444) + 4"`) all clustered at the left screen
edge instead of spreading across it.

Two distinct bugs, both rooted in the same missing capability:

1. parseNumParam (used by create_instance's x/y, among many other
   actions) substitutes a few known tokens (self.x, other.x,
   facing_angle) then validates what's left against a digits-only
   whitelist regex with NO letters allowed at all -- any function call
   fails that check and silently returns the caller's fallback (0 for
   create_instance). Every ground target landed at x=0 -- not "near" the
   left edge, exactly on it, every time.

2. set_hspeed/set_vspeed used a bare `parseFloat(params.hspeed ?? ...)`
   with no fallback at all (unlike every OTHER parseFloat(...) site in
   this file, which all have a trailing `|| 0`). parseFloat on a
   non-numeric string like "irandom(2) - 1" returns NaN, not 0 -- and
   NaN hspeed poisons this.x on the very next movement step
   (this.x += this.hspeed) and never recovers. That's why the enemy
   planes were invisible, not just mispositioned: their x coordinate was
   NaN forever, and a canvas draw at a NaN position renders nothing.

Ported from runtime/action_executor.py's _evaluate_expression
(gm_random/gm_irandom/gm_choose): irandom(n) is a random INTEGER 0..n
inclusive, random(n) a random FLOAT 0..n exclusive, choose(a,b,...) one
of its arguments. Desktop's _eval_bool_expression (the if_condition/
test_expression boolean-condition path) does NOT support these either --
this fix intentionally matches that asymmetry, touching only the
numeric-parameter path (parseNumParam), not gmExpressionValue.

Verification tier, per this repo's "no Node in CI" convention: source-
level assertions on engine.js, plus a real HTML5Exporter export/round-
trip. The full behavioral proof — a real headless-Chromium run
(Playwright, not a CI dependency) against the actual exported promo
game, running 200 real room.step() calls — showed enemy plane x going
from NaN (every instance, forever) to real spread values (298, 438, 313,
86), and ground target x going from 0 (every instance, always) to
(280, 150, 233).
"""
import base64
import gzip
import json
import re
import tempfile
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _function_body(name):
    m = re.search(r"function " + re.escape(name) + r"\([^)]*\)\s*\{(.*?)\n\}",
                  ENGINE, re.S)
    assert m, f"{name} not found"
    return m.group(1)


def test_gm_irandom_matches_desktop_semantics():
    body = _function_body("gmIrandom")
    # 0..n INCLUSIVE, matching random.randint(0, int(n)) — not
    # Math.random() * n (exclusive) which would be gmRandom's job.
    assert "Math.floor(Math.random() * (n + 1))" in body


def test_gm_random_is_exclusive_float():
    body = _function_body("gmRandom")
    assert "Math.random() * n" in body


def test_gm_choose_picks_an_argument():
    body = _function_body("gmChoose")
    assert "args[Math.floor(Math.random() * args.length)]" in body


def test_parse_num_param_substitutes_random_calls_before_the_whitelist():
    m = re.search(r"function parseNumParam\([^)]*\)\s*\{(.*?)\n\}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert r"\birandom\b" in body
    assert r"\brandom\b" in body
    assert r"\bchoose\b" in body
    assert "gmIrandom" in body and "gmRandom" in body and "gmChoose" in body
    # The actual eval call must pass the three helpers in, not rely on
    # them being ambiently in scope of the `new Function` sandbox.
    assert "'gmIrandom', 'gmRandom', 'gmChoose'" in body
    assert "(gmIrandom, gmRandom, gmChoose)" in body


def test_set_hspeed_and_vspeed_no_longer_use_bare_parsefloat():
    for case in ("set_hspeed", "set_vspeed"):
        m = re.search(r"case '" + case + r"':(.*?)break;", ENGINE, re.S)
        assert m, case
        body = m.group(1)
        assert "parseNumParam(" in body, case
        assert "parseFloat(params." not in body, case


# ---------------------------------------------------------------------------
# End-to-end: a real export carries the irandom()-using actions through.
# ---------------------------------------------------------------------------

def test_random_spawn_project_exports_and_round_trips():
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="html5_random_fn_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    data = {
        "name": "random_fn_html5",
        "settings": {"window_width": 200, "window_height": 200},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_spawner": {
                    "name": "obj_spawner", "sprite": "",
                    "events": {
                        "create": {"actions": [
                            {"action": "create_instance", "parameters": {
                                "object": "obj_spawner", "x": "irandom(100) + 4",
                                "y": "0", "relative": False}},
                            {"action": "set_hspeed", "parameters": {
                                "hspeed": "irandom(2) - 1"}},
                        ]},
                    },
                },
            },
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 200, "height": 200,
                          "instances": [{"object_name": "obj_spawner", "x": 0, "y": 0}]},
            },
        },
        "room_order": ["rm_a"],
    }
    (proj / "project.json").write_text(json.dumps(data), encoding="utf-8")
    out = proj.parent / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out)

    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m
    embedded = json.loads(gzip.decompress(base64.b64decode(m.group(1))))

    actions = embedded["assets"]["objects"]["obj_spawner"]["events"]["create"]["actions"]
    assert actions[0]["parameters"]["x"] == "irandom(100) + 4"
    assert actions[1]["parameters"]["hspeed"] == "irandom(2) - 1"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
