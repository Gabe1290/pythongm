"""HTML5 export: set_variable / test_variable resolve who they apply to like the desktop.

The same cases as the Kivy test (tests/test_kivy_variable_scope.py), run in the real HTML5 engine in Chromium
(dev box; skipped without Playwright), with the desktop handlers as the reference. The HTML5 engine keeps the
author's y (down from the top) and vspeed (positive down), so only the *who* can differ: it handled scope
(self / other / global) but not GameMaker's "Applies to" (``target``: self / other / object + ``target_object``,
emitted by the GMK importer), nor a ``global.`` / ``other.`` / ``self.`` prefix in the variable NAME (the action's
own description offers it), and a test with no collision partner compared against 0 instead of being false.
"""
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_kivy_variable_scope import (  # noqa: E402
    GLOBALS, ORDER, SET_CASES, SPECS, TEST_CASES, _id, desktop_set, desktop_test)

PAGE_SETUP = """([specs, globals]) => {
    const game = window.game, room = game.currentRoom;
    game.paused = true;                  // the live loop must not move the probes between calls
    room.instances = [];
    game.globalVariables = Object.assign({}, globals);
    const make = (key, spec) => {
        const inst = new GameObject(key.startsWith('gem') ? 'obj_gem' : 'obj_' + key, spec.x, spec.y, {}, {});
        inst.hp = spec.hp; inst.vspeed = spec.vspeed; inst.hspeed = 0;
        room.instances.push(inst);
        return inst;
    };
    window.__w = {};
    for (const key of Object.keys(specs)) window.__w[key] = make(key, specs[key]);
    return true;
}"""

PAGE_RUN = """([params, collision, kind, order]) => {
    const w = window.__w, game = window.game;
    w.me._collision_other = collision ? w.other : null;
    let answer = null;
    if (kind === 'set') {
        w.me.executeAction({action: 'set_variable', parameters: params}, game);
    } else {
        answer = !!w.me.evaluateCondition({action: 'test_variable', parameters: params}, game);
    }
    const out = [];
    for (const key of order) out.push(w[key].x, w[key].y, w[key].hp, w[key].vspeed);
    out.push(game.globalVariables.score_total === undefined ? -1 : game.globalVariables.score_total,
             game.globalVariables.fresh === undefined ? -1 : game.globalVariables.fresh);
    return [out, answer];
}"""


@pytest.fixture(scope="module")
def page():
    sync_api = pytest.importorskip("playwright.sync_api")
    from export.HTML5.html5_exporter import HTML5Exporter
    out = Path(tempfile.mkdtemp(prefix="html5_scope_")) / "o"
    out.mkdir(parents=True)
    assert HTML5Exporter().export(ROOT / "samples" / "maze_1", out)
    with sync_api.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"no Chromium: {exc}")
        pg = browser.new_page()
        pg.goto(next(out.glob("*.html")).as_uri())
        pg.wait_for_function("window.game && window.game.currentRoom && window.game.currentRoom.instances.length > 3",
                             timeout=20000)
        yield pg
        browser.close()


def _run(page, params, collision, kind):
    page.evaluate(PAGE_SETUP, [SPECS, GLOBALS])
    return page.evaluate(PAGE_RUN, [params, collision, kind, list(ORDER)])


@pytest.mark.parametrize("case", SET_CASES, ids=_id)
def test_set_variable_applies_to_the_same_instances_as_the_desktop(case, page):
    params, collision = case
    state, _ = _run(page, params, collision, "set")
    assert state == pytest.approx(desktop_set(params, collision))


@pytest.mark.parametrize("case", TEST_CASES, ids=_id)
def test_test_variable_reads_the_same_instance_as_the_desktop(case, page):
    params, collision = case
    _, answer = _run(page, params, collision, "test")
    assert answer is desktop_test(params, collision)


def test_a_name_prefix_names_its_own_scope_like_on_kivy(page):
    state, _ = _run(page, {"variable": "global.fresh", "value": "3"}, False, "set")
    assert state[-1] == 3
    state, _ = _run(page, {"variable": "other.hp", "value": "6"}, True, "set")
    assert state[ORDER.index("other") * 4 + 2] == 6 and state[2] == SPECS["me"]["hp"]
    state, _ = _run(page, {"variable": "self.hp", "value": "8"}, False, "set")
    assert state[2] == 8
