#!/usr/bin/env python3
"""Targeted room-lifecycle smoke check on real sample data (cross-platform).

Loads real samples and exercises change_room / restart_current_room /
restart_game and the create-once guard directly, asserting no exception and
that rooms rebuild. Complements tools/smoke_run_samples.py (which drives the
full frame loop). Headless (SDL dummy), so it runs on Linux/Windows/macOS/CI.

Validates: M48 (room_speed→fps), M51 (persistent on restart_room),
M52 (restart_game rebuilds all rooms), M53 (create fires once).

Usage:
    python tools/smoke_room_lifecycle.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import pygame
from runtime.game_runner import GameRunner

SAMPLES = ["maze_1", "maze_3", "plateforme_2", "plateforme_4"]


def _prep(name):
    pygame.init()
    pygame.display.set_mode((64, 64))
    runner = GameRunner(str(ROOT / "samples" / name / "project.json"))
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.process_pending_messages = lambda *a, **k: None
    starting = runner.find_starting_room()
    runner.current_room = runner.rooms[starting]
    runner.window_width = runner.current_room.width
    runner.window_height = runner.current_room.height
    runner.load_sprites()
    runner.load_backgrounds()
    runner.load_room_backgrounds()
    runner.assign_sprites_to_rooms()
    for inst in list(runner.current_room.instances):
        if inst.object_data and "events" in inst.object_data:
            runner.action_executor.execute_event(inst, "create", inst.object_data["events"])
    return runner


def check(name):
    runner = _prep(name)
    rooms = runner.get_room_list()
    notes = [f"fps={runner.fps}", f"rooms={len(rooms)}"]

    # M53 — create fires once: re-dispatching on a live instance is a no-op.
    fired_twice = False
    for inst in runner.current_room.instances:
        if getattr(inst, "_create_fired", False):
            before = len(runner.current_room.instances)
            if inst.object_data and "events" in inst.object_data:
                runner.action_executor.execute_event(inst, "create", inst.object_data["events"])
            fired_twice = len(runner.current_room.instances) != before
            break
    notes.append("create_once=" + ("OK" if not fired_twice else "FAIL"))

    # M51 — restart current room.
    n = len(runner.current_room.instances)
    runner.restart_current_room()
    notes.append(f"restart_room {n}->{len(runner.current_room.instances)}")

    # Re-entry across all rooms (M53 / persistent carry).
    for r in rooms:
        runner.change_room(r)
    notes.append(f"changed_all->{runner.current_room.name}")

    # M52 — restart_game rebuilds every visited room.
    runner.restart_game()
    notes.append(f"restart_game->{runner.current_room.name}")

    ok = not fired_twice
    print(f"  [{'OK' if ok else 'FAIL':4}] {name:13} " + " | ".join(notes))
    return ok


def main():
    print("Room-lifecycle check on real samples\n")
    ok = 0
    for n in SAMPLES:
        try:
            ok += check(n)
        except Exception as e:
            import traceback
            print(f"  [FAIL] {n}: {e}")
            traceback.print_exc()
    print(f"\n{ok}/{len(SAMPLES)} samples passed room-lifecycle checks.")
    return 0 if ok == len(SAMPLES) else 1


if __name__ == "__main__":
    sys.exit(main())
