"""The Thymio activity sheets (docs/thymio_fiches/) only promise what the simulator really does.

Every reference solution in tools/thymio_fiches_solutions.py is copied onto its starter project
(samples/thymio_fiches_1..3) and run in the real GameRunner loop with scripted key presses (the arrow keys and the
space bar press the robot's buttons). The numbers asserted here are the ones quoted in the sheets.
"""
import json
import math
import os
import shutil
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest

pygame = pytest.importorskip("pygame")

from tools.thymio_fiches_solutions import PROGRAMS  # noqa: E402

SAMPLES = ("thymio_fiches_1", "thymio_fiches_2", "thymio_fiches_3")


@pytest.fixture(autouse=True)
def _thymio_enabled(monkeypatch):
    from events import plugin_loader
    real = plugin_loader.is_extension_enabled
    monkeypatch.setattr(plugin_loader, "is_extension_enabled",
                        lambda folder, default=True: True if folder == "thymio" else real(folder, default))


def run_program(name, frames, keys=None):
    """Run PROGRAMS[name]; return one dict per frame: x, y, angle, top, bottom_left, circle, vars, prox, ground."""
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRunner
    from extensions.thymio.state import simulator_of
    prog = PROGRAMS[name]
    root = Path(tempfile.mkdtemp(prefix="fiche_")) / prog["sample"]
    shutil.copytree(REPO_ROOT / "samples" / prog["sample"], root)
    path = root / "objects" / "thymio_1.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["events"] = {k: {"actions": v} for k, v in prog["events"].items()}
    path.write_text(json.dumps(obj), encoding="utf-8")

    load_all_plugins()
    pygame.init()
    runner = GameRunner(str(root / "project.json"))
    frames_seen, keys, real = [], keys or {}, pygame.time.Clock

    class Clock:
        n = 0

        def tick(self, fps=0):
            Clock.n += 1
            for kind, key in keys.get(Clock.n, []):
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN if kind == "down" else pygame.KEYUP,
                                                     key=key, mod=0, unicode=""))
            bot = next((i for i in runner.current_room.instances if i.object_name == "thymio_1"), None)
            if bot is not None:
                sim = simulator_of(bot)
                frames_seen.append({
                    "x": sim.x, "y": sim.y, "angle": sim.angle, "top": tuple(sim.leds.top),
                    "bottom_left": tuple(sim.leds.bottom_left), "bottom_right": tuple(sim.leds.bottom_right),
                    "circle": list(sim.leds.circle), "prox": list(sim.sensors.proximity),
                    "ground": list(sim.sensors.ground_delta),
                    "compteur": getattr(bot, "compteur", None), "etat": getattr(bot, "etat", None),
                    "note": getattr(bot, "note", None), "tone": sim.current_sound_frequency,
                    "playing": sim.sound_playing, "dur": sim.current_sound_duration,
                    "busy": bool(pygame.mixer.get_init() and pygame.mixer.Channel(4).get_busy())})
            if Clock.n >= frames:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return 16

        def get_fps(self):
            return 60.0
    pygame.time.Clock = Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real
    return frames_seen


def tap(frame, key, hold=3):
    return {frame: [("down", key)], frame + hold: [("up", key)]}


def keys_of(*parts):
    out = {}
    for p in parts:
        for f, ev in p.items():
            out.setdefault(f, []).extend(ev)
    return out


K = pygame


def test_every_solution_names_a_real_sample_and_real_events():
    from extensions.thymio.events import THYMIO_EVENT_TYPES
    from extensions.thymio.actions import THYMIO_ACTIONS
    for name, prog in PROGRAMS.items():
        assert prog["sample"] in SAMPLES and (REPO_ROOT / "samples" / prog["sample"] / "project.json").exists(), name
        for event, actions in prog["events"].items():
            assert event in THYMIO_EVENT_TYPES, (name, event)      # every event is in the Thymio tab
            for a in actions:
                assert a["action"] in THYMIO_ACTIONS or a["action"] in ("start_block", "end_block"), (name, a)


def test_starter_projects_each_hold_one_robot_with_no_program():
    for sample in SAMPLES:
        project = json.loads((REPO_ROOT / "samples" / sample / "project.json").read_text(encoding="utf-8"))
        assert project["settings"]["active_extensions"] == ["thymio"]
        robot = json.loads((REPO_ROOT / "samples" / sample / "objects" / "thymio_1.json").read_text(encoding="utf-8"))
        assert robot["is_thymio"] is True and robot["events"] == {}
        room = json.loads((REPO_ROOT / "samples" / sample / "rooms" / "room0.json").read_text(encoding="utf-8"))
        assert [i["object_name"] for i in room["instances"]].count("thymio_1") == 1


def test_sprites_are_centred_so_the_drawn_wall_is_the_wall_the_sensors_feel():
    for sample in SAMPLES:
        project = json.loads((REPO_ROOT / "samples" / sample / "project.json").read_text(encoding="utf-8"))
        for s in project["assets"]["sprites"].values():
            assert (s["origin_x"], s["origin_y"]) == (s["width"] // 2, s["height"] // 2), (sample, s["name"])


def test_fiche1_each_button_lights_its_led_and_centre_turns_them_off():
    r = run_program("fiche1_boutons", 60, keys_of(tap(5, K.K_UP), tap(15, K.K_DOWN), tap(25, K.K_LEFT),
                                                  tap(35, K.K_RIGHT), tap(50, K.K_SPACE)))
    assert r[12]["top"] == (0, 32, 0)
    assert r[22]["top"] == (32, 0, 0)
    assert r[32]["bottom_left"] == (0, 0, 32)
    assert r[42]["bottom_right"] == (0, 0, 32)
    assert r[58]["top"] == (0, 0, 0) and r[58]["bottom_left"] == (0, 0, 0)


def test_fiche2_mixed_colours_and_the_circle():
    r = run_program("fiche2_couleurs", 70, keys_of(tap(3, K.K_UP), tap(13, K.K_DOWN), tap(23, K.K_LEFT),
                                                   tap(33, K.K_RIGHT), tap(43, K.K_SPACE)))
    assert [r[i]["top"] for i in (9, 19, 29, 39)] == [(32, 32, 0), (32, 16, 0), (32, 0, 32), (0, 32, 32)]
    assert r[60]["circle"] == [32, 0, 32, 0, 32, 0, 32, 0]


def test_fiche3_the_robot_drives_while_a_button_is_held():
    hold = lambda f, key, n: {f: [("down", key)], f + n: [("up", key)]}      # noqa: E731
    r = run_program("fiche3_moteurs", 420, keys_of(hold(10, K.K_UP, 60), hold(100, K.K_DOWN, 60),
                                                   hold(180, K.K_LEFT, 62), hold(280, K.K_RIGHT, 62)))
    x0 = r[5]["x"]
    assert r[9]["x"] == x0                                                    # nothing moves before a press
    assert r[75]["x"] - x0 == pytest.approx(72, abs=3)                       # 60 frames at speed 30: 1.2 px/frame
    assert r[90]["x"] == r[75]["x"]                                          # released: it stopped
    assert r[165]["x"] - r[90]["x"] == pytest.approx(-72, abs=3)             # backward
    assert r[250]["angle"] == pytest.approx(-90, abs=3)                      # left button: a quarter turn
    assert r[250]["x"] == pytest.approx(r[170]["x"], abs=1)                  # ... on the spot
    assert r[360]["angle"] == pytest.approx(0, abs=4)                        # right button turns back


def test_fiche4_the_robot_stops_before_the_obstacle():
    r = run_program("fiche4_arret_mur", 700, tap(5, K.K_SPACE))
    assert r[300]["x"] > r[5]["x"] + 100                                      # it did drive
    assert r[-1]["x"] == r[-100]["x"]                                         # ... and it is stopped now
    assert r[-1]["top"] == (32, 0, 0)                                         # red
    assert r[-1]["prox"][2] > 1000
    assert 440 - (r[-1]["x"] + 55) > 5                                        # its nose is short of the box (x=440)


def test_fiche4_avoidance_keeps_clear_of_walls_and_boxes():
    r = run_program("fiche4_evitement", 3000, tap(5, K.K_SPACE))
    rects = [(870, 0, 900, 560), (0, 0, 30, 560), (0, 0, 900, 30), (0, 530, 900, 560),
             (440, 220, 520, 300), (640, 290, 720, 370)]
    closest = min(min(math.hypot(max(x0 - f["x"], 0, f["x"] - x1), max(y0 - f["y"], 0, f["y"] - y1))
                      for x0, y0, x1, y1 in rects) for f in r)
    assert closest > 40                                                       # about the robot's half width
    assert max(f["x"] for f in r) - min(f["x"] for f in r) > 400              # and it really wandered about
    assert {f["top"] for f in r} >= {(0, 32, 0), (32, 16, 0)}                 # green while free, orange while turning


def test_fiche5_the_robot_stops_on_the_black_tape():
    r = run_program("fiche5_ruban", 400, tap(5, K.K_SPACE))
    assert min(r[5]["ground"]) > 900                                          # white floor
    assert r[-1]["ground"][0] < 100 and r[-1]["top"] == (32, 0, 0)
    assert r[-1]["x"] == r[-50]["x"]
    assert 405 < r[-1]["x"] < 450                                             # its nose stopped at the tape (x=450)


def test_fiche6_a_variable_counts_button_presses():
    ks = keys_of(tap(5, K.K_UP), tap(15, K.K_UP), tap(25, K.K_UP), tap(40, K.K_DOWN), tap(60, K.K_SPACE))
    r = run_program("fiche6_compteur", 100, ks)
    assert [r[i]["compteur"] for i in (12, 22, 32)] == [1, 2, 3]
    assert [r[i]["top"] for i in (12, 22, 32)] == [(32, 0, 0), (32, 0, 0), (0, 32, 0)]
    assert r[50]["compteur"] == 2 and r[50]["top"] == (32, 0, 0)
    assert r[80]["compteur"] == 0                                             # one press counts once, not on release


def test_fiche7_the_timer_makes_the_led_blink():
    r = run_program("fiche7_clignotant", 300, tap(5, K.K_SPACE))
    on = [f["top"] == (0, 0, 32) for f in r]
    edges = sum(1 for a, b in zip(on, on[1:]) if a != b)
    assert edges >= 8                                                         # on, off, on, off ... every half second
    first_on = on.index(True)
    assert 32 <= first_on <= 38                                               # 500 ms = 30 frames after the press


def test_fiche7_the_timer_drives_a_square():
    r = run_program("fiche7_carre", 1300, tap(5, K.K_SPACE))
    xs, ys = [f["x"] for f in r], [f["y"] for f in r]
    assert max(xs) - min(xs) == pytest.approx(75, abs=15)
    assert max(ys) - min(ys) == pytest.approx(75, abs=15)                     # 75 px sides: a square, not a line
    turned = [f["angle"] for f in r]
    assert min(turned) < -85 and max(turned) > 85                             # it really turned all the way round


def test_fiche9_traffic_light_cycles_green_orange_red():
    r = run_program("fiche9_feu", 420, tap(5, K.K_SPACE))
    seen = []
    for f in r:
        if not seen or f["top"] != seen[-1]:
            seen.append(f["top"])
    assert seen[:7] == [(0, 0, 0), (0, 32, 0), (32, 16, 0), (32, 0, 0), (0, 32, 0), (32, 16, 0), (32, 0, 0)]
    first_green = next(i for i, f in enumerate(r) if f["top"] == (0, 32, 0))
    assert 62 <= first_green <= 68                                            # 1 s = 60 frames after the press


def test_fiche9_alarm_changes_colour_as_the_box_gets_closer():
    r = run_program("fiche9_alarme", 400, {10: [("down", K.K_UP)], 270: [("up", K.K_UP)]})
    seen = []
    for f in r:
        if f["top"] != (0, 0, 0) and (not seen or f["top"] != seen[-1]):
            seen.append(f["top"])
    assert seen == [(0, 32, 0), (32, 16, 0), (32, 0, 0)]                      # green, then orange, then red


def test_fiche9_hourglass_lights_one_more_led_every_second():
    r = run_program("fiche9_sablier", 340, tap(5, K.K_SPACE))
    lit = lambda f: sum(1 for v in f["circle"] if v)                          # noqa: E731
    assert [lit(r[i]) for i in (35, 95, 155, 215, 275, 330)] == [0, 1, 2, 3, 4, 0]


def test_fiche9_traffic_light_can_be_stopped_by_setting_the_period_to_zero():
    r = run_program("fiche9_feu", 400, keys_of(tap(5, K.K_SPACE), tap(200, K.K_DOWN)))
    assert r[190]["top"] != (0, 0, 0)                                         # running
    assert {f["top"] for f in r[210:]} == {(0, 0, 0)}                         # off, and the timer no longer lights it
