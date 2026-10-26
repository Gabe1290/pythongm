#!/usr/bin/env python3
"""Per-frame micro:bit simulation inside a running game (Stage S4).

``update_microbits`` runs through the ``after_collision`` frame-update hook,
like Thymio's: after movement and collision events, before end-step. It steps
every simulator by one frame and fires the events each one reports on the
board's own instance.
"""
from .events import event_name_for
from .state import simulator_of


def update_microbits(game_runner):
    room = getattr(game_runner, "current_room", None)
    if not room:
        return

    # Same early-out as Thymio: most rooms have no micro:bit at all.
    boards = [(inst, simulator_of(inst)) for inst in room.instances
              if simulator_of(inst) is not None]
    if not boards:
        return

    dt = 1.0 / max(1, getattr(game_runner, "fps", 60) or 60)
    for instance, sim in boards:
        reported = sim.update(dt)
        events = (instance.object_data or {}).get("events") \
            if getattr(instance, "object_data", None) else None
        executor = getattr(instance, "action_executor", None)
        if not reported or not events or executor is None:
            continue
        for kind, detail in reported:
            name = event_name_for(kind, detail)
            if name and name in events:
                executor.execute_event(instance, name, events)
