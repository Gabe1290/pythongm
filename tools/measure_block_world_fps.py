#!/usr/bin/env python3
"""Measure the block_world samples' real frame rate, headlessly.

Exists because the Block World renderer is the one bundled feature that misses
its own target frame rate, and every claim about it needs a number rather than
an impression. `tools/smoke_run_samples.py` proves a sample *runs*; this says
how fast.

Method, stated because it decides what the number means:

  * the real `GameRunner.run()` loop under SDL's dummy drivers -- same harness
    shape as smoke_run_samples.py, so it needs no window and runs anywhere;
  * `pygame.time.Clock` is swapped for a fake whose `tick()` never sleeps, so
    the loop runs as fast as the engine can produce frames. The result is the
    engine's CEILING, not the room's configured 30fps;
  * the first WARMUP frames are discarded -- first-frame surface and texture
    caching is not representative of steady state;
  * conditions are INTERLEAVED across repeats, not run in blocks, and the full
    min/median/max spread is printed. This is not fussiness: while writing
    this, block_world_1's *identical* static condition measured ~14fps and
    ~24fps minutes apart purely from background load on a desktop. Interleaving
    spreads that drift across every condition instead of biasing whichever ran
    first, and printing the spread lets a reader see the noise instead of
    trusting one number.

Two camera conditions, because the renderer's cost depends entirely on what is
in view and one number hides that:

  * static  -- no input; the camera stands where the sample spawns it;
  * walking -- W held, so the camera actually walks.
    Deliberately NOT the arrow keys: in these samples Up/Down are bound to
    `set_look_pitch` (+2 deg per frame, relative), so holding Up simply tilts
    the camera at the empty sky, where almost nothing renders. That measured as
    a 3x "speedup" on the first attempt here -- it was a blank screen, not a
    faster renderer.

`PYGM_ROOT` selects which tree to measure, so the same harness can be pointed
at a `git worktree` of an older commit. On a machine this noisy, an A/B between
two trees measured minutes apart is the only sound way to ask whether a change
actually moved the number.

Usage:
    py -3.12 tools/measure_block_world_fps.py                # 60 frames, 3 runs
    py -3.12 tools/measure_block_world_fps.py 90 5
    PYGM_ROOT=/path/to/worktree py -3.12 tools/measure_block_world_fps.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import statistics
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("PYGM_ROOT")
            or Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(ROOT))

import pygame  # noqa: E402
from runtime.game_runner import GameRunner  # noqa: E402

SAMPLES = ["block_world_1", "block_world_2"]
WARMUP = 15
TARGET_FPS = 30


def run_once(sample, frames, walking):
    """One timed run. Returns None if the loop died before producing frames."""
    runner = GameRunner(str(ROOT / "samples" / sample / "project.json"))
    runner.language = "en"
    # Modal dialogs run their own blocking event loop -- no-op them headlessly,
    # exactly as smoke_run_samples.py does.
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None

    state = {"n": 0, "t0": None, "stamps": []}

    class _FakeClock:
        def tick(self, fps=0):
            n = state["n"] = state["n"] + 1
            now = time.perf_counter()
            if n == WARMUP:
                state["t0"] = now
                if walking:
                    pygame.event.post(pygame.event.Event(
                        pygame.KEYDOWN, key=pygame.K_w))
            elif n > WARMUP:
                state["stamps"].append(now)
            if n >= frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        ok = runner.run()
    finally:
        pygame.time.Clock = real_clock

    stamps = state["stamps"]
    if not ok or len(stamps) < 5:
        return None
    per_frame = [b - a for a, b in zip([state["t0"]] + stamps, stamps)]
    return {"fps": len(stamps) / (stamps[-1] - state["t0"]),
            "ms_worst": 1000 * max(per_frame)}


def main():
    frames = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    print("tree    %s" % ROOT)
    print("frames  %d (first %d discarded), %d interleaved runs per condition"
          % (frames, WARMUP, repeats))
    print("target  %dfps (the samples' configured room speed)\n" % TARGET_FPS)

    runs = {(s, w): [] for s in SAMPLES for w in (False, True)}
    for _ in range(repeats):
        for sample in SAMPLES:
            for walking in (False, True):
                result = run_once(sample, frames, walking)
                if result:
                    runs[(sample, walking)].append(result)

    worst = TARGET_FPS
    for (sample, walking), results in runs.items():
        label = "walking" if walking else "static"
        if not results:
            print("%-16s %-8s FAILED TO RUN" % (sample, label))
            worst = 0
            continue
        fps = sorted(r["fps"] for r in results)
        median = statistics.median(fps)
        worst = min(worst, median)
        print("%-16s %-8s median %5.2f fps  (min %5.2f, max %5.2f)  "
              "worst frame %4.0f ms  %s"
              % (sample, label, median, fps[0], fps[-1],
                 max(r["ms_worst"] for r in results),
                 "OK" if median >= TARGET_FPS
                 else "%.1fx under target" % (TARGET_FPS / median)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
