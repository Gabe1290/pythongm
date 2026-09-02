"""GameRunner._print_net_status -- a grep-able stdout line an external
harness (tools/smoke_run_multiplayer.py) can check for, the same
"opt-in, observable from outside the process" pattern PYGM_FRAMES_COMPLETED
/PYGM_SCREENSHOT already establish for desktop-export verification.
Fires only when a v2 multiplayer session mirrored network_role into
globals -- an ordinary single-player run's stdout is unaffected.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

from runtime.game_runner import GameRunner  # noqa: E402


def _bare_runner():
    runner = GameRunner.__new__(GameRunner)
    runner.global_variables = {}
    return runner


def test_prints_nothing_for_a_single_player_run(capsys):
    runner = _bare_runner()
    runner._print_net_status()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_prints_role_connected_and_player_id_for_a_host(capsys):
    runner = _bare_runner()
    runner.global_variables = {
        "network_role": "host", "network_connected": 1, "player_id": 0,
    }
    runner._print_net_status()
    out = capsys.readouterr().out
    assert "PYGM_NET_STATUS=" in out
    assert "role=host" in out
    assert "connected=1" in out
    assert "player_id=0" in out


def test_prints_role_connected_and_player_id_for_a_client(capsys):
    runner = _bare_runner()
    runner.global_variables = {
        "network_role": "client", "network_connected": 1, "player_id": 1,
    }
    runner._print_net_status()
    out = capsys.readouterr().out
    assert "role=client" in out
    assert "connected=1" in out
    assert "player_id=1" in out


def test_missing_keys_default_sensibly(capsys):
    runner = _bare_runner()
    runner.global_variables = {"network_role": "client"}
    runner._print_net_status()
    out = capsys.readouterr().out
    assert "role=client" in out
    assert "connected=0" in out
    assert "player_id=-1" in out


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
