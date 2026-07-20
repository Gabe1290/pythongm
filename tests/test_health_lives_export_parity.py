"""Health/lives CONDITIONALS and the no_more_health event across targets.

Found while authoring raycast_3, whose core mechanic is health-as-a-resource
(monsters damage you; the health bar is the reason the sample exists). The
display half worked everywhere — set_health and draw_health_bar both export —
but the logic half did not:

    action / event      desktop   HTML5   Kivy   (before 2026-07-20)
    set_health             y        y       y
    draw_health_bar        y        y       y
    test_health            y        y       .
    test_lives             y        y       .
    no_more_health         y        .       .
    no_more_lives          y        y       y

So health and lives were usable as DISPLAY only on the export targets: the bar
moved, but every conditional branching on it silently vanished and a "you died"
handler never fired. Exactly the failure mode docs/RAYCAST_HUD_PLAN.md's risk
assessment missed, and the class of gap CLAUDE.md's "audits miss absent
features" note warns about — a static read of the sample sees the actions
present and concludes it works.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
KIVY_EXPORTER = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
KIVY_CODEGEN = (REPO_ROOT / "export" / "Kivy" / "code_generator.py").read_text(encoding="utf-8")


def test_kivy_generates_test_health_and_test_lives():
    """Both mirror the existing test_score branch."""
    assert "'test_health', 'test_lives'" in KIVY_CODEGEN
    assert "_tsga().{attr}" in KIVY_CODEGEN or "_tsga().health" in KIVY_CODEGEN


def test_kivy_test_health_emits_a_real_guard():
    """Exercise the generator rather than trusting the source text."""
    from export.Kivy.code_generator import ActionCodeGenerator
    for action, attr in (("test_health", "health"), ("test_lives", "lives")):
        gen = ActionCodeGenerator(base_indent=0)
        gen.process_action(
            {"action": action, "parameters": {"operation": "less", "value": "1"}},
            "step")
        gen.process_action({"action": "restart_room", "parameters": {}}, "step")
        code = gen.get_code()
        assert f".{attr}" in code, f"{action} produced no {attr} reference:\n{code}"
        assert f"if (_tsga().{attr}" in code, f"{action} produced no guard:\n{code}"
        assert "< 1:" in code, f"{action} produced no comparison:\n{code}"
        # The guarded action must actually land INSIDE the guard.
        guarded = code.split("< 1:", 1)[1]
        assert guarded.strip().startswith(" ") or guarded.lstrip("\n").startswith("    "), \
            f"{action}'s body is not indented under the guard:\n{code}"


def test_kivy_unknown_operation_is_a_dead_guard_not_a_crash():
    """Matches test_score's handling of raw GM numeric operation codes."""
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=0)
    gen.process_action(
        {"action": "test_health", "parameters": {"operation": "7", "value": "1"}},
        "step")
    assert "if False" in gen.get_code()


def test_no_more_health_fires_on_both_export_targets():
    # Kivy: dispatched from set_health, and mapped to a generated method.
    assert "on_no_more_health" in KIVY_EXPORTER
    assert "'no_more_health': 'on_no_more_health'" in KIVY_EXPORTER
    # HTML5: dispatched from the set_health action.
    assert "inst.events.no_more_health" in ENGINE


def test_no_more_health_fires_only_on_the_downward_crossing():
    """Same guard as no_more_lives: >0 -> <=0, once. Without the old-value
    check, every further set_health at 0 would re-fire the handler — a death
    loop rather than a single death."""
    kivy = KIVY_EXPORTER[KIVY_EXPORTER.index("def set_health("):]
    kivy = kivy[:kivy.index("def set_window_caption(")]
    assert "_old_health > 0" in kivy and "<= 0" in kivy

    js = ENGINE[ENGINE.index("case 'set_health':"):]
    js = js[:js.index("case 'jump_to_start':")]
    assert "oldHealth > 0" in js and "game.health <= 0" in js


def test_no_more_health_fires_on_every_instance_that_defines_it():
    """Not just the instance whose action changed health — matches the
    desktop runtime and the existing no_more_lives behaviour."""
    kivy = KIVY_EXPORTER[KIVY_EXPORTER.index("def set_health("):]
    kivy = kivy[:kivy.index("def set_window_caption(")]
    assert "for _inst in list(_game_app.scene.instances)" in kivy

    js = ENGINE[ENGINE.index("case 'set_health':"):]
    js = js[:js.index("case 'jump_to_start':")]
    assert "game.currentRoom.instances" in js


# --- Kivy letter/number keys (2026-07-20) ----------------------------------
# The Kivy code generator's key_map held ONLY the four arrows, in three
# duplicated copies, so a keyboard event on any other key generated
# `if key == 0:` and silently never fired on Android. Desktop and engine.js
# both handle letter keys, so this was a real three-target divergence.
# Found while adding raycast_3's 'm' map toggle; it also revives maze_3's
# R / N / P debug keys on Android.

def test_kivy_key_map_is_single_sourced():
    assert "_KIVY_KEY_MAP = {" in KIVY_EXPORTER
    # Three former inline copies now reference the one table.
    assert KIVY_EXPORTER.count("key_map = _KIVY_KEY_MAP") == 3
    assert "'right': '275',\n    'left': '276'," in KIVY_EXPORTER


def test_kivy_key_map_covers_letters_and_digits():
    from export.Kivy.kivy_exporter import _KIVY_KEY_MAP
    assert _KIVY_KEY_MAP['m'] == '109'
    assert _KIVY_KEY_MAP['r'] == '114'
    assert _KIVY_KEY_MAP['a'] == '97' and _KIVY_KEY_MAP['z'] == '122'
    assert _KIVY_KEY_MAP['0'] == '48' and _KIVY_KEY_MAP['9'] == '57'
    assert _KIVY_KEY_MAP['space'] == '32'
    # Arrows unchanged.
    assert (_KIVY_KEY_MAP['up'], _KIVY_KEY_MAP['down'],
            _KIVY_KEY_MAP['left'], _KIVY_KEY_MAP['right']) == \
        ('273', '274', '276', '275')


def test_kivy_key_lookup_is_case_insensitive():
    """maze_3 writes its debug keys as 'N' and 'P' (uppercase) while others
    are lowercase; a case-sensitive lookup left those dead on Android."""
    assert KIVY_EXPORTER.count("key_map.get(str(key_name).lower(), '0')") == 3


def test_map_button_is_opt_in():
    """The extra D-pad button appears only when the game actually binds 'm',
    so ordinary keyboard games don't grow a mystery control."""
    assert "NEEDS_MAP_BUTTON = {needs_map_button}" in KIVY_EXPORTER
    assert "needs_map_button=self._project_binds_key('m')" in KIVY_EXPORTER
    assert "def _project_binds_key(" in KIVY_EXPORTER
    assert "if NEEDS_MAP_BUTTON:" in KIVY_EXPORTER
    assert "KEY_MAP_TOGGLE = 109" in KIVY_EXPORTER
