#!/usr/bin/env python3
"""Per-frame robot simulation inside a running game (Stage A5).

``update_thymio_robots`` is the body ``GameRunner.update_thymio_robots``
used to have, verbatim, now run through the ``after_collision`` frame-update
hook (runtime/extension_hooks): after movement and collision events, before
end-step/destroy -- exactly where the engine called it.
"""
import pygame


def update_thymio_robots(game_runner):
    """Advance every Thymio robot simulator in the current room and fire the
    sensor/timer/sound events it reports."""
    room = game_runner.current_room
    if not room:
        return

    # Find Thymio instances first. If none, the room is non-Thymio and the
    # obstacle-list scan below would just be wasted work — every frame.
    # (Profiling on a 131-instance maze showed this function consumed ~10%
    # of per-frame work time despite no Thymios being present.)
    thymio_instances = [
        inst for inst in room.instances
        if inst.is_thymio and inst.thymio_simulator
    ]
    if not thymio_instances:
        return

    # Get obstacles for collision detection (all solid instances that aren't Thymio)
    obstacles = []
    for instance in room.instances:
        # Check solid from cached object data
        obj_data = instance._cached_object_data
        is_solid = obj_data.get('solid', False) if obj_data else False
        if is_solid and not instance.is_thymio:
            if instance.sprite:
                rect = pygame.Rect(
                    int(instance.x - instance.sprite.width / 2),
                    int(instance.y - instance.sprite.height / 2),
                    instance.sprite.width,
                    instance.sprite.height
                )
                obstacles.append(rect)

    # Update each Thymio robot
    for instance in thymio_instances:

        # Update simulator (returns dict of events that occurred)
        dt = 1/60  # 60 FPS
        thymio_events = instance.thymio_simulator.update(dt, obstacles, game_runner.screen)

        # Sync instance position with simulator
        instance.x = instance.thymio_simulator.x
        instance.y = instance.thymio_simulator.y

        # Trigger Thymio events if they occurred
        if not instance.object_data or "events" not in instance.object_data:
            continue

        events = instance.object_data["events"]

        if thymio_events.get('proximity_update'):
            if 'thymio_proximity_update' in events:
                instance.action_executor.execute_event(instance, 'thymio_proximity_update', events)

        if thymio_events.get('ground_update'):
            if 'thymio_ground_update' in events:
                instance.action_executor.execute_event(instance, 'thymio_ground_update', events)

        if thymio_events.get('timer_0'):
            if 'thymio_timer_0' in events:
                instance.action_executor.execute_event(instance, 'thymio_timer_0', events)

        if thymio_events.get('timer_1'):
            if 'thymio_timer_1' in events:
                instance.action_executor.execute_event(instance, 'thymio_timer_1', events)

        if thymio_events.get('sound_finished'):
            if 'thymio_sound_finished' in events:
                instance.action_executor.execute_event(instance, 'thymio_sound_finished', events)
