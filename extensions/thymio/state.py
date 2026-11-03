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


# --- the floor the ground sensors look at ------------------------------------------------------------------
# A robot's ground sensors sit under its body, and the body is drawn on the very screen they sample, so sampling
# the screen read the robot's own off-white shell and never the floor (a black line or a table edge was invisible).
# The overlay keeps a copy of each frame taken BEFORE the first robot of that frame is drawn; the frame update
# samples that. One entry only: it remembers which screen it copied, so another game's stale copy is never used.
_FLOOR = {"screen": None, "surface": None, "seen": set()}


def remember_floor(instance, screen) -> None:
    """Overlay hook, called before ``instance``'s body is drawn: on the first robot of a frame, keep a copy of the
    screen as it is now (every robot is drawn after the room, so the copy has none of them)."""
    seen = _FLOOR["seen"]
    if not seen or id(instance) in seen or _FLOOR["screen"] is not screen:
        seen.clear()
        _FLOOR["screen"] = screen
        _FLOOR["surface"] = screen.copy()
    seen.add(id(instance))


def floor_frame(screen):
    """The robot-free copy of ``screen`` from the last drawn frame, or ``screen`` itself before the first one."""
    if _FLOOR["screen"] is screen and _FLOOR["surface"] is not None:
        return _FLOOR["surface"]
    return screen
