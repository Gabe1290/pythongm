#!/usr/bin/env python3
"""Run the micro:bit simulator in Python AND in real Chromium and diff them.

Local development tool (CI has no JS engine; ``tests/test_microbit_html5_sim.py``
runs this same comparison when Playwright + Chromium happen to be installed
and skips otherwise). A seeded random script of simulator calls is applied to
``extensions/microbit/simulator.py`` and to the port in ``export_html5.js``;
after every call the observable state and the events ``update`` reported must
be identical.

    py -3.12 tools/microbit_js_parity.py [--seeds 40] [--steps 400]
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

JS = ROOT / "extensions" / "microbit" / "export_html5.js"

IMAGES = ["HEART", "happy", "SAD", "00000:09990:09990:09990:00000", "nonsense",
          "09090:99999", "ARROW_N"]
TEXTS = ["Hi", "micro:bit", "Hé!", "", "A", "0123456789"]
MELODIES = ["DADADADUM", "ode", "c4:4 d e:2 r", "g#5:1 ab:2 e#:3 cb:1", "zz", "", "c9"]
NUMBERS = [0, 7, -3, 12, 100, 3.5, 12345]


def make_script(seed, steps):
    rng = random.Random(seed)
    script = []
    for _ in range(steps):
        r = rng.random()
        if r < 0.40:
            script.append(["update", rng.choice([0.0, 0.004, 0.016, 0.016, 0.033, 0.2, 1.5])])
        elif r < 0.46:
            script.append(["show_image", rng.choice(IMAGES), rng.choice([0, 0.2, 1.0])])
        elif r < 0.52:
            script.append(["scroll_text", rng.choice(TEXTS), rng.choice([0.05, 0.15])])
        elif r < 0.55:
            script.append(["show_number", rng.choice(NUMBERS)])
        elif r < 0.58:
            script.append(["set_pixel", rng.randint(-1, 5), rng.randint(-1, 5), rng.randint(-2, 12)])
        elif r < 0.60:
            script.append(["clear"])
        elif r < 0.62:
            script.append(["set_brightness", rng.randint(-10, 300)])
        elif r < 0.66:
            script.append(["play_tone", rng.choice([0, 262, 440, 30000, -5]), rng.choice([0, 20, 500])])
        elif r < 0.70:
            script.append(["play_melody", rng.choice(MELODIES), rng.choice([60, 120, 240, 0])])
        elif r < 0.72:
            script.append(["stop_sound"])
        elif r < 0.74:
            script.append(["set_radio_group", rng.choice([0, 7, 255, 999, -4])])
        elif r < 0.76:
            script.append(["radio_send", rng.choice([1, 2.5, "hello", "x" * 40, True])])
        elif r < 0.78:
            script.append(["radio_receive", rng.choice([3, "ping"])])
        elif r < 0.84:
            script.append(["set_button", rng.choice(["a", "b"]), rng.random() < 0.5])
        elif r < 0.86:
            script.append(["set_logo_touched", rng.random() < 0.5])
        elif r < 0.88:
            script.append(["set_pin_touched", rng.choice([0, 1, 2]), rng.random() < 0.5])
        elif r < 0.94:
            script.append(["set_acceleration"] + [rng.choice([0, 1024, -1024, 500, -2500, 4000, 9000, 150]) for _ in range(3)])
        elif r < 0.955:
            script.append(["shake"])
        elif r < 0.97:
            script.append(["set_compass_heading", rng.randint(-720, 720)])
        elif r < 0.985:
            script.append(["set_sound_level", rng.choice([0, 100, 150, 200, 255])])
        else:
            script.append(["set_light_level", rng.randint(-5, 300)])
    return script


def snapshot(sim):
    return {
        "display": [row[:] for row in sim.display], "brightness": sim.brightness, "tone": sim.tone,
        "busy": bool(sim.busy), "sound_busy": bool(sim.sound_busy),
        "gesture": sim.current_gesture, "group": sim.radio_group,
        "accel": list(sim.acceleration), "compass": sim.compass_heading,
        "light": sim.light_level, "sound_level": sim.sound_level,
        "buttons": [bool(sim.buttons["a"]), bool(sim.buttons["b"])],
        "logo": bool(sim.logo_touched),
        "pins": [bool(sim.pins_touched[p]) for p in (0, 1, 2)],
    }


def run_python(script):
    from extensions.microbit.simulator import MicrobitSimulator
    sim = MicrobitSimulator()
    trace = []
    for op in script:
        name, args = op[0], op[1:]
        events, error = None, None
        try:
            if name == "update":
                events = [[k, list(d) if isinstance(d, tuple) else d] for k, d in sim.update(*args)]
            elif name == "show_number":
                v = args[0]
                sim.show_number(int(v) if isinstance(v, float) and v.is_integer() else v)
            elif name == "set_button":
                sim.set_button(*args)
            else:
                getattr(sim, name)(*args)
        except ValueError:
            error = True
        trace.append({"events": events, "error": error, "state": snapshot(sim)})
    return trace


JS_RUNNER = """
(script) => {
  const sim = new window.__pygmMicrobit.MicrobitSimulator();
  const snap = () => ({
    display: sim.display, brightness: sim.brightness, tone: sim.tone,
    busy: !!sim.busy, sound_busy: !!sim.sound_busy, gesture: sim.current_gesture,
    group: sim.radio_group, accel: Array.from(sim.acceleration),
    compass: sim.compass_heading, light: sim.light_level, sound_level: sim.sound_level,
    buttons: [!!sim.buttons.a, !!sim.buttons.b], logo: !!sim.logo_touched,
    pins: [0, 1, 2].map(p => !!sim.pins_touched[p]),
  });
  const out = [];
  for (const op of script) {
    const name = op[0], args = op.slice(1);
    let events = null, error = null;
    try {
      if (name === 'update') events = sim.update(...args);
      else sim[name](...args);
    } catch (e) { error = true; }
    out.push({events, error, state: JSON.parse(JSON.stringify(snap()))});
  }
  return out;
}
"""


def run_js(page, script):
    return page.evaluate(JS_RUNNER, script)


def normalise(trace):
    return json.loads(json.dumps(trace))


def first_difference(py, js):
    for i, (a, b) in enumerate(zip(py, js)):
        if a != b:
            return i, a, b
    return None


def available():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch().close()
        return True
    except Exception:
        return False


def compare(seeds=40, steps=400):
    """Returns a list of (seed, index, python_entry, js_entry) mismatches."""
    from playwright.sync_api import sync_playwright
    bad = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content("<html><body></body></html>")
        page.add_script_tag(content=JS.read_text(encoding="utf-8"))
        for seed in range(seeds):
            script = make_script(seed, steps)
            diff = first_difference(normalise(run_python(script)), run_js(page, script))
            if diff:
                bad.append((seed, script[diff[0]], diff[1], diff[2]))
        browser.close()
    return bad


def main(argv):
    seeds = int(argv[argv.index("--seeds") + 1]) if "--seeds" in argv else 40
    steps = int(argv[argv.index("--steps") + 1]) if "--steps" in argv else 400
    bad = compare(seeds, steps)
    for seed, op, py, js in bad[:3]:
        print(f"seed {seed}: first difference at op {op}")
        print("  python:", json.dumps(py)[:600])
        print("  js    :", json.dumps(js)[:600])
    print(f"{seeds} seeds x {steps} ops: {'OK, identical' if not bad else str(len(bad)) + ' differ'}")
    return 1 if bad else 0


# ---------------------------------------------------------------------------
# Stage P / H3: layout and drawing
# ---------------------------------------------------------------------------

def _plain(value):
    """Tuples -> lists, dataclasses -> dicts, so the Python layout compares to
    the JSON the browser returns."""
    import dataclasses
    if dataclasses.is_dataclass(value):
        return {k: _plain(v) for k, v in dataclasses.asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


LAYOUT_RUNNER = """
(cases) => {
  const M = window.__pygmMicrobit;
  return cases.map(([cx, cy, scale, level, brightness]) => {
    const lay = M.boardLayout(cx, cy, scale);
    const strip = M.stripLayout(lay);
    return {lay, strip, led: M.ledColor(level, brightness)};
  });
}
"""


def layout_cases(n=400, seed=7):
    rng = random.Random(seed)
    cases = [[400, 300, 1.0, 5, 255], [0.5, 0.5, 0.5, 9, 128], [100.5, 99.5, 1.5, 0, 0]]
    for _ in range(n):
        cases.append([rng.choice([rng.uniform(-50, 900), rng.randint(0, 900) + 0.5, rng.randint(0, 900)]),
                      rng.choice([rng.uniform(-50, 700), rng.randint(0, 700) + 0.5, rng.randint(0, 700)]),
                      rng.choice([0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, rng.uniform(0.1, 4.0)]),
                      rng.randint(-1, 10), rng.randint(-5, 300)])
    return cases


def compare_layout(n=400):
    """Mismatches between layout.py and the JS port over many positions/scales
    (including exact .5 ties, where Python's round and Math.round differ)."""
    from extensions.microbit.layout import board_layout, strip_layout, led_color
    from playwright.sync_api import sync_playwright
    cases = layout_cases(n)
    bad = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content("<html><body></body></html>")
        page.add_script_tag(content=JS.read_text(encoding="utf-8"))
        got = page.evaluate(LAYOUT_RUNNER, cases)
        browser.close()
    for case, js in zip(cases, got):
        cx, cy, scale, level, brightness = case
        lay = board_layout(cx, cy, scale)
        want = {"lay": _plain(lay), "strip": _plain(strip_layout(lay)),
                "led": list(led_color(level, brightness))}
        mine = {"lay": js["lay"], "strip": js["strip"], "led": js["led"]}
        for key in ("cx", "cy", "scale"):
            mine["lay"].pop(key, None)
            want["lay"].pop(key, None)
        if json.loads(json.dumps(want)) != mine:
            bad.append((case, want, mine))
    return bad


PIXEL_STATES = [
    [],
    [["show_image", "HEART", 0]],
    [["show_image", "HAPPY", 0], ["set_brightness", 120]],
    [["set_button", "a", True], ["set_pin_touched", 1, True], ["set_logo_touched", True]],
    [["set_button", "b", True], ["play_tone", 440, 5000], ["update", 0.01]],
    [["set_acceleration", 700, -400, -500], ["update", 0.1], ["set_light_level", 200],
     ["set_temperature", 30], ["set_compass_heading", 90], ["set_sound_level", 60]],
    [["shake"], ["update", 0.05]],
]


def _points(lay, strip, sim):
    """(name, x, y) the two renderers must agree on: where things land."""
    from extensions.microbit.layout import tilt_to_pos, slider_fraction
    from extensions.microbit.renderer import _slider_value
    pts = []
    bx0, by0, bw0, bh0 = lay.body
    pts.append(("body", bx0 + 6, by0 + bh0 // 2))
    pts.append(("body_edge", bx0, by0 + bh0 // 2))
    pts.append(("corner_mark", bx0 + 4, by0 + 4))
    for y in range(5):
        for x in range(5):
            cx, cy = lay.led_center(x, y)
            pts.append((f"led{x}{y}", cx, cy))
    for name, (bx, by, br) in lay.buttons.items():
        pts.append((f"button_{name}", bx + int(br * 0.7), by))
    lx, ly, rx, ry = lay.logo
    pts.append(("logo", lx, ly + ry // 2))
    for pin in ("0", "1", "2", "3V", "GND"):
        px, py, pw, ph = lay.pads[pin]
        pts.append((f"pad{pin}", px + pw // 2, py + ph - 5))
    kx, ky, kr = lay.speaker
    pts.append(("speaker", kx, ky))
    tx, ty, tw, th = strip.tilt
    pts.append(("tilt_corner", tx + 2, ty + th - 3))
    dx, dy = tilt_to_pos(strip.tilt, sim.acceleration[0], sim.acceleration[1])
    pts.append(("tilt_dot", dx, dy))
    sx, sy, sw, sh = strip.shake
    pts.append(("shake", sx + 4, sy + 4))
    pts.append(("panel_left", strip.panel_left[0] + 3, strip.panel_left[1] + strip.panel_left[3] // 2))
    pts.append(("panel_right", strip.panel_right[0] + 3, strip.panel_right[1] + strip.panel_right[3] // 2))
    for name, (sx0, sy0, sw0, sh0) in strip.sliders.items():
        filled = int(sw0 * slider_fraction(name, _slider_value(sim, name)))
        pts.append((f"slider_{name}_end", sx0 + sw0 - 4, sy0 + sh0 // 2))
        pts.append((f"slider_{name}_knob", sx0 + filled, sy0 + sh0 // 2))
    return pts


PIXEL_RUNNER = """
([ops, cx, cy, scale, pts]) => {
  const M = window.__pygmMicrobit;
  const sim = new M.MicrobitSimulator();
  for (const op of ops) {
    try { if (op[0] === 'update') sim.update(...op.slice(1)); else sim[op[0]](...op.slice(1)); } catch (e) {}
  }
  const canvas = document.createElement('canvas'); canvas.width = 900; canvas.height = 700;
  const ctx = canvas.getContext('2d', {willReadFrequently: true});
  ctx.fillStyle = 'rgb(0,0,0)'; ctx.fillRect(0, 0, 900, 700);
  const inst = {name: 'microbit_t', x: cx, y: cy, sprite: null, spriteInfo: null, visible: true,
                objectData: {microbit_scale: scale}, instanceData: {}, _mb: sim};
  M.drawOverlay(inst, ctx);
  return pts.map(([name, x, y]) => [name, Array.from(ctx.getImageData(x, y, 1, 1).data.slice(0, 3))]);
}
"""


def compare_pixels(tolerance=2):
    """Render the same board state with pygame and with canvas 2D and compare
    the colour at every point where a control should land."""
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    from types import SimpleNamespace
    from extensions.microbit.simulator import MicrobitSimulator
    from extensions.microbit.layout import layout_for, strip_layout
    from extensions.microbit.renderer import draw_overlay
    from extensions.microbit.state import attach_simulator
    from playwright.sync_api import sync_playwright
    pygame.init()
    bad = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content("<html><body></body></html>")
        page.add_script_tag(content=JS.read_text(encoding="utf-8"))
        for ops in PIXEL_STATES:
            for (cx, cy, scale) in ((450, 330, 1.0), (430.5, 300.5, 0.8)):
                sim = MicrobitSimulator()
                for op in ops:
                    if op[0] == "update":
                        sim.update(*op[1:])
                    else:
                        getattr(sim, op[0])(*op[1:])
                inst = SimpleNamespace(x=cx, y=cy, sprite=None, visible=True,
                                       object_data={"microbit_scale": scale}, extension_state={})
                attach_simulator(inst, sim)
                screen = pygame.Surface((900, 700))
                screen.fill((0, 0, 0))
                draw_overlay(inst, screen)
                lay = layout_for(inst)
                pts = _points(lay, strip_layout(lay), sim)
                got = page.evaluate(PIXEL_RUNNER, [ops, cx, cy, scale, [list(p) for p in pts]])
                for (name, x, y), (_, rgb) in zip(pts, got):
                    want = list(screen.get_at((x, y)))[:3]
                    if max(abs(a - b) for a, b in zip(want, rgb)) > tolerance:
                        bad.append((ops, scale, name, (x, y), want, rgb))
        browser.close()
    return bad


# ---------------------------------------------------------------------------
# Stage P / H4: hit tests and the tilt / slider maths
# ---------------------------------------------------------------------------

INPUT_RUNNER = """
(cases) => {
  const M = window.__pygmMicrobit;
  return cases.map(([cx, cy, scale, x, y, name]) => {
    const lay = M.boardLayout(cx, cy, scale);
    const strip = M.stripLayout(lay);
    return {hit: M.hitTest(lay, x, y), strip: M.stripHitTest(strip, x, y),
            tilt: M.tiltFromPos(strip.tilt, x, y),
            slider: M.sliderFromX(name, strip.sliders[name], x)};
  });
}
"""


def compare_input(n=2500, seed=11):
    """Mismatches between the Python and JS hit tests / tilt / slider maths at
    random points, biased toward the edges where rounding and inequalities
    (< vs <=) differ."""
    from extensions.microbit.layout import (board_layout, strip_layout, hit_test, strip_hit_test,
                                            tilt_from_pos, slider_value, SLIDERS)
    from playwright.sync_api import sync_playwright
    rng = random.Random(seed)
    names = list(SLIDERS)
    cases = []
    for _ in range(n):
        cx, cy = rng.choice([400, 320.5, 123, 640.5]), rng.choice([300, 200.5, 77])
        scale = rng.choice([0.5, 1.0, 1.25, 2.0])
        lay = board_layout(cx, cy, scale)
        strip = strip_layout(lay)
        # a point near some control, or anywhere
        anchor = rng.choice([lay.buttons["a"][:2], lay.buttons["b"][:2], lay.logo[:2],
                             strip.tilt[:2], strip.shake[:2], strip.sliders["light"][:2],
                             strip.sliders["compass"][:2], lay.pads["1"][:2], (cx, cy)])
        x = anchor[0] + rng.randint(-40, 160)
        y = anchor[1] + rng.randint(-40, 60)
        cases.append([cx, cy, scale, x, y, rng.choice(names)])
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content("<html><body></body></html>")
        page.add_script_tag(content=JS.read_text(encoding="utf-8"))
        got = page.evaluate(INPUT_RUNNER, cases)
        browser.close()
    bad = []
    hits = set()
    for case, js in zip(cases, got):
        cx, cy, scale, x, y, name = case
        lay = board_layout(cx, cy, scale)
        strip = strip_layout(lay)
        want = {"hit": hit_test(lay, x, y), "strip": strip_hit_test(strip, x, y),
                "tilt": list(tilt_from_pos(strip.tilt, x, y)),
                "slider": slider_value(name, strip.sliders[name], x)}
        hits.add((want["hit"], want["strip"]))
        if want != js:
            bad.append((case, want, js))
    return bad, hits


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
