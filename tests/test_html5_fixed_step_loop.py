"""The HTML5 game loop runs 60 logic steps per real second at ANY refresh rate.

It used to take one step per requestAnimationFrame, so a 90/120 Hz phone or
monitor ran every exported game up to 2x too fast (TODO.md, found 2026-11-03).
Always runs: the loop's structure. On the dev box (Playwright + Chromium) a
real export is driven with a fake animation-frame clock at 30..144 Hz and the
logic steps are counted.
"""
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

ENGINE = (ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _loop():
    start = ENGINE.index("    gameLoop(frameTime) {")
    return ENGINE[start:ENGINE.index("_renderFadeTransition() {", start)]


def test_loop_is_a_fixed_step_accumulator_not_one_step_per_frame():
    loop = _loop()
    assert "const STEP_MS = 1000 / 60;" in loop
    assert "this._stepAcc" in loop and "this._logicStep()" in loop
    assert "requestAnimationFrame((t) => this.gameLoop(t))" in loop
    # the simulation lives in _logicStep, no longer straight in the frame callback
    assert "this.currentRoom.step(this)" not in loop
    body = ENGINE[ENGINE.index("    _logicStep() {"):ENGINE.index("    gameLoop(frameTime) {")]
    for call in ("this.processKeyboard()", "runExtensionFrameUpdates(this)", "this.currentRoom.step(this)"):
        assert call in body
    # drawing is still once per animation frame, after the steps
    assert loop.index("this._logicStep()") < loop.index("this.currentRoom.render(this.ctx)")


def test_a_stalled_tab_cannot_fast_forward_the_game():
    loop = _loop()
    assert "dtMs > 250" in loop and "MAX_STEPS_PER_FRAME" in loop


# -- real browser (dev box only) -------------------------------------------------

_INIT = """
window.__q = []; window.__t = 0;
window.requestAnimationFrame = cb => { window.__q.push(cb); return 1; };
performance.now = () => window.__t;
"""

_DRIVE = """([hz, seconds, jitter]) => {
    const dt = 1000 / hz; window.__steps = 0;
    for (let i = 0; i < Math.round(hz * seconds); i++) {
        window.__t += dt + (i % 2 ? jitter : -jitter);
        const q = window.__q; window.__q = [];
        q.forEach(cb => cb(window.__t));
    }
    return window.__steps;
}"""


@pytest.fixture(scope="module")
def page():
    sync_api = pytest.importorskip("playwright.sync_api")
    import junior_maze_lesson as jm
    from export.HTML5.html5_exporter import HTML5Exporter
    tmp = Path(tempfile.mkdtemp())
    proj, out = tmp / "p", tmp / "o"
    proj.mkdir()
    out.mkdir()
    jm.build_finished(proj)
    assert HTML5Exporter().export(proj, out)
    html = next(out.glob("*.html"))
    with sync_api.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:               # no Chromium installed
            pytest.skip(f"no Chromium: {exc}")
        pg = browser.new_page()
        pg.add_init_script(_INIT)
        pg.goto(html.as_uri())
        pg.wait_for_timeout(1500)
        pg.evaluate("""() => { const o = Game.prototype._logicStep;
            Game.prototype._logicStep = function () { window.__steps++; return o.call(this); }; }""")
        yield pg
        browser.close()


@pytest.mark.parametrize("hz,jitter", [(60, 0), (60, 0.8), (50, 0), (75, 0), (90, 0), (120, 0), (144, 0), (30, 0)])
def test_sixty_logic_steps_a_second_at_any_refresh_rate(page, hz, jitter):
    steps = page.evaluate(_DRIVE, [hz, 2.0, jitter])
    assert abs(steps - 120) <= 2, f"{hz} Hz gave {steps} steps in 2 s (want 120)"


def test_a_long_stall_drops_the_backlog(page):
    steps = page.evaluate("""() => { window.__steps = 0; window.__t += 10000;
        const q = window.__q; window.__q = []; q.forEach(cb => cb(window.__t)); return window.__steps; }""")
    assert steps <= 1
