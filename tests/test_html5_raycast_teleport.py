"""Go to Room Seamlessly in the HTML5 export (docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md, T2).

Run in headless Chromium where Playwright is installed (the dev box; skipped in CI). In the browser the
room change happens in the middle of a logic step and the new room's Create events run at the start of
ITS first step, so the port applies the arrival once that step has consumed room_start (in the
after_collision phase, before climbing's hook) and shows the pre-change frame in between. These tests
prove "no wrong frame" from the outside: every frame the canvas shows is the old room's (blue ceiling)
or the new room's raycast view (red ceiling) -- never the new room drawn flat or at its authored start --
and every raycast draw of the new room has the camera where the arrival put it.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_html5_raycast_stairs import _page, needs_browser, JS  # noqa: E402

AUTHORED_B = (64.0, 64.0)
MARKER_B = (320.0, 128.0)

RECORDER = """() => {
    window.__draws = []; window.__pixels = [];
    const orig = GameRoom.prototype.renderRaycastView;
    GameRoom.prototype.renderRaycastView = function(ctx) {
        const cam = this.findFirstInstance(this.raycastCamera.camera_object || '');
        window.__draws.push([this.name, cam.x, cam.y, cam.facing_angle]);
        return orig.call(this, ctx);
    };
    const tick = () => {
        const g = window.game, c = g.canvas.getContext('2d');
        const d = c.getImageData(240, 2, 1, 1).data;
        window.__pixels.push([g.currentRoom.name, d[0], d[1], d[2]]);
        requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
}"""


def _make(tmp_path, **kw):
    from test_raycast_seamless_teleport import _project
    proj = tmp_path / "proj"
    proj.mkdir()
    _project(proj, colors=True, via_step=True, **kw)
    return proj


GO = "() => { window.game.globalVariables.go = 1; }"      # fires the action from the room's own step


def test_the_port_registers_the_teleport_pieces():
    assert "registerExtensionAction('go_to_room_seamlessly'" in JS
    assert "registerFrameUpdate(raycastArrivalAfter, 'after_collision');" in JS
    # registered before climbing's, so the carried view height is in place when it eases
    assert JS.index("registerFrameUpdate(raycastArrivalAfter") < JS.index("registerFrameUpdate(raycastClimbBefore)")


@needs_browser
def test_the_camera_arrives_at_the_marker_offset_and_no_wrong_frame_is_shown(tmp_path):
    with _page(_make(tmp_path), tmp_path) as pg:
        pg.evaluate(RECORDER)
        pg.evaluate(GO)
        pg.wait_for_timeout(800)
        res = pg.evaluate("() => ({room: window.game.currentRoom.name, draws: window.__draws, "
                          "pixels: window.__pixels, pending: !!window.game._raycastArrival})")
    assert res["room"] == "room1" and not res["pending"]
    new_draws = [d for d in res["draws"] if d[0] == "room1"]
    assert new_draws
    for _name, x, y, facing in new_draws:
        assert (x, y) != AUTHORED_B and facing != 90, (x, y, facing)
    assert (new_draws[0][1], new_draws[0][2]) == (MARKER_B[0] - 96.0, MARKER_B[1])
    assert new_draws[0][3] == 40
    colours = {tuple(p[1:]) for p in res["pixels"]}
    assert colours <= {(0, 0, 255), (255, 0, 0)}, colours            # blue: old room, red: new room
    assert (255, 0, 0) in colours


@needs_browser
def test_a_held_key_stays_held_across_the_junction(tmp_path):
    with _page(_make(tmp_path), tmp_path) as pg:
        pg.keyboard.down("ArrowUp")
        pg.evaluate(GO)
        pg.wait_for_timeout(400)
        res = pg.evaluate("() => ({room: window.game.currentRoom.name, up: !!window.game.keys['ArrowUp']})")
        pg.keyboard.up("ArrowUp")
    assert res["room"] == "room1" and res["up"]


@needs_browser
def test_a_missing_marker_in_the_new_room_is_a_plain_change(tmp_path):
    with _page(_make(tmp_path, marker_b=False), tmp_path) as pg:
        pg.evaluate(RECORDER)
        pg.evaluate(GO)
        pg.wait_for_timeout(800)
        res = pg.evaluate("() => ({room: window.game.currentRoom.name, draws: window.__draws, "
                          "pending: !!window.game._raycastArrival})")
    assert res["room"] == "room1" and not res["pending"]
    first = [d for d in res["draws"] if d[0] == "room1"][0]
    assert (first[1], first[2]) == AUTHORED_B and first[3] == 90


@needs_browser
def test_a_missing_target_room_does_nothing(tmp_path):
    with _page(_make(tmp_path, target="nowhere"), tmp_path) as pg:
        pg.evaluate(GO)
        pg.wait_for_timeout(500)
        room = pg.evaluate("() => window.game.currentRoom.name")
    assert room == "room0"
