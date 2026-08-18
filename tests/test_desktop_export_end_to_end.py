"""The export must be LAUNCHED, not just built.

This is the test whose absence let five bugs through (EYEBALL_FIXES_2026-08-16
issues 4-8: no tiles, a keyboard that jammed at the first wall, no wall
collision, a player drifting upward, sub-images stuck on frame 0). Every one
was in a built .exe, and the suite was green, because nothing ever ran the
artifact the exporter produced.

Three layers, cheapest first:

1. the frame budget and screenshot hook the verification depends on --
   milliseconds, always run;
2. the real pygame engine reaching a real frame count in a SEPARATE process,
   which is how a compiled binary has to be measured -- seconds, always run;
3. a real PyInstaller build, launched, asserted to render -- minutes, so it is
   opt-in via PYGM_E2E_EXPORT=1 and lives in tools/verify_desktop_export.py.

Layer 3 was run by hand on Windows (2026-08-17): maze_1 built, launched,
rendered 100 frames, exited 0, and its frame differed from the IDE's by 0.00%
of pixels.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

RUN_GAME = REPO_ROOT / "runtime" / "run_game.py"
MARKER = "PYGM_FRAMES_COMPLETED="

E2E_ENABLED = os.environ.get("PYGM_E2E_EXPORT") == "1"


def _engine_env(**extra):
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    env.pop("PYGM_MAX_FRAMES", None)
    env.pop("PYGM_SCREENSHOT", None)
    env.update({k: str(v) for k, v in extra.items()})
    return env


def _run_sample(sample, frames, screenshot=None, language="en", timeout=180):
    extra = {"PYGM_MAX_FRAMES": frames}
    if screenshot:
        extra["PYGM_SCREENSHOT"] = screenshot
    result = subprocess.run(
        [sys.executable, str(RUN_GAME),
         str(REPO_ROOT / "samples" / sample / "project.json"), language],
        capture_output=True, text=True, timeout=timeout, env=_engine_env(**extra))
    return result, (result.stdout or "") + (result.stderr or "")


# --- layer 1: the mechanism ------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("120", 120),
    ("1", 1),
    ("", 0),            # unset: run forever, i.e. a player's game
    ("0", 0),
    ("-5", 0),          # nonsense must not mean "quit immediately"
    ("abc", 0),
    ("12.5", 0),
])
def test_frame_budget_parsing(monkeypatch, raw, expected):
    """A player's game must never be affected, so anything not a positive
    integer means "no budget" rather than an early exit or a crash."""
    from runtime.game_runner import GameRunner

    if raw == "":
        monkeypatch.delenv("PYGM_MAX_FRAMES", raising=False)
    else:
        monkeypatch.setenv("PYGM_MAX_FRAMES", raw)
    assert GameRunner._frame_budget() == expected


def test_screenshot_hook_is_a_no_op_when_unset(monkeypatch):
    from runtime.game_runner import GameRunner

    monkeypatch.delenv("PYGM_SCREENSHOT", raising=False)
    runner = GameRunner.__new__(GameRunner)
    runner.screen = object()  # would explode if pygame.image.save were called
    runner._save_final_frame()  # must simply return


# --- layer 2: the engine reaches real frames in its own process -----------

def test_the_engine_reports_the_frames_it_rendered():
    """The signal the whole verification rests on. Without it the only
    available check was "the process had not died yet after N seconds", which
    cannot tell a running game from one stuck on a black screen before its
    first frame."""
    result, output = _run_sample("maze_1", 30)
    assert MARKER in output, output[-2000:]
    assert int(output.split(MARKER)[1].split()[0]) == 30
    assert result.returncode == 0, output[-2000:]


def test_a_budgeted_run_exits_by_itself():
    """It must exit cleanly, not hang: a harness that has to kill the process
    cannot tell a clean run from a wedged one. (Killing a one-file PyInstaller
    build is genuinely awkward -- the bootloader spawns a child that keeps the
    pipes open -- so the budget is what avoids needing to.)"""
    result, _ = _run_sample("maze_1", 15, timeout=120)
    assert result.returncode == 0


@pytest.mark.parametrize("sample", ["maze_1", "plateforme_2", "raycast_4"])
def test_reported_samples_render_frames(sample):
    """The three shapes the user reported broken as .exe files: a plain maze,
    a tile-based platformer, and a game whose renderer comes from a folder
    extension. Each must reach real frames in a separate process, which is how
    the frozen build is measured."""
    result, output = _run_sample(sample, 40, language="fr")
    assert MARKER in output, output[-2000:]
    assert int(output.split(MARKER)[1].split()[0]) == 40
    assert result.returncode == 0


def test_screenshot_hook_writes_a_real_frame(tmp_path):
    """Comparing the export against the IDE needs a picture from each side."""
    shot = tmp_path / "frame.png"
    result, output = _run_sample("maze_1", 20, screenshot=shot)
    assert result.returncode == 0, output[-2000:]
    assert shot.exists(), "no frame was saved: %s" % output[-1500:]

    from PIL import Image
    with Image.open(shot) as image:
        assert image.size[0] > 0 and image.size[1] > 0
        colours = image.convert("RGB").getcolors(maxcolors=1 << 20)
    assert colours and len(colours) > 1, (
        "the saved frame is a single flat colour, i.e. nothing was drawn")


def test_two_different_samples_do_not_render_the_same_frame(tmp_path):
    """Guards the comparison itself. If it reported 0% difference for
    everything, a pixel-identical result would prove nothing."""
    from tools.verify_desktop_export import compare_frames

    first = tmp_path / "maze1.png"
    second = tmp_path / "maze2.png"
    _run_sample("maze_1", 20, screenshot=first)
    _run_sample("maze_2", 20, screenshot=second)
    assert first.exists() and second.exists()

    assert compare_frames(first, first, 0.02) == "", (
        "a frame must match itself")
    assert compare_frames(first, second, 0.02) != "", (
        "two different games must not compare as identical")


# --- layer 3: a real build, launched --------------------------------------

@pytest.mark.skipif(not E2E_ENABLED,
                    reason="set PYGM_E2E_EXPORT=1 to run a real PyInstaller "
                           "build (minutes); see tools/verify_desktop_export.py")
def test_a_real_export_builds_launches_and_renders():
    from tools.verify_desktop_export import verify

    problem = verify("maze_1", frames=60, timeout=180, language="en",
                     keep=False, compare=True, tolerance=0.02)
    assert problem == "", problem


def test_the_verifier_tool_exists_and_is_runnable():
    """Layer 3 is opt-in, so the tool must at least be importable and its
    host mapping correct -- otherwise it would rot unnoticed and the manual
    cross-platform check would have nothing to run."""
    from tools.verify_desktop_export import exporter_for_host

    exporter_class, label = exporter_for_host()
    import platform
    if platform.system() in ("Windows", "Linux", "Darwin"):
        assert exporter_class is not None, label
        assert exporter_class.required_host_platform == platform.system()
    else:
        assert exporter_class is None
