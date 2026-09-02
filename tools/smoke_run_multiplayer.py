#!/usr/bin/env python3
"""Headless two-PROCESS multiplayer smoke test (Phase 8.5).

Unlike tools/smoke_run_samples.py (one in-process GameRunner per sample),
this launches a real host subprocess and a real client subprocess,
talking over a real 127.0.0.1 TCP socket via runtime/run_game.py --
proving the actual CLI/subprocess deployment path works end to end
(two real OS processes, real sockets), which the in-process pytest
coverage (tests/test_reseau_1_sample.py etc.) doesn't exercise.

Scoped to `reseau_1`, the one bundled sample launched purely via the v2
PYGM_NET_AUTOHOST/PYGM_NET_AUTOJOIN env vars (no in-game keyboard trigger
needed -- reseau_2/reseau_3 use host_game/join_game from a "h"/"j"
keypress instead, which a headless subprocess with no display can't be
sent from outside; those are already thoroughly covered by their own
real two-GameRunner-loopback pytest suites). v1's `multiplayer_lan_1`
is out of scope here too: v1 has no identity/globals mirroring at all
(a v2-only addition -- see docs/MULTIPLAYER_LAN_V2_PLAN.md's "what v1
deliberately does NOT do"), so the PYGM_NET_STATUS marker this script
checks for never fires for it; it has its own existing in-process
networked smoke test (tests/test_multiplayer_lan_1_sample.py).

Verification: both processes must exit 0, and both must print
PYGM_NET_STATUS=role=...connected=1 player_id=... (GameRunner.
_print_net_status, runtime/game_runner.py) -- proving the client
actually received a WELCOME from the host (player_id is only assigned
once that real inbound frame arrives), not just "the process didn't
crash".

Usage:
    python tools/smoke_run_multiplayer.py
"""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SAMPLES = ["reseau_1"]

# Not the documented default (45782) -- a distinct port so this smoke
# test never collides with an actual game a developer happens to be
# running locally on the standard port.
TEST_PORT = 45790
MAX_FRAMES = 120
PROC_TIMEOUT = 30.0


def _base_env(max_frames):
    env = dict(os.environ)
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    env["PYGM_MAX_FRAMES"] = str(max_frames)
    # A fresh child process must not inherit a role from whatever
    # launched this script.
    for key in ("PYGM_NET_AUTOHOST", "PYGM_NET_AUTOJOIN", "PYGM_NET_MODE",
                "PYGM_NET_HOST_ADDR", "PYGM_NET_PORT"):
        env.pop(key, None)
    return env


def _net_status(stdout):
    for line in stdout.splitlines():
        if line.startswith("PYGM_NET_STATUS="):
            return line
    return None


def run_pair(name, max_frames=MAX_FRAMES, port=TEST_PORT):
    project_json = str(ROOT / "samples" / name / "project.json")
    run_game = str(ROOT / "runtime" / "run_game.py")

    # The host gets a bigger budget than the client (and starts first, see
    # the sleep below): if the host's process exited -- closing its
    # listening socket -- before the client finished its own run, the
    # client would detect connection_lost right near the end (Phase 8.6's
    # graceful-teardown behavior correctly kicking in) and print
    # connected=0 despite having been genuinely connected the whole time
    # that mattered. Outliving the client avoids that race entirely.
    host_env = _base_env(max_frames * 2)
    host_env["PYGM_NET_AUTOHOST"] = "1"
    host_env["PYGM_NET_PORT"] = str(port)

    host_proc = subprocess.Popen(
        [sys.executable, run_game, project_json, "en"],
        cwd=str(ROOT), env=host_env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    # Give the host a moment to bind its listening socket before the
    # client tries to connect -- run_game.py has no "ready" signal of
    # its own to wait on instead.
    time.sleep(0.5)

    client_env = _base_env(max_frames)
    client_env["PYGM_NET_AUTOJOIN"] = "127.0.0.1"
    client_env["PYGM_NET_PORT"] = str(port)

    client_proc = subprocess.Popen(
        [sys.executable, run_game, project_json, "en"],
        cwd=str(ROOT), env=client_env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )

    try:
        client_out, client_err = client_proc.communicate(timeout=PROC_TIMEOUT)
    except subprocess.TimeoutExpired:
        client_proc.kill()
        client_out, client_err = client_proc.communicate()
    try:
        host_out, host_err = host_proc.communicate(timeout=PROC_TIMEOUT)
    except subprocess.TimeoutExpired:
        host_proc.kill()
        host_out, host_err = host_proc.communicate()

    host_status = _net_status(host_out)
    client_status = _net_status(client_out)

    ok = (
        host_proc.returncode == 0 and client_proc.returncode == 0
        and host_status is not None and "connected=1" in host_status
        and client_status is not None and "connected=1" in client_status
        and "player_id=" in client_status and "player_id=-1" not in client_status
    )

    print(f"  [{'OK' if ok else 'FAIL':4}] {name}")
    print(f"        host   : exit={host_proc.returncode}  {host_status}")
    print(f"        client : exit={client_proc.returncode}  {client_status}")
    if not ok:
        if host_err.strip():
            print("        host stderr (tail):")
            for line in host_err.strip().splitlines()[-8:]:
                print(f"          {line}")
        if client_err.strip():
            print("        client stderr (tail):")
            for line in client_err.strip().splitlines()[-8:]:
                print(f"          {line}")
    return ok


def main():
    print(f"Smoke-running {len(SAMPLES)} multiplayer sample(s) as real "
          f"host+client subprocesses over 127.0.0.1:{TEST_PORT}, "
          f"{MAX_FRAMES} frames each\n")
    results = {}
    for name in SAMPLES:
        try:
            results[name] = run_pair(name)
        except Exception as e:
            import traceback
            print(f"  [ERR ] {name}: {e}")
            traceback.print_exc()
            results[name] = False
    ok = sum(1 for v in results.values() if v)
    print(f"\n{ok}/{len(results)} multiplayer samples connected successfully.")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
