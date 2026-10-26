#!/usr/bin/env python3
"""Where a micro:bit's per-instance state lives (Stage S1).

Everything the extension keeps on a game instance sits under
``instance.extension_state["microbit"]`` -- the engine's ``GameInstance``
carries nothing micro:bit-specific. ``simulator_of`` is the one accessor
the handlers, the frame update, the overlay and the input hook go through.
"""

KEY = "microbit"


def attach_simulator(instance, simulator) -> None:
    """Make ``instance`` a micro:bit by storing its simulator.

    Unlike Thymio's, this doesn't set ``custom_rendered``: the instance's
    own sprite (if any) keeps drawing, and the board overlay (renderer.py)
    draws the LEDs and controls on top of it -- the body too when there is
    no sprite."""
    state = getattr(instance, "extension_state", None)
    if state is None:
        state = instance.extension_state = {}
    state[KEY] = {"simulator": simulator}


def simulator_of(instance):
    """The instance's ``MicrobitSimulator``, or ``None`` for anything else."""
    state = getattr(instance, "extension_state", None)
    if not state:
        return None
    entry = state.get(KEY)
    return entry.get("simulator") if entry else None


def is_microbit(instance) -> bool:
    return simulator_of(instance) is not None


def option_of(instance, name, default=None):
    """An authored per-board option (``microbit_scale``, ``microbit_keyboard``):
    an instance variable wins, else the object's own property."""
    value = getattr(instance, name, None)
    if value is None:
        data = getattr(instance, "object_data", None) or {}
        value = data.get(name, default)
    return default if value is None else value


def scratch(instance) -> dict:
    """The mutable per-board dict (held keys and the like) that sits beside
    the simulator in ``extension_state``."""
    return instance.extension_state[KEY]
