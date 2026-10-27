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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
