"""HTML5 export — create_instance was entirely unimplemented in engine.js.

Only create_moving_instance existed there; create_instance (no initial
speed/direction -- the plain "spawn an object" action, used far more often
in authored projects than the moving variant) silently fell through
executeAction's `default` case, logging "Unknown action: create_instance"
and doing nothing. Desktop (runtime/action_executor.py
execute_create_instance_action) and Kivy (export/Kivy/code_generator.py)
both implement it; only HTML5 was missing it.

Verification tier, per this repo's "no Node in CI" convention (matching
test_html5_room_actions.py): source-level assertions on engine.js, a Python
port of the relative-offset math checked against the desktop runtime's own
semantics, and a real HTML5Exporter export round-trip.
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


def _case_body():
    m = re.search(r"case 'create_instance':\s*\{(.*?)\n            \}\n\n            case 'create_moving_instance'",
                   ENGINE, re.S)
    assert m, "case 'create_instance' not found immediately before create_moving_instance"
    return m.group(1)


def test_create_instance_case_exists_exactly_once():
    assert ENGINE.count("case 'create_instance':") == 1


def test_create_instance_spawns_via_spawn_instance():
    body = _case_body()
    assert "game.spawnInstance(params.object || '', px, py);" in body


def test_create_instance_supports_relative_positioning():
    body = _case_body()
    # Same truthy-string-safe pattern as the sibling destroy_at_position
    # action (params.relative can arrive as the JSON boolean OR the string
    # 'true' depending on how the project was authored/imported).
    assert "params.relative === true || params.relative === 'true'" in body
    assert "if (relative) { px += this.x; py += this.y; }" in body


def test_create_instance_no_longer_falls_through_to_default_warning():
    # Regression guard for the actual reported bug: before the fix,
    # create_instance had no case at all and hit the shared "Unknown
    # action" warning in executeAction's default branch.
    switch_start = ENGINE.index("executeAction(action, game) {")
    create_instance_pos = ENGINE.index("case 'create_instance':", switch_start)
    default_pos = ENGINE.index("console.warn(`Unknown action:", switch_start)
    assert create_instance_pos < default_pos


def _desktop_style_relative_offset(inst_x, inst_y, x, y, relative):
    """Python port of the case body's positioning math, mirroring
    execute_create_instance_action's `if relative: x = instance.x + x`."""
    px, py = x, y
    if relative:
        px += inst_x
        py += inst_y
    return px, py


def test_relative_offset_math_matches_desktop_runtime_semantics():
    # Desktop: instance at (100, 50), spawn offset (10, -5), relative=True
    # -> new instance lands at (110, 45), exactly like the runtime's
    # `x = instance.x + x; y = instance.y + y`.
    assert _desktop_style_relative_offset(100, 50, 10, -5, True) == (110, 45)
    # Non-relative: position is absolute, caller's position is irrelevant.
    assert _desktop_style_relative_offset(100, 50, 10, -5, False) == (10, -5)


def test_create_instance_project_exports_and_round_trips():
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="html5_create_instance_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    data = {
        "name": "create_instance_html5",
        "settings": {"window_width": 320, "window_height": 240},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_spawner": {
                    "name": "obj_spawner", "sprite": "",
                    "events": {
                        "create": {"actions": [
                            {"action": "create_instance",
                             "parameters": {"object": "obj_pickup", "x": 20,
                                            "y": 30, "relative": True}},
                        ]},
                    },
                },
                "obj_pickup": {"name": "obj_pickup", "sprite": "", "events": {}},
            },
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 320, "height": 240,
                          "instances": [{"object_name": "obj_spawner", "x": 5, "y": 5}]},
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
    assert actions[0]["action"] == "create_instance"
    assert actions[0]["parameters"]["object"] == "obj_pickup"
    assert actions[0]["parameters"]["relative"] is True

    # engine.js is inlined into the single exported .html, not a separate file
    assert "case 'create_instance':" in html
