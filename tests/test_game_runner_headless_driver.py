"""Importing the game runner keeps an explicitly headless SDL video driver.

runtime/game_runner.py picks the platform's video driver at import time (x11 / windows / cocoa) so
pygame does not clash with Qt. It used to do that unconditionally, overriding the "dummy" driver
tests/conftest.py asks for: on a desktop every test that ran a game opened a real X11 window, and the
window manager's focus / move / expose events (and the developer's own typing) reached those games at
random moments -- the flaky tests/test_tutorial_reference_projects.py T06 failures. Checked in a fresh
interpreter, because the choice is made once, at import.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _driver_after_import(value):
    env = dict(os.environ)
    if value is None:
        env.pop("SDL_VIDEODRIVER", None)
    else:
        env["SDL_VIDEODRIVER"] = value
    code = "import os, runtime.game_runner; print(os.environ.get('SDL_VIDEODRIVER'))"
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True,
                         text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-2000:]
    return out.stdout.strip().splitlines()[-1]


@pytest.mark.parametrize("headless", ["dummy", "offscreen"])
def test_a_headless_driver_is_kept(headless):
    assert _driver_after_import(headless) == headless


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="the Linux choice")
def test_a_real_run_still_gets_the_platform_driver():
    assert _driver_after_import(None) == "x11"
    assert _driver_after_import("wayland") == "x11"
