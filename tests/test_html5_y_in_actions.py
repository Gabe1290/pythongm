"""HTML5 export: the position-taking actions mean the same as the desktop's.

The HTML5 engine keeps the author's space natively (y down from the top, vspeed positive down), so unlike the
Kivy export it needed no conversion -- this pins that, with the same cases as tests/test_kivy_y_in_actions.py,
run in the real engine in Chromium (dev box; skipped without Playwright) against the desktop handlers:
jump_to_position, move_towards_point, create_instance (absolute / relative / ``y`` reads), destroy_at_position.
"""
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_kivy_y_in_actions import (  # noqa: E402
    JUMPS, START, _desktop_inst, _desktop_runner)

SETUP = """([start, spots]) => {
    const game = window.game, room = game.currentRoom;
    game.paused = true;
    room.instances = [];
    const me = new GameObject('obj_probe', start.x, start.y, {}, {});
    me.hp = start.hp; me.hspeed = 0; me.vspeed = 0;
    room.instances.push(me);
    window.__me = me;
    window.__others = spots.map(([x, y], i) => {
        const o = new GameObject('obj_' + i, x, y, {}, {});
        room.instances.push(o);
        return o;
    });
    return true;
}"""


@pytest.fixture(scope="module")
def page():
    sync_api = pytest.importorskip("playwright.sync_api")
    from export.HTML5.html5_exporter import HTML5Exporter
    out = Path(tempfile.mkdtemp(prefix="html5_y_")) / "o"
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


def _act(page, action, params, spots=()):
    page.evaluate(SETUP, [START, [list(s) for s in spots]])
    return page.evaluate("""([action, params]) => {
        const me = window.__me, game = window.game;
        me.executeAction({action: action, parameters: params}, game);
        return {x: me.x, y: me.y, hspeed: me.hspeed, vspeed: me.vspeed,
                created: game.currentRoom.instances.filter(i => i.name === 'obj_wall')
                    .map(i => [i.name, i.x, i.y]),
                destroyed: window.__others.map(o => !!o.toDestroy)};
    }""", [action, params])


@pytest.mark.parametrize("params", JUMPS, ids=lambda p: f"{p['x']},{p['y']}{'+' if p.get('relative') else ''}")
def test_jump_to_position_lands_where_the_desktop_does(params, page):
    from runtime.action_executor import ActionExecutor
    ref = _desktop_inst()
    ActionExecutor(game_runner=_desktop_runner([ref])).execute_jump_to_position_action(ref, dict(params))
    got = _act(page, "jump_to_position", params)
    assert (got["x"], got["y"]) == pytest.approx((ref.x, ref.y))


@pytest.mark.parametrize("target", [(100, 200), (10, 20), (0, 0), (300, 5), ("x + 100", "y + 50")])
def test_move_towards_point_heads_to_the_same_place(target, page):
    from runtime.action_executor import ActionExecutor
    params = {"x": str(target[0]), "y": str(target[1]), "speed": "4"}
    ref = _desktop_inst()
    ActionExecutor(game_runner=_desktop_runner([ref])).execute_move_towards_point_action(ref, dict(params))
    got = _act(page, "move_towards_point", params)
    assert (got["hspeed"], got["vspeed"]) == pytest.approx((ref.hspeed, ref.vspeed), abs=1e-6)


@pytest.mark.parametrize("params,expected", [
    ({"object": "obj_wall", "x": "100", "y": "200"}, (100, 200)),
    ({"object": "obj_wall", "x": "x + 5", "y": "y + 7"}, (15, 27)),
    ({"object": "obj_wall", "x": "32", "y": "16", "relative": True}, (42, 36)),
    ({"object": "obj_wall", "x": "0", "y": "-20", "relative": True}, (10, 0)),
])
def test_create_instance_appears_at_the_authors_position(params, expected, page):
    got = _act(page, "create_instance", params)
    gems = [c for c in got["created"] if c[0] == "obj_wall"]
    assert len(gems) == 1 and (gems[0][1], gems[0][2]) == pytest.approx(expected)


@pytest.mark.parametrize("params", [
    {"x": "100", "y": "200", "radius": "40"},
    {"x": "100", "y": "200", "radius": "0"},
    {"x": "0", "y": "40", "radius": "20", "relative": True},
    {"x": "x", "y": "y", "radius": "100"},
])
def test_destroy_at_position_hits_the_same_instances(params, page):
    from runtime.action_executor import ActionExecutor
    spots = [(100, 200), (110, 215), (100, 240), (50, 60), (10, 60), (10, 20), (400, 400), (100, 190)]
    caller = _desktop_inst()
    others = [_desktop_inst(x=gx, y=gy, object_name=f"obj_{i}") for i, (gx, gy) in enumerate(spots)]
    ActionExecutor(game_runner=_desktop_runner([caller] + others)).execute_destroy_at_position_action(
        caller, {"object": "all", **params})
    expected = [bool(o.to_destroy) for o in others]
    got = _act(page, "destroy_at_position", {"object": "all", **params}, spots)
    assert got["destroyed"] == expected
