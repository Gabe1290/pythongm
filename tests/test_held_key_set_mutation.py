"""Regression test for H1 (docs/FULL_AUDIT_2026-09-07.md): mutating
instance.keys_pressed while _process_held_keys iterates it used to raise
RuntimeError("Set changed size during iteration") and kill the game.

The real-world trigger: a keyboard (held) event's action list shows a
modal dialog (show_message, a splash, the high-score/name-entry screens);
every one of those dialogs' KEYUP handling calls
GameRunner._release_held_key_silent, which discards from the very
instance.keys_pressed set _process_held_keys is looping over. This test
drives that exact shape directly against InputMixin._process_held_keys,
with a fake action_executor that simulates a dialog's side effect
(discarding a key mid-iteration) instead of actually opening pygame UI.
"""

import pytest

pygame = pytest.importorskip("pygame")

from runtime.input_handler import InputMixin


class _FakeActionExecutor:
    """Simulates a modal-dialog action: discards a key from the instance's
    keys_pressed set (as _release_held_key_silent would) while the held-key
    loop is still iterating it."""

    def __init__(self, instance, key_to_release_on_fire):
        self.instance = instance
        self.key_to_release_on_fire = key_to_release_on_fire
        self.calls = []

    def execute_action_list(self, instance, actions):
        self.calls.append(list(actions))
        if self.key_to_release_on_fire in instance.keys_pressed:
            instance.keys_pressed.discard(self.key_to_release_on_fire)


class _Inst:
    def __init__(self, keys, events, executor_factory):
        self.keys_pressed = set(keys)
        self.object_data = {"events": events}
        self.intended_x = self.x = 0
        self.intended_y = self.y = 0
        self.action_executor = executor_factory(self)


class _Runner(InputMixin):
    pass


def _keyboard_events(sub_keys):
    """Build an object_data['events']['keyboard'] dict with one action per
    sub_key, keyed the way the runtime actually looks them up
    (press_<key> preferred, falls back to bare <key>)."""
    return {
        "keyboard": {
            key: {"actions": [{"action": "noop", "parameters": {}}]}
            for key in sub_keys
        }
    }


def test_process_held_keys_survives_mid_iteration_release():
    """Two keys held; firing the first one's action releases the second
    key from the set (simulating a dialog's KEYUP side effect). Must not
    raise RuntimeError, and must not fire the released key's action."""
    events = _keyboard_events(["left", "right"])

    inst = _Inst(
        keys={"left", "right"},
        events=events,
        executor_factory=lambda i: _FakeActionExecutor(i, key_to_release_on_fire="right"),
    )

    runner = _Runner()
    # Must not raise -- this is the crash the audit finding describes.
    runner._process_held_keys(inst)

    # "right" must never remain in keys_pressed after having been
    # released mid-iteration by the other key's action.
    assert "right" not in inst.keys_pressed


def test_process_held_keys_releasing_self_mid_loop_does_not_crash():
    """A key's own action releases *itself* mid-iteration (e.g. the
    player lets go while the dialog from their own key's action is up).
    The loop must finish without raising."""
    events = _keyboard_events(["space"])

    inst = _Inst(
        keys={"space"},
        events=events,
        executor_factory=lambda i: _FakeActionExecutor(i, key_to_release_on_fire="space"),
    )

    runner = _Runner()
    runner._process_held_keys(inst)  # must not raise

    assert "space" not in inst.keys_pressed
    assert len(inst.action_executor.calls) == 1


def test_process_held_keys_many_keys_no_mutation_all_fire():
    """Baseline: with no mid-loop mutation, every held key's action fires
    exactly once (behaviour-preservation check for the snapshot change)."""
    events = _keyboard_events(["up", "down", "left", "right"])
    inst = _Inst(
        keys={"up", "down", "left", "right"},
        events=events,
        executor_factory=lambda i: _FakeActionExecutor(i, key_to_release_on_fire="__never__"),
    )

    runner = _Runner()
    runner._process_held_keys(inst)

    assert len(inst.action_executor.calls) == 4
    assert inst.keys_pressed == {"up", "down", "left", "right"}
