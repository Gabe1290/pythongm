"""The thymio_hw_test sample -- six small Thymio programs for the FIRST run on a real robot.

Structure and wiring (Welcome tab, editions, smoke list, translations, bilingual guide), and above
all the exported Aseba: one ``.aesl`` per robot, well-formed, with the lines each program is meant to
test, balanced ``if``/``end``, only real Aseba event names, and -- the safety property -- nothing that
moves the robot at load time. Nobody has yet loaded these onto a real Thymio; what these tests can
check is everything short of that.
"""
import json
import os
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
SAMPLE = REPO_ROOT / "samples" / "thymio_hw_test"
LABEL = "Thymio — Hardware test"
ROBOTS = ["thymio_hw_1_leds", "thymio_hw_2_motors", "thymio_hw_3_counter",
          "thymio_hw_4_proximity", "thymio_hw_5_ground", "thymio_hw_6_timer"]
# the event names a Thymio II program may use (the ones this exporter can emit)
ASEBA_EVENTS = {"button.forward", "button.backward", "button.left", "button.right", "button.center",
                "buttons", "prox", "timer0", "timer1", "tap", "mic", "sound.finished"}

import pytest


@pytest.fixture(autouse=True)
def _thymio_enabled(monkeypatch):
    """The developer's own config may switch the Thymio extension off (this machine's does); the
    sample needs it, so force it on for these tests without touching any config file."""
    from events import plugin_loader
    real = plugin_loader.is_extension_enabled
    monkeypatch.setattr(plugin_loader, "is_extension_enabled",
                        lambda folder, default=True: True if folder == "thymio" else real(folder, default))


def _project():
    return json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def aesl(tmp_path_factory):
    """{robot: aesl source text inside the node} from a real export of the sample."""
    from extensions.thymio.export.aseba_exporter import AsebaExporter
    out = tmp_path_factory.mktemp("aseba")
    assert AsebaExporter().export(str(SAMPLE / "project.json"), str(out)) is True
    result = {}
    for robot in ROBOTS:
        text = (out / f"{robot}.aesl").read_text(encoding="utf-8")
        body = text.split("\n", 1)[1]                                   # drop the DOCTYPE line
        node = ElementTree.fromstring(body).find("node")
        assert node is not None and node.get("name") == "thymio-II", robot
        result[robot] = node.text
    assert sorted(p.stem for p in out.glob("*.aesl")) == sorted(ROBOTS)  # one file per robot, no more
    return result


def _code(text):
    return [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]


# --- structure ---------------------------------------------------------------------------------

def test_the_room_holds_the_six_robots_and_the_label_object():
    project = _project()
    assert project["settings"]["active_extensions"] == ["thymio"]
    room = json.loads((SAMPLE / "rooms" / "room0.json").read_text(encoding="utf-8"))
    names = [i["object_name"] for i in room["instances"]]
    assert sorted(n for n in names if n.startswith("thymio")) == sorted(ROBOTS)
    assert names.count("obj_labels") == 1
    positions = {(i["x"], i["y"]) for i in room["instances"] if i["object_name"].startswith("thymio")}
    assert len(positions) == 6                                         # none on top of another


def test_embedded_objects_match_the_object_files():
    project = _project()
    for name, embedded in project["assets"]["objects"].items():
        on_disk = json.loads((SAMPLE / "objects" / f"{name}.json").read_text(encoding="utf-8"))
        assert on_disk == embedded, name


def test_every_action_is_registered_and_every_event_known():
    """Core actions live in ACTION_TYPES; the Thymio ones in the extension's own registry."""
    from events.action_types import ACTION_TYPES
    from events.event_types import EVENT_TYPES
    from extensions.thymio.actions import THYMIO_ACTIONS
    from extensions.thymio.events import THYMIO_EVENT_TYPES
    actions, events = set(), set()
    for obj in _project()["assets"]["objects"].values():
        for event, data in obj["events"].items():
            events.add(event)
            actions.update(a["action"] for a in data["actions"])
    structural = {"start_block", "end_block"}
    known_actions = set(ACTION_TYPES) | set(THYMIO_ACTIONS) | structural
    assert not actions - known_actions, actions - known_actions
    assert {a for a in actions if a.startswith("thymio_")} <= set(THYMIO_ACTIONS)
    assert not events - set(THYMIO_EVENT_TYPES) - set(EVENT_TYPES) - {"create", "draw"}, events


def test_label_text_is_quoted_so_it_is_not_evaluated():
    for action in _project()["assets"]["objects"]["obj_labels"]["events"]["draw"]["actions"]:
        assert action["parameters"]["text"].startswith('"') and action["parameters"]["text"].endswith('"')


def test_no_robot_moves_when_the_game_starts():
    """Safety: a program must not drive the robot on load. Only button/sensor handlers may."""
    moving = {"thymio_move_forward", "thymio_move_backward", "thymio_turn_left", "thymio_turn_right",
              "thymio_set_motor_speed"}
    for name in ROBOTS:
        create = _project()["assets"]["objects"][name]["events"].get("create", {"actions": []})
        assert not moving & {a["action"] for a in create["actions"]}, name


# --- the exported Aseba -------------------------------------------------------------------------

def test_every_handler_is_a_real_aseba_event(aesl):
    for robot, text in aesl.items():
        events = re.findall(r"^onevent (\S+)", text, re.M)
        assert events, robot
        assert set(events) <= ASEBA_EVENTS, (robot, set(events) - ASEBA_EVENTS)
        assert len(events) == len(set(events)), (robot, "an event is handled twice")


def test_every_if_is_closed(aesl):
    for robot, text in aesl.items():
        lines = _code(text)
        assert sum(1 for l in lines if l.startswith("if ")) == sum(1 for l in lines if l == "end"), robot
        assert not any(l.startswith(("else", "elseif")) for l in lines), robot      # none used here


def test_no_motor_is_driven_before_the_first_handler(aesl):
    """Aseba runs top-level statements when the program starts: nothing may move there."""
    for robot, text in aesl.items():
        top = text.split("onevent", 1)[0]
        assert not re.search(r"motor\.(left|right)\.target", top), robot


def test_every_nonzero_motor_command_is_inside_a_guard(aesl):
    """Every handler that drives the wheels does so under a button or sensor condition."""
    for robot in ("thymio_hw_2_motors", "thymio_hw_4_proximity", "thymio_hw_5_ground"):
        lines, guarded, open_ifs = _code(aesl[robot]), False, 0
        for line in lines:
            if line.startswith("onevent"):
                open_ifs = 0
            elif line.startswith("if "):
                open_ifs += 1
            elif line == "end":
                open_ifs -= 1
            elif re.match(r"motor\.(left|right)\.target = -?[1-9]", line):
                assert open_ifs > 0, (robot, line)
                guarded = True
        assert guarded, robot


def test_leds_program(aesl):
    code = _code(aesl["thymio_hw_1_leds"])
    assert "call leds.top(0, 0, 8)" in code                                    # "loaded and running"
    for line in ("call leds.top(32, 0, 0)", "call leds.top(0, 32, 0)", "call leds.bottom.left(0, 0, 32)",
                 "call leds.bottom.right(0, 0, 32)", "call leds.circle(0, 0, 0, 0, 0, 0, 0, 0)"):
        assert line in code, line
    assert not any(l.startswith("motor.") for l in code)                       # moves nothing


def test_motors_program_drives_while_held_and_stops_on_release(aesl):
    code = _code(aesl["thymio_hw_2_motors"])
    for button, left, right in (("forward", 200, 200), ("backward", -200, -200), ("left", 0, 200), ("right", 200, 0)):
        i = code.index(f"onevent button.{button}")
        block = code[i:i + 14]
        assert f"if button.{button} == 1 then" in block
        assert f"motor.left.target = {left}" in block and f"motor.right.target = {right}" in block
        assert f"if button.{button} == 0 then" in block                        # the release stops it
    i = code.index("onevent button.center")
    assert code[i + 1:i + 3] == ["motor.left.target = 0", "motor.right.target = 0"]


def test_counter_program_declares_and_uses_its_variable(aesl):
    code = _code(aesl["thymio_hw_3_counter"])
    assert "var count" in code and "count = 0" in code
    assert "count++" in code and "if count >= 3 then" in code
    assert code.index("var count") < code.index("count = 0")                   # declared before use


def test_proximity_program(aesl):
    """Armed by the centre button; stops at an obstacle; drives on by itself when the way is clear."""
    code = _code(aesl["thymio_hw_4_proximity"])
    assert code[:2] == ["var armed", "armed = 0"]                              # declared, and disarmed at load
    assert "onevent prox" in code
    assert "if prox.horizontal[2] > 2000 then" in code and "if prox.horizontal[2] <= 2000 then" in code
    i = code.index("onevent button.center")
    assert code[i + 1:i + 3] == ["if button.center == 1 then", "armed = 1"]    # the centre button arms it
    i = code.index("onevent button.backward")
    assert code[i + 1:i + 3] == ["if button.backward == 1 then", "armed = 0"]  # the backward button disarms it
    # resuming is nested: only when the way is clear AND it is armed
    clear = code.index("if prox.horizontal[2] <= 2000 then")
    nested = code.index("if armed == 1 then", clear)
    assert "motor.left.target = 80" in code[nested:nested + 3]
    assert code[nested + 3:nested + 5] == ["end", "end"]                       # both ifs closed


def _proximity_robot(runner):
    from extensions.thymio.state import simulator_of
    robot = next(i for i in runner.current_room.instances if i.object_name == "thymio_hw_4_proximity")
    return robot, simulator_of(robot)


def test_proximity_robot_only_resumes_when_armed_and_clear():
    """The arming logic through the real engine (the simulator's proximity sensors read 'clear')."""
    import pygame
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRunner
    from extensions.thymio import input as inp
    load_all_plugins()
    pygame.init()
    runner = GameRunner(str(SAMPLE / "project.json"))
    seen = {}
    real_clock = pygame.time.Clock

    class FakeClock:
        n = 0

        def tick(self, fps=0):
            FakeClock.n += 1
            if FakeClock.n == 5:
                robot, sim = _proximity_robot(runner)
                events = robot.object_data["events"]

                def fire(name):
                    robot.action_executor.execute_event(robot, name, events)
                sim.set_motor_speed(0, 0)
                fire("thymio_proximity_update")
                seen["disarmed_clear"] = sim.get_motor_speeds()          # clear but never armed: stays still
                inp.key_down(robot, "space")                              # centre: arm and go
                seen["after_centre"] = sim.get_motor_speeds()
                sim.set_motor_speed(0, 0)                                 # an obstacle stopped it ...
                fire("thymio_proximity_update")
                seen["resumed"] = sim.get_motor_speeds()                  # ... and now it is clear: drives on
                inp.key_down(robot, "down")                               # backward: disarm and stop
                seen["after_backward"] = sim.get_motor_speeds()
                fire("thymio_proximity_update")
                seen["clear_but_disarmed"] = sim.get_motor_speeds()
            if FakeClock.n == 8:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return 16

        def get_fps(self):
            return 60.0
    pygame.time.Clock = FakeClock
    try:
        assert runner.run() is not False
    finally:
        pygame.time.Clock = real_clock
    assert seen["disarmed_clear"] == (0, 0)
    assert seen["after_centre"] == (80, 80)
    assert seen["resumed"] == (80, 80)
    assert seen["after_backward"] == (0, 0)
    assert seen["clear_but_disarmed"] == (0, 0)


def test_ground_program(aesl):
    code = _code(aesl["thymio_hw_5_ground"])
    assert "if prox.ground.delta[0] < 300 then" in code and "if prox.ground.delta[0] >= 300 then" in code
    assert "motor.left.target = 80" in code


def test_timer_program(aesl):
    code = _code(aesl["thymio_hw_6_timer"])
    assert code.index("timer.period[0] = 1000") < code.index("onevent timer0")  # armed at load, before the handler
    assert "call sound.freq(440, 15)" in code and "call sound.freq(0, -1)" in code
    assert "timer.period[0] = 0" in code                                       # centre stops the timer


# --- wiring ---------------------------------------------------------------------------------------

def test_welcome_tab_lists_it_and_beginner_does_not():
    from config.editions import EDITIONS
    from widgets.welcome_tab import SAMPLE_PROJECTS
    assert ("samples/thymio_hw_test", LABEL) in SAMPLE_PROJECTS
    assert "thymio_hw_test" not in EDITIONS["beginner"]["sample_folders"]
    assert "thymio_hw_test" not in EDITIONS["junior"]["sample_folders"]


def test_smoke_runner_covers_it():
    assert '"thymio_hw_test"' in (REPO_ROOT / "tools" / "smoke_run_samples.py").read_text(encoding="utf-8")


_TS = {"fr": "pygm2_fr.ts", "es": "pygm2_es.ts", "pt": "pygm2_pt.ts", "ja": "pygm2_ja.ts", "zh": "pygm2_zh.ts",
       "de": "pygm2_de_core.ts", "it": "pygm2_it_core.ts", "ru": "pygm2_ru_core.ts", "sl": "pygm2_sl_core.ts",
       "uk": "pygm2_uk_core.ts"}


@pytest.mark.parametrize("lang", sorted(_TS))
def test_name_is_translated_in_every_shipped_language(lang):
    root = ElementTree.parse(REPO_ROOT / "translations" / _TS[lang]).getroot()
    for context in root.iter("context"):
        if context.findtext("name") != "WelcomeTab":
            continue
        for message in context.iter("message"):
            if message.findtext("source") == LABEL:
                text = message.findtext("translation")
                assert text and text != LABEL and text.startswith("Thymio")
                return
    pytest.fail(f"{LABEL!r} not found in WelcomeTab of {_TS[lang]}")


def test_the_compiled_french_catalog_resolves_the_name_with_its_accents():
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])           # never a bare QCoreApplication
    translator = QTranslator()
    assert translator.load(str(REPO_ROOT / "translations" / "pygm2_fr.qm"))
    QCoreApplication.installTranslator(translator)
    try:
        assert QCoreApplication.translate("WelcomeTab", LABEL) == "Thymio — Test avec le robot"
    finally:
        QCoreApplication.removeTranslator(translator)


def test_both_guides_exist_and_name_every_exported_file():
    for guide in ("README.md", "README.fr.md"):
        text = (SAMPLE / guide).read_text(encoding="utf-8")
        for robot in ROBOTS:
            assert f"{robot}.aesl" in text, (guide, robot)
        assert "asebastudio" in text.lower() or "Aseba Studio" in text


def test_the_french_guide_keeps_its_accents():
    text = (SAMPLE / "README.fr.md").read_text(encoding="utf-8")
    for word in ("Sécurité", "Étape", "déclenche", "Résultats", "Préférences"):
        assert word in text, word
    for bad in ("Securite", "Etape 1", "declenche", "Resultats", "Preferences"):
        assert bad not in text, bad


def test_the_guide_names_the_menu_items_that_exist():
    """The instructions point at real UI: the Preferences checkbox text and the export entry."""
    prefs = (REPO_ROOT / "dialogs" / "preferences_dialog.py").read_text(encoding="utf-8")
    assert "Show this extension's tab, menus and toolbar button" in prefs
    assert "Show this extension's tab, menus and toolbar button" in (SAMPLE / "README.md").read_text(encoding="utf-8")
    export = (REPO_ROOT / "extensions" / "thymio" / "__init__.py").read_text(encoding="utf-8")
    assert "Export &Aseba (Thymio) code..." in export


# --- the simulator side: the six robots come up and the timer fires --------------------------------

def test_the_real_game_loop_runs_and_the_timer_robot_beeps_and_lights_up():
    pytest.importorskip("pygame")
    import pygame
    from conftest import skip_without_pygame  # noqa: F401
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRunner
    from extensions.thymio.state import simulator_of
    load_all_plugins()
    pygame.init()
    runner = GameRunner(str(SAMPLE / "project.json"))
    seen = {}
    real_clock = pygame.time.Clock

    class FakeClock:
        def __init__(self):
            self.frames = 0

        def tick(self, fps=0):
            self.frames += 1
            if self.frames == 5:
                robots = {i.object_name: simulator_of(i) for i in runner.current_room.instances
                          if simulator_of(i) is not None}
                seen["robots"] = sorted(robots)
            if self.frames == 90:                                   # > 1 second of game time
                timer_robot = next(i for i in runner.current_room.instances
                                   if i.object_name == "thymio_hw_6_timer")
                seen["led"] = simulator_of(timer_robot).leds.top
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return 16

        def get_fps(self):
            return 60.0
    pygame.time.Clock = FakeClock
    try:
        assert runner.run() is not False
    finally:
        pygame.time.Clock = real_clock
    assert seen["robots"] == sorted(ROBOTS)
    assert tuple(seen["led"]) == (0, 0, 32)
