"""The runtime/action_handlers/ package is retired; nothing regressed with it.

That package was a second, parallel handler source predating the
`execute_*_action` convention, and `ActionExecutor._register_action_handlers`
had a whole "Phase 2" to merge it in. It was torn down on 2026-09-06
(docs/POST_1_0_REFACTOR.md's companion cleanup) once the question it was
blocked on got an answer: legacy action names are not worth carrying, there
being too few legacy projects to justify it.

Three things are worth pinning, because each would fail quietly rather than
loudly:

1. the package really is gone (an import of it would silently start working
   again if someone recreated it, and the parallel-systems debt would be back);
2. the four live actions it used to own are still dispatchable, having been
   folded into the mixins;
3. `play_sound` -- the one non-legacy handler it carried -- keeps its
   PLUGIN-owned implementation. Folding the fallback onto the executor risked
   inverting that: if the base's copy won, every game would get a stub instead
   of real audio, and nothing would raise.
"""
import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_the_package_is_gone():
    assert not (REPO_ROOT / "runtime" / "action_handlers").exists()
    try:
        importlib.import_module("runtime.action_handlers")
    except ImportError:
        return
    raise AssertionError(
        "runtime/action_handlers is importable again -- the parallel handler "
        "source is back; see docs/POST_1_0_REFACTOR.md's companion cleanup")


def test_no_phase_two_registration_remains():
    source = (REPO_ROOT / "runtime" / "action_executor.py").read_text(
        encoding="utf-8")
    assert "from runtime.action_handlers import" not in source


def test_the_folded_actions_are_still_dispatchable():
    """move_free / set_speed / set_direction / comment were the package's last
    reachable entries; they are mixin methods now."""
    from runtime.action_executor import ActionExecutor

    executor = ActionExecutor()
    for action in ("move_free", "set_speed", "set_direction", "comment"):
        assert action in executor.action_handlers, action


def test_set_speed_and_set_direction_still_preserve_the_other_component():
    """The behaviour the two folded movement actions exist for: each changes
    one half of the velocity vector and rebuilds from the other."""
    from runtime.action_executor import ActionExecutor

    class _Inst:
        object_name = "obj_test"
        hspeed = 0.0
        vspeed = 0.0

    executor = ActionExecutor()
    inst = _Inst()

    # Moving right at 4, then re-aimed straight up, must keep magnitude 4.
    executor.execute_set_speed_action(inst, {"speed": "4"})
    assert round(inst.hspeed, 6) == 4.0 and round(inst.vspeed, 6) == 0.0

    executor.execute_set_direction_action(inst, {"direction": "90"})
    assert round(inst.hspeed, 6) == 0.0
    assert round(inst.vspeed, 6) == -4.0, "90 degrees is up; screen y grows down"


def test_play_sound_stays_plugin_owned():
    """The base keeps only a fallback. Once plugins load, the plugin's
    implementation must REPLACE it -- otherwise every game silently gets the
    stub instead of real audio."""
    from events.plugin_loader import load_all_plugins
    from runtime.action_executor import ActionExecutor

    executor = ActionExecutor()
    fallback = executor.action_handlers["play_sound"]
    assert "MiscMixin" in getattr(fallback, "__qualname__", ""), fallback

    load_all_plugins(executor)
    live = executor.action_handlers["play_sound"]
    assert live is not fallback, (
        "the plugin did not override the fallback; games would get the stub")


def test_play_sound_fallback_queues_a_sound_when_plugins_are_absent():
    """Why the fallback is kept at all: without it a sample calling play_sound
    hits an unregistered action. test_export_feature_matrix's "runtime covers
    every sample action" check caught exactly that when it was deleted."""
    from runtime.action_executor import ActionExecutor

    class _Inst:
        object_name = "obj_test"

    inst = _Inst()
    ActionExecutor().execute_play_sound_action(inst, {"sound": "beep"})
    assert inst.pending_sounds == [
        {"sound": "beep", "loop": False, "action": "play"}]
