#!/usr/bin/env python3
"""Where a robot's per-instance state lives (Stage B3).

Everything Thymio keeps on a game instance sits under
``instance.extension_state["thymio"]`` -- the engine's ``GameInstance``
carries nothing robot-specific. ``simulator_of`` is the one accessor the
handlers, the frame update, the overlay and the input hook all go through.
"""

KEY = "thymio"


def attach_simulator(instance, simulator) -> None:
    """Make ``instance`` a robot: store its simulator and have the engine
    leave its drawing to this extension's overlay."""
    state = getattr(instance, "extension_state", None)
    if state is None:
        state = instance.extension_state = {}
    state[KEY] = {"simulator": simulator}
    instance.custom_rendered = True


def simulator_of(instance):
    """The instance's ``ThymioSimulator``, or ``None`` for a non-robot."""
    state = getattr(instance, "extension_state", None)
    if not state:
        return None
    entry = state.get(KEY)
    return entry.get("simulator") if entry else None


def is_robot(instance) -> bool:
    return simulator_of(instance) is not None
