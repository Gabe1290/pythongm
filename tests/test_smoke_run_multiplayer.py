"""tools/smoke_run_multiplayer.py (Phase 8.5) -- a two-real-subprocess
LAN multiplayer smoke test, proving the actual CLI/subprocess deployment
path (two real OS processes, real 127.0.0.1 socket) works, not just the
in-process pytest coverage.

Structural checks run every time (cheap). The real end-to-end run
(actually launching both subprocesses) is opt-in behind
PYGM_E2E_MULTIPLAYER=1, matching tests/test_desktop_export_end_to_end.py's
PYGM_E2E_EXPORT=1 precedent -- real subprocess launches with a 0.5s
head-start sleep and a real socket handshake take a few real seconds,
not appropriate for the default fast suite.
"""
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

TOOL = REPO_ROOT / "tools" / "smoke_run_multiplayer.py"


def test_tool_exists_and_compiles():
    assert TOOL.is_file()
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(TOOL)],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_reseau_1_is_registered():
    text = TOOL.read_text(encoding="utf-8")
    assert '"reseau_1"' in text


def test_scoping_rationale_is_documented():
    """Pins the actual design decision, not just its outcome: v1's
    multiplayer_lan_1 and reseau_2/reseau_3 are deliberately NOT in this
    tool's SAMPLES list (see the module docstring for why) -- a future
    edit that silently drops the reasoning without a fresh decision
    should fail this, not just quietly lose the explanation."""
    text = TOOL.read_text(encoding="utf-8")
    assert "multiplayer_lan_1" in text        # named as explicitly out of scope
    assert "reseau_2/reseau_3" in text or ("reseau_2" in text and "reseau_3" in text)


def test_host_env_never_leaks_a_role_from_the_launching_process(monkeypatch):
    """_base_env must strip PYGM_NET_* from os.environ before building a
    child's env -- otherwise running this smoke tool FROM inside another
    multiplayer-launched process would silently inherit the wrong role."""
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    import importlib
    smoke_run_multiplayer = importlib.import_module("smoke_run_multiplayer")

    monkeypatch.setenv("PYGM_NET_AUTOHOST", "1")
    monkeypatch.setenv("PYGM_NET_AUTOJOIN", "10.0.0.5")
    monkeypatch.setenv("PYGM_NET_MODE", "host")
    env = smoke_run_multiplayer._base_env(60)
    assert "PYGM_NET_AUTOHOST" not in env
    assert "PYGM_NET_AUTOJOIN" not in env
    assert "PYGM_NET_MODE" not in env
    assert env["PYGM_MAX_FRAMES"] == "60"
    assert env["SDL_VIDEODRIVER"] == "dummy"


def test_net_status_parsing():
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    import importlib
    smoke_run_multiplayer = importlib.import_module("smoke_run_multiplayer")

    stdout = "some log line\nPYGM_NET_STATUS=role=client connected=1 player_id=1\nmore\n"
    assert smoke_run_multiplayer._net_status(stdout) == (
        "PYGM_NET_STATUS=role=client connected=1 player_id=1")
    assert smoke_run_multiplayer._net_status("no marker here") is None


def test_real_end_to_end_two_subprocess_run():
    if os.environ.get("PYGM_E2E_MULTIPLAYER") != "1":
        import pytest
        pytest.skip("set PYGM_E2E_MULTIPLAYER=1 to run the real two-subprocess smoke test")

    result = subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1/1 multiplayer samples connected successfully." in result.stdout


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
