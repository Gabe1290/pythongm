"""HTML5 export: execute_code and the page share the instance's state, both ways.

The page owns the instance -- it moves, tests and draws it -- but the author's Python ran against a stand-in
that only exchanged x, y, visible, the mouse, held keys and score/lives/health. So ``self.hspeed = 4``,
``self.vspeed = -8`` or ``self.hp = 9`` stayed inside Python (they persisted THERE between calls) and never
reached the engine, and Python never saw the page's hspeed or variables. Now the motion attributes and the
instance's plain variables (number / text / boolean) are synced in before the code runs and any change is diffed
back out; in a collision event ``other`` is the partner, synced the same way.

Three layers: the Python half executed for real (PY_BOOTSTRAP, deterministic, always runs); the JS glue by
structure; and, on the dev box (Playwright + Chromium, Pyodide from the CDN), a real export where the page's
instance really changes. The reference is the desktop's execute_execute_code_action.
"""
import json
import re
import sys
import tempfile
import types
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ENGINE = (ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8").replace("\r\n", "\n")


def _bootstrap_source():
    m = re.search(r"const PY_BOOTSTRAP = `(.*?)`;", ENGINE, re.S)
    assert m, "PY_BOOTSTRAP not found"
    return m.group(1)


@pytest.fixture()
def py():
    ns = {}
    exec(compile(_bootstrap_source(), "PY_BOOTSTRAP", "exec"), ns)
    return ns


def _sync(**kw):
    base = {"x": 10, "y": 20, "visible": True, "mouse_x": 0, "mouse_y": 0, "keys": [], "score": 0,
            "lives": 3, "health": 100, "vars": {}, "motion": {}}
    base.update(kw)
    return json.dumps(base)


def _run(py, code, inst="t", **kw):
    return json.loads(py["run_code"](inst, code, _sync(**kw)))


# ---------------------------------------------------------------- the Python half, executed

def test_motion_assigned_in_python_reaches_the_page(py):
    patch = _run(py, "self.hspeed = 4\nself.vspeed = -8", motion={"hspeed": 0, "vspeed": 0})
    assert patch["vars"] == {"hspeed": 4, "vspeed": -8}


def test_python_reads_what_the_page_holds(py):
    patch = _run(py, "self.hp = self.hp - 1\nself.vspeed = self.vspeed + self.hspeed",
                 vars={"hp": 5}, motion={"hspeed": 3, "vspeed": 1})
    assert patch["vars"] == {"hp": 4, "vspeed": 4}


def test_a_new_variable_and_a_bare_local_become_instance_variables(py):
    patch = _run(py, "self.counter = 1\nscore_bonus = 50")
    assert patch["vars"] == {"counter": 1, "score_bonus": 50}


def test_text_and_boolean_variables_sync_and_unchanged_ones_do_not_patch(py):
    patch = _run(py, "self.title = self.title + '!'\nself.alive = not self.alive\nself.same = self.same",
                 vars={"title": "hi", "alive": True, "same": 7})
    assert patch["vars"] == {"title": "hi!", "alive": False}


def test_nothing_changed_means_no_vars_key(py):
    assert "vars" not in _run(py, "pass", vars={"hp": 5}, motion={"hspeed": 1})


def test_only_plain_values_cross_over(py):
    patch = _run(py, "self.items = [1, 2]\nself.table = {'a': 1}\nself.inf = float('inf')\nself.ok = 2")
    assert patch["vars"] == {"ok": 2}
    # ...and the list a Python-only attribute holds still persists in Python between calls
    again = _run(py, "self.n = len(self.items)")
    assert again["vars"] == {"n": 2}


def test_private_names_and_the_reserved_ones_never_cross_over(py):
    patch = _run(py, "self._hidden = 1\nself.visible = False\nself.x = 99\nself.shown = 3")
    assert patch["vars"] == {"shown": 3}
    assert patch["x"] == 99 and patch["visible"] is False                      # the existing keys, as before


def test_the_page_is_authoritative_each_call(py):
    _run(py, "self.hp = 100", vars={"hp": 5})
    patch = _run(py, "self.hp = self.hp + 1", vars={"hp": 9})                   # the page changed it meanwhile
    assert patch["vars"] == {"hp": 10}


def test_other_is_the_partner_in_a_collision(py):
    other = {"id": 7, "x": 70, "y": 90, "vars": {"hp": 1}, "motion": {"vspeed": 2}}
    patch = _run(py, "other.hp -= 1\nother.vspeed = -other.vspeed\nother.x = other.x + 5\nself.hit = other.hp",
                 other=other)
    assert patch["other"] == {"x": 75, "vars": {"hp": 0, "vspeed": -2}}
    assert patch["vars"] == {"hit": 0}


def test_other_is_none_outside_a_collision(py):
    patch = _run(py, "self.none = other is None")
    assert patch["vars"] == {"none": True}


# ---------------------------------------------------------------- the desktop reference

def _desktop(code, state, other_state=None):
    from runtime.action_executor import ActionExecutor
    class _I:
        pass

    def make(spec):
        i = _I()
        i.object_name = "obj_probe"
        i.keys_pressed = set()
        i.__dict__.update(spec)
        return i
    runner = types.SimpleNamespace(global_variables={}, score=0, lives=3, health=100, project_data={"assets": {}},
                                   current_room=types.SimpleNamespace(width=640, height=480, instances=[]))
    ex = ActionExecutor(game_runner=runner)
    me = make(state)
    other = make(other_state) if other_state else None
    if other:
        ex._collision_other = other
    ex.execute_execute_code_action(me, {"code": code})
    return me, other


def test_the_same_code_leaves_the_same_state_as_on_desktop(py):
    code = "self.hp -= 1\nself.hspeed = self.hspeed * 2\nself.vspeed = -8\nself.counter = self.hp + 10\nbonus = 3"
    state = {"x": 10, "y": 20, "hp": 5, "hspeed": 3, "vspeed": 0}
    me, _ = _desktop(code, state)
    patch = _run(py, code, vars={"hp": 5}, motion={"hspeed": 3, "vspeed": 0})
    merged = {"hp": 5, "hspeed": 3, "vspeed": 0, **patch["vars"]}
    assert merged == {k: getattr(me, k) for k in merged}


def test_other_matches_the_desktop_in_a_collision(py):
    code = "other.hp -= 1\nother.vspeed = -3\nself.hp = other.hp"
    me, other = _desktop(code, {"x": 10, "y": 20, "hp": 5, "vspeed": 0}, {"x": 70, "y": 90, "hp": 4, "vspeed": 2})
    patch = _run(py, code, vars={"hp": 5}, motion={"vspeed": 0},
                 other={"id": 3, "x": 70, "y": 90, "vars": {"hp": 4}, "motion": {"vspeed": 2}})
    assert (patch["vars"]["hp"], patch["other"]["vars"]) == (me.hp, {"hp": other.hp, "vspeed": other.vspeed})


# ---------------------------------------------------------------- the JS glue, by structure

def test_the_page_packs_state_in_and_applies_the_patch_out():
    assert "vars: pyPackVars(inst), motion: pyPackMotion(inst)," in ENGINE
    assert "pyApplyVars(inst, patch.vars);" in ENGINE
    assert "state.other = {" in ENGINE and "pyApplyVars(partner, patch.other.vars);" in ENGINE
    assert "'hspeed', 'vspeed', 'speed', 'direction'" in ENGINE


def test_the_engine_attribute_deny_list_is_built_from_a_real_instance():
    assert "new GameObject('probe', 0, 0, {}, {})" in ENGINE
    assert "Object.getOwnPropertyNames(proto)" in ENGINE
    assert "pyIsAuthorVar(key) && pyIsPlain(value)" in ENGINE


# ---------------------------------------------------------------- real browser + real Pyodide (dev box)

@pytest.fixture(scope="module")
def page():
    sync_api = pytest.importorskip("playwright.sync_api")
    from export.HTML5.html5_exporter import HTML5Exporter
    src = Path(tempfile.mkdtemp(prefix="pysync_proj_")) / "maze_1"
    shutil.copytree(ROOT / "samples" / "maze_1", src)
    # one inert execute_code so the project NEEDS Python (the engine only loads Pyodide when it does)
    side = src / "objects" / "obj_wall.json"
    data = json.loads(side.read_text(encoding="utf-8"))
    data.setdefault("events", {})["create"] = {"actions": [{"action": "execute_code", "parameters": {"code": "pass"}}]}
    side.write_text(json.dumps(data), encoding="utf-8")
    out = Path(tempfile.mkdtemp(prefix="pysync_out_")) / "o"
    out.mkdir(parents=True)
    assert HTML5Exporter().export(src, out)
    with sync_api.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"no Chromium: {exc}")
        pg = browser.new_page()
        pg.goto(next(out.glob("*.html")).as_uri())
        try:
            pg.wait_for_function("window.game && window.game.python && window.game.python.ready", timeout=90000)
        except Exception as exc:
            pytest.skip(f"Pyodide did not load (no network?): {exc}")
        pg.evaluate("window.game.paused = true")
        yield pg
        browser.close()


_SETUP = """([spec, otherSpec]) => {
    const game = window.game, room = game.currentRoom;
    room.instances = [];
    const make = (name, s) => {
        const o = new GameObject(name, s.x, s.y, {}, {});
        Object.assign(o, s.vars || {});
        o.hspeed = s.hspeed || 0; o.vspeed = s.vspeed || 0;
        room.instances.push(o);
        return o;
    };
    window.__me = make('obj_probe', spec);
    window.__other = otherSpec ? make('obj_other', otherSpec) : null;
    window.__me._collision_other = window.__other;
    return true;
}"""

_RUN = """(code) => {
    const me = window.__me, game = window.game;
    me.executeAction({action: 'execute_code', parameters: {code: code}}, game);
    const grab = o => o ? {x: o.x, y: o.y, hp: o.hp, hspeed: o.hspeed, vspeed: o.vspeed, counter: o.counter,
                           title: o.title, bonus: o.bonus} : null;
    return {me: grab(me), other: grab(window.__other)};
}"""


@pytest.mark.parametrize("code,expect", [
    ("self.hspeed = 4\nself.vspeed = -8", {"hspeed": 4, "vspeed": -8}),
    ("self.hp = self.hp - 1", {"hp": 4}),
    ("self.counter = self.hp * 2\nbonus = 3", {"counter": 10, "bonus": 3}),
    ("self.title = 'hi'", {"title": "hi"}),
])
def test_the_page_instance_really_changes(code, expect, page):
    page.evaluate(_SETUP, [{"x": 10, "y": 20, "vars": {"hp": 5}}, None])
    got = page.evaluate(_RUN, code)["me"]
    assert {k: got[k] for k in expect} == expect


def test_the_engine_moves_what_python_set(page):
    """Python sets hspeed; the engine's own step then moves the instance by it."""
    page.evaluate(_SETUP, [{"x": 10, "y": 20}, None])
    page.evaluate(_RUN, "self.hspeed = 5")
    # (the engine scales a step by roomSpeed / 60, as it does for every instance)
    moved, factor = page.evaluate("""() => { const me = window.__me, game = window.game; const x0 = me.x; me.processMovement(game); return [me.x - x0, game.currentRoom.roomSpeed / 60]; }""")
    assert moved == pytest.approx(5 * factor)


def test_python_reads_the_pages_motion_and_variables(page):
    page.evaluate(_SETUP, [{"x": 10, "y": 20, "hspeed": 3, "vars": {"hp": 9}}, None])
    got = page.evaluate(_RUN, "self.vspeed = self.hspeed + self.hp")["me"]
    assert got["vspeed"] == 12


def test_a_collision_other_is_the_partner_in_a_real_page(page):
    page.evaluate(_SETUP, [{"x": 10, "y": 20, "vars": {"hp": 5}}, {"x": 70, "y": 90, "vars": {"hp": 1}, "vspeed": 2}])
    got = page.evaluate(_RUN, "other.hp -= 1\nother.vspeed = -3\nself.hp = other.hp + 100")
    assert (got["other"]["hp"], got["other"]["vspeed"], got["me"]["hp"]) == (0, -3, 100)


def test_python_cannot_overwrite_the_engines_own_attributes(page):
    page.evaluate(_SETUP, [{"x": 10, "y": 20}, None])
    got = page.evaluate("""(code) => {
        const me = window.__me, game = window.game;
        const before = [me.events, me.alarms, typeof me.processMovement, me.name];
        me.executeAction({action: 'execute_code', parameters: {code: code}}, game);
        return [me.events === before[0], me.alarms === before[1], typeof me.processMovement === before[2], me.name === before[3]];
    }""", "self.events = 1\nself.alarms = 2\nself.processMovement = 3\nself.name = 'hacked'")
    assert got == [True, True, True, True]
