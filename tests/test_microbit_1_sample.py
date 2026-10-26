"""The microbit_1 sample -- "micro:bit — Dice and Moods"
(docs/MICROBIT_EXTENSION_PLAN.md, Stage S11).

Structure, wiring (Welcome tab, editions, smoke list, translations, guides),
and the real project through the real ``GameRunner`` loop: A/B show moods, a
shake rolls a die whose pip count matches the roll, the logo queues a scroll
then the count, and the keyboard opt-in works.
"""
import json
import os
import random
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
SAMPLE = REPO_ROOT / "samples" / "microbit_1"
PROJECT_JSON = str(SAMPLE / "project.json")
LABEL = "micro:bit — Dice and Moods"

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame
pygame.init()


def _project():
    return json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))


# --- structure ---------------------------------------------------------------------------------

def test_project_activates_the_extension_and_the_board_is_named_for_it():
    project = _project()
    assert project["settings"]["active_extensions"] == ["microbit"]
    assert "microbit_1" in project["assets"]["objects"]
    room = json.loads((SAMPLE / "rooms" / "room0.json").read_text(encoding="utf-8"))
    names = [i["object_name"] for i in room["instances"]]
    assert names.count("microbit_1") == 1 and "obj_help" in names
    assert (room["width"], room["height"]) == (640, 480)


def test_embedded_objects_match_the_object_files():
    """The runtime re-merges objects/*.json over the embedded copy, so the two
    must not drift."""
    project = _project()
    for name, embedded in project["assets"]["objects"].items():
        on_disk = json.loads((SAMPLE / "objects" / f"{name}.json").read_text(encoding="utf-8"))
        assert on_disk == embedded, name


def test_every_action_the_sample_uses_is_a_registered_action():
    from events.plugin_loader import load_all_plugins
    from events.action_types import ACTION_TYPES
    load_all_plugins()
    used = set()
    for obj in _project()["assets"]["objects"].values():
        for event in obj["events"].values():
            used.update(a["action"] for a in event["actions"])
    assert used
    assert not used - set(ACTION_TYPES), used - set(ACTION_TYPES)
    assert {"microbit_show_image", "microbit_scroll_text",
            "microbit_show_number"} <= used


def test_the_dice_faces_have_the_right_pips():
    shake = _project()["assets"]["objects"]["microbit_1"]["events"]["microbit_gesture_shake"]
    images = [a["parameters"]["image"] for a in shake["actions"]
              if a["action"] == "microbit_show_image"]
    assert len(images) == 6
    for pips, image in enumerate(images, start=1):
        rows = image.split(":")
        assert len(rows) == 5 and all(re.fullmatch(r"[09]{5}", r) for r in rows)
        assert sum(r.count("9") for r in rows) == pips
        # a die face looks the same turned half a turn (point-symmetric)
        assert [r[::-1] for r in rows[::-1]] == rows


def test_help_text_is_quoted_so_it_is_not_evaluated():
    helper = _project()["assets"]["objects"]["obj_help"]
    for action in helper["events"]["draw"]["actions"]:
        assert action["parameters"]["text"].startswith('"')


# --- wiring ---------------------------------------------------------------------------------------

def test_welcome_tab_lists_the_sample():
    from widgets.welcome_tab import SAMPLE_PROJECTS
    assert ("samples/microbit_1", LABEL) in SAMPLE_PROJECTS


def test_beginner_edition_offers_it_but_not_junior():
    from config.editions import EDITIONS
    assert "microbit_1" in EDITIONS["beginner"]["sample_folders"]
    assert "microbit_1" not in EDITIONS["junior"]["sample_folders"]


def test_smoke_runner_covers_it():
    src = (REPO_ROOT / "tools" / "smoke_run_samples.py").read_text(encoding="utf-8")
    assert '"microbit_1"' in src


_TS = {
    "fr": "pygm2_fr.ts", "es": "pygm2_es.ts", "pt": "pygm2_pt.ts",
    "ja": "pygm2_ja.ts", "zh": "pygm2_zh.ts", "de": "pygm2_de_core.ts",
    "it": "pygm2_it_core.ts", "ru": "pygm2_ru_core.ts", "sl": "pygm2_sl_core.ts",
    "uk": "pygm2_uk_core.ts",
}


@pytest.mark.parametrize("lang", sorted(_TS))
def test_name_is_translated_in_every_shipped_language(lang):
    root = ElementTree.parse(REPO_ROOT / "translations" / _TS[lang]).getroot()
    for context in root.iter("context"):
        if context.findtext("name") != "WelcomeTab":
            continue
        for message in context.iter("message"):
            if message.findtext("source") == LABEL:
                text = message.findtext("translation")
                assert text and text != LABEL and text.startswith("micro:bit")
                assert message.find("translation").get("type") != "unfinished"
                return
    pytest.fail(f"{LABEL!r} not found in WelcomeTab of {_TS[lang]}")


def test_french_name_has_its_accent_and_compiled_catalog_resolves_it():
    from PySide6.QtCore import QCoreApplication, QTranslator
    app = QCoreApplication.instance() or QCoreApplication([])
    translator = QTranslator()
    assert translator.load(str(REPO_ROOT / "translations" / "pygm2_fr.qm"))
    app.installTranslator(translator)
    try:
        assert app.translate("WelcomeTab", LABEL) == "micro:bit — Dé et humeurs"
    finally:
        app.removeTranslator(translator)


def test_both_guides_exist_and_the_french_one_carries_its_accents():
    en = (SAMPLE / "README.md").read_text(encoding="utf-8")
    fr = (SAMPLE / "README.fr.md").read_text(encoding="utf-8")
    for token in ("microbit_1", "obj_help", "microbit_keyboard", "irandom(5) + 1",
                  "00000:00000:00900:00000:00000", "POWER_UP"):
        assert token in en and token in fr, token
    for good in ("événement", "Création", "Paramètres du projet", "Bon à savoir",
                 "À essayer", "carte", "mélodie", "Régler le groupe radio"):
        assert good in fr, good
    for bad in ("evenement", "Creation", "Parametres", "melodie", "Regler", "carte entiere"):
        assert bad not in fr, bad


# --- the real game -----------------------------------------------------------------------------------

def _run(script, frames=80):
    from runtime.game_runner import GameRunner
    runner = GameRunner(PROJECT_JSON)
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.process_pending_messages = lambda *a, **k: None
    state = {"frames": 0}

    class _FakeClock:
        def tick(self, fps=0):
            state["frames"] += 1
            if runner.current_room is not None:
                script(state["frames"], runner)
            if state["frames"] >= frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        assert runner.run() is not False, "game loop reported a fatal crash"
    finally:
        pygame.time.Clock = real
    return runner


def _board(runner):
    inst = next(i for i in runner.current_room.instances if i.object_name == "microbit_1")
    return inst, inst.extension_state["microbit"]["simulator"]


def _lit(sim):
    return sum(1 for row in sim.display for v in row if v)


def _key(key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=key))


def test_starts_with_a_heart():
    seen = {}

    def script(frame, runner):
        if frame == 5:
            seen["row0"] = list(_board(runner)[1].display[0])

    _run(script, frames=8)
    assert seen["row0"] == [0, 9, 0, 9, 0]


def test_a_and_b_show_the_two_moods_via_the_keyboard_opt_in():
    from extensions.microbit.images import IMAGES
    seen = {}

    def script(frame, runner):
        sim = _board(runner)[1]
        if frame == 4:
            _key(pygame.K_a)
        if frame == 9:
            seen["a"] = ["".join(map(str, r)) for r in sim.display]
            _key(pygame.K_b)
        if frame == 14:
            seen["b"] = ["".join(map(str, r)) for r in sim.display]

    _run(script, frames=18)
    assert tuple(seen["a"]) == IMAGES["HAPPY"]
    assert tuple(seen["b"]) == IMAGES["SAD"]


def test_a_shake_rolls_a_die_whose_pips_match_and_counts_the_roll():
    random.seed(20261027)
    seen = {"faces": set(), "ok": True}

    def script(frame, runner):
        inst, sim = _board(runner)
        if frame == 3:
            events = inst.object_data["events"]
            for _ in range(60):                       # 60 rolls, straight through the handler
                inst.action_executor.execute_event(inst, "microbit_gesture_shake", events)
                sim.update(0.0)
                seen["ok"] &= (_lit(sim) == inst.roll)
                seen["faces"].add(inst.roll)
            seen["rolls"] = inst.rolls

    _run(script, frames=6)
    assert seen["ok"]
    assert seen["faces"] == {1, 2, 3, 4, 5, 6}
    assert seen["rolls"] == 60


def test_a_real_shake_through_the_loop_rolls_once():
    seen = {}

    def script(frame, runner):
        inst, sim = _board(runner)
        if frame == 4:
            sim.shake()
        if frame == 12:
            seen["rolls"] = inst.rolls
            seen["pips"] = _lit(sim)
            seen["roll"] = inst.roll

    _run(script, frames=16)
    assert seen["rolls"] == 1
    assert seen["pips"] == seen["roll"] and 1 <= seen["roll"] <= 6


def test_logo_scrolls_the_word_then_the_count_and_the_queue_drains():
    from extensions.microbit.simulator import glyph_image
    seen = {}

    def script(frame, runner):
        inst, sim = _board(runner)
        if frame == 3:
            inst.rolls = 4
            sim.set_logo_touched(True)
        if frame == 5:
            seen["queued"] = len(sim._queue)             # the word, then the number
        if frame == 420:                                 # "Rolls" scrolls for ~5 s
            seen["busy"] = sim.busy
            seen["display"] = sim.display

    _run(script, frames=424)
    assert seen["queued"] == 2
    assert seen["busy"] is False
    assert seen["display"] == glyph_image("4")           # ends holding the count


def test_the_board_and_the_instructions_render_in_the_window():
    from extensions.microbit import layout as L
    seen = {}

    def script(frame, runner):
        if frame == 6:
            lay = L.board_layout(320, 160)
            seen["body"] = tuple(runner.screen.get_at((lay.body[0] + 6, lay.body[1] + 90)))[:3]
            seen["heart_led"] = tuple(runner.screen.get_at(lay.led_center(1, 0)))[:3]
            seen["help_px"] = any(tuple(runner.screen.get_at((x, 411)))[:3] == (255, 255, 255)
                                  for x in range(40, 300))

    _run(script, frames=8)
    assert seen["body"] != (26, 42, 68)                  # not the room background
    assert seen["heart_led"] == L.ON_COLOR
    assert seen["help_px"]
