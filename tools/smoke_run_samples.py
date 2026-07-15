#!/usr/bin/env python3
"""Headless smoke-runner for the bundled samples (cross-platform).

Drives each sample's REAL game loop (create/step/alarm/collision/input/room
logic) for a bounded number of frames under SDL's dummy drivers, injecting
keyboard input, and reports the outcome. No window required, so it runs
identically on Linux, Windows and macOS / CI.

Usage:
    python tools/smoke_run_samples.py            # all samples, 180 frames
    python tools/smoke_run_samples.py 300        # custom frame cap

Classification per sample:
    OK         - ran the full frame cap without the loop dying
    GAME-END   - loop exited cleanly before the cap (authored game_end)
    LOOP-CRASH - run_game_loop caught a FATAL exception (run() returned False)
Caught per-action errors (logged, loop continues) are usually authored
sample-script issues, not engine regressions, and are listed for eyeballing.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import logging
import sys
from pathlib import Path

# Make the repo root importable and locate samples/ regardless of CWD.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import pygame
from runtime.game_runner import GameRunner

SAMPLES = ["maze_1", "maze_2", "maze_3",
           "plateforme_1", "plateforme_2", "plateforme_3",
           "match3_1", "match3_2", "match3_3",
           "views_1"]


class _Collector(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.ERROR)
        self.records = []

    def emit(self, record):
        try:
            self.records.append(record.getMessage())
        except Exception:
            pass


def run_sample(name, max_frames):
    project_json = str(ROOT / "samples" / name / "project.json")
    runner = GameRunner(project_json)
    runner.language = "en"

    state = {"frames": 0, "cap_fired": False}

    # Modal dialogs run their own blocking event loop — no-op them headlessly.
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None

    # pygame.time.Clock is an immutable C type, but the module attribute can be
    # swapped; game_runner instantiates it via pygame.time.Clock().
    class _FakeClock:
        def tick(self, fps=0):
            f = state["frames"] = state["frames"] + 1
            if f == 3:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
            if f == 50:
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_RIGHT))
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
            if f == 90:
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_LEFT))
            if f % 20 == 0:
                for k in (pygame.K_UP, pygame.K_SPACE):
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=k))
                    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=k))
            if f >= max_frames:
                state["cap_fired"] = True
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    collector = _Collector()
    logging.getLogger().addHandler(collector)
    real_clock = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        result = runner.run()
    except Exception as e:
        result = e
    finally:
        pygame.time.Clock = real_clock
        logging.getLogger().removeHandler(collector)

    if isinstance(result, Exception):
        status = "HARNESS-EXC"
    elif result is False:
        status = "LOOP-CRASH"
    elif state["cap_fired"]:
        status = "OK"
    else:
        status = "GAME-END"

    room = getattr(getattr(runner, "current_room", None), "name", "?")
    insts = len(runner.current_room.instances) if runner.current_room else 0
    print(f"  [{status:11}] {name:13} frames={state['frames']:3}  room={room}  "
          f"inst={insts}  score={getattr(runner, 'score', '?')} "
          f"lives={getattr(runner, 'lives', '?')}")

    seen = []
    for m in collector.records:
        first = m.splitlines()[0][:110] if m else ""
        if first and first not in seen:
            seen.append(first)
    for s in seen[:6]:
        print(f"        · {s}")
    if isinstance(result, Exception):
        import traceback
        traceback.print_exception(type(result), result, result.__traceback__)

    return status in ("OK", "GAME-END")


def main():
    max_frames = int(sys.argv[1]) if len(sys.argv) > 1 else 180
    print(f"Smoke-running {len(SAMPLES)} samples, {max_frames} frames each "
          f"(SDL dummy, injected input)\n")
    results = {}
    for name in SAMPLES:
        try:
            results[name] = run_sample(name, max_frames)
        except Exception as e:
            import traceback
            print(f"  [HARNESS-ERR] {name}: {e}")
            traceback.print_exc()
            results[name] = False
    ok = sum(1 for v in results.values() if v)
    print(f"\n{ok}/{len(results)} samples ran with no fatal loop crash.")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
