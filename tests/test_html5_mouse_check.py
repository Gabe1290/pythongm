"""HTML5 export: the if_condition mouse_check condition.

It always took the else branch (the engine tracked no mouse-button state), so "if the left
button is pressed" / "if the mouse is over me" never held in a browser. Now the engine keeps the
held buttons (``game.mouseButtons``: DOM button 0/1/2, a touch is the left button, any release or a
blur ends the hold) next to the pointer it already tracked, and ``mouse_check`` answers as the
desktop runtime does. "In region" has no region parameters in the editor: never true.

Always runs: the structure. On the dev box (Playwright + Chromium) a real export is driven with
real mouse events on the canvas.
"""
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ENGINE = (ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8").replace("\r\n", "\n")


def test_the_condition_and_the_button_state_exist():
    assert "case 'mouse_check': {" in ENGINE
    for check in ("Left button pressed", "Middle button pressed", "Right button pressed", "Over object"):
        assert f"check === '{check}'" in ENGINE
    assert "this.mouseButtons = {left: false, middle: false, right: false};" in ENGINE
    assert "window.addEventListener('blur'" in ENGINE
    assert "screenToRoom(sx, sy) {" in ENGINE and "this.mouseButtons.left = true;" in ENGINE


def test_the_stale_note_that_mouse_check_is_unported_is_gone():
    assert "mouse_check is the one\n                // condition_type NOT ported" not in ENGINE


# -- real browser (dev box only) ---------------------------------------------------------

@pytest.fixture(scope="module")
def page():
    sync_api = pytest.importorskip("playwright.sync_api")
    from export.HTML5.html5_exporter import HTML5Exporter
    src = ROOT / "samples" / "maze_1"
    out = Path(tempfile.mkdtemp(prefix="html5_mouse_")) / "out"
    out.mkdir(parents=True)
    assert HTML5Exporter().export(src, out)
    html = next(out.glob("*.html"))
    with sync_api.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"no Chromium: {exc}")
        pg = browser.new_page(viewport={"width": 900, "height": 700})
        pg.goto(html.as_uri())
        pg.wait_for_function("window.game && window.game.currentRoom && window.game.currentRoom.instances.filter(i => i.sprite).length > 10",
                             timeout=20000)
        yield pg
        browser.close()


_HELPERS = """
window.__q = (check, inst) => (inst || window.__inst).evaluateCondition(
    {action: 'if_condition', parameters: {condition_type: 'mouse_check', check: check}}, window.game);
window.__client = (inst) => {            // the page position of an instance's centre
    const c = window.game.canvas, r = c.getBoundingClientRect();
    const w = inst.spriteInfo ? inst.spriteInfo.width : 32, h = inst.spriteInfo ? inst.spriteInfo.height : 32;
    return [r.left + c.clientLeft + (inst.x + w / 2) * c.clientWidth / c.width,
            r.top + c.clientTop + (inst.y + h / 2) * c.clientHeight / c.height];
};
0;   // Playwright CALLS a function an evaluated string ends with, so end on a plain value
"""


def _two_instances(page):
    page.evaluate(_HELPERS)
    return page.evaluate("""(() => {
        const sprited = window.game.currentRoom.instances.filter(i => i.sprite && !i.toDestroy);
        const a = sprited[0];
        const b = sprited.find(i => Math.abs(i.x - a.x) > 64 || Math.abs(i.y - a.y) > 64);
        window.__inst = a; window.__other = b;
        return [window.__client(a), window.__client(b)];
    })()""")


def test_buttons_follow_real_mouse_presses(page):
    (ax, ay), _ = _two_instances(page)
    page.mouse.move(ax, ay)
    states = lambda: page.evaluate(  # noqa: E731
        "['Left button pressed', 'Middle button pressed', 'Right button pressed'].map(c => window.__q(c))")
    assert states() == [False, False, False]
    page.mouse.down(button="left")
    assert states() == [True, False, False]
    page.mouse.down(button="right")
    assert states() == [True, False, True]
    page.mouse.up(button="left")
    assert states() == [False, False, True]
    page.mouse.up(button="right")
    page.mouse.down(button="middle")
    assert states() == [False, True, False]
    page.mouse.up(button="middle")
    assert states() == [False, False, False]


def test_over_object_follows_the_pointer_and_uses_the_instance_box(page):
    (ax, ay), (bx, by) = _two_instances(page)
    page.mouse.move(ax, ay)
    assert page.evaluate("[window.__q('Over object'), window.__q('Over object', window.__other)]") == [True, False]
    page.mouse.move(bx, by)
    assert page.evaluate("[window.__q('Over object'), window.__q('Over object', window.__other)]") == [False, True]
    page.mouse.move(ax, ay)                                   # no click needed: the pointer is tracked on move
    assert page.evaluate("window.__q('Over object')") is True


def test_a_release_outside_the_canvas_ends_the_hold_and_in_region_is_never_true(page):
    (ax, ay), _ = _two_instances(page)
    page.mouse.move(ax, ay)
    page.mouse.down(button="left")
    page.mouse.move(2, 2)                                      # drag off the canvas
    page.mouse.up(button="left")
    assert page.evaluate("window.__q('Left button pressed')") is False
    assert page.evaluate("[window.__q('In region'), window.__q('')]") == [False, False]


def test_a_touch_is_the_left_button_and_ends_with_the_finger(page):
    (ax, ay), _ = _two_instances(page)
    page.evaluate("""([x, y]) => {
        const mk = (type) => new TouchEvent(type, {cancelable: true, bubbles: true,
            changedTouches: [new Touch({identifier: 1, target: window.game.canvas, clientX: x, clientY: y})]});
        window.game.canvas.dispatchEvent(mk('touchstart'));
    }""", [ax, ay])
    assert page.evaluate("[window.__q('Left button pressed'), window.__q('Over object')]") == [True, True]
    page.evaluate("window.dispatchEvent(new TouchEvent('touchend', {bubbles: true}))")
    assert page.evaluate("window.__q('Left button pressed')") is False


def test_spriteless_instances_are_never_over_and_views_translate_the_pointer(page):
    page.evaluate(_HELPERS)
    got = page.evaluate("""(() => {
        const room = window.game.currentRoom;
        const probe = new GameObject('probe', 0, 0, {}, {});          // no sprite
        window.game.pointer = {x: 1, y: 1};
        const spriteless = window.__q('Over object', probe);
        room.viewsEnabled = true;                                      // desktop screen_to_room: undo the view's translation
        room.views[0].visible = true;
        Object.assign(room.views[0], {port_x: 0, port_y: 0, port_w: 640, port_h: 480, view_x: 100, view_y: 50});
        const mapped = room.screenToRoom(10, 20);
        const outside = room.screenToRoom(700, 20);
        room.viewsEnabled = false;
        return [spriteless, mapped, outside, room.screenToRoom(10, 20)];
    })()""")
    assert got == [False, [110, 70], [700, 20], [10, 20]]
