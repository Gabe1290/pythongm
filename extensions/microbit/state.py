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
