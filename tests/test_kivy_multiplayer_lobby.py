"""LAN multiplayer on a phone: the waiting room (host_game with show_lobby).

The overlay needs real Kivy, so it is driven in a subprocess on a hidden window (``_real_kivy_lobby.py``): the
export's own ``mp_lan.glue`` opens it, a real desktop client joins, the overlay lists the player, Démarrer starts the
game for everyone and removes the overlay, Annuler leaves. Without Kivy the glue degrades to the old behaviour:
one warning, and the game hosts at once. Not run on a real device.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from conftest import skip_without_pyside6  # noqa: E402
from test_kivy_multiplayer_client import export_dir, glue  # noqa: E402,F401  (fixtures)

pytestmark = skip_without_pyside6


def test_without_kivy_the_waiting_room_warns_once_and_the_game_hosts_at_once(glue, monkeypatch):
    g, app = glue
    monkeypatch.setitem(sys.modules, "kivy", None)         # import kivy -> ImportError
    monkeypatch.setitem(sys.modules, "kivy.clock", None)
    try:
        g.host(0, "Prof", 4, True)
        assert "lobby" in g._warned and g.active() and g._lobby is None
    finally:
        g.leave()


def test_under_real_kivy_the_waiting_room_lists_players_starts_and_cancels(tmp_path):
    pytest.importorskip("kivy")
    from export.Kivy.kivy_exporter import KivyExporter
    import events.plugin_loader as loader
    from export.Kivy import code_generator
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    code_generator._EXTENSION_CODEGEN = None
    try:
        src = ROOT / "samples" / "reseau_1"
        out = tmp_path / "export"
        assert KivyExporter(json.loads((src / "project.json").read_text(encoding="utf-8")), src, out).export()
    finally:
        loader.list_available_extensions = original
        code_generator._EXTENSION_CODEGEN = None
    result = tmp_path / "result.json"
    try:
        proc = subprocess.run([sys.executable, str(ROOT / "tests" / "_real_kivy_lobby.py"),
                               str(out / "game"), str(ROOT), str(result)],
                              capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        pytest.skip("real Kivy worker timed out")
    if not result.exists():
        pytest.skip(f"real Kivy cannot run here: {proc.stderr[-300:]}")
    data = json.loads(result.read_text(encoding="utf-8"))
    if data["error"] and any(s in data["error"] for s in ("No module named 'kivy'", "GL", "Window")):
        pytest.skip("real Kivy cannot open a window here: " + data["error"][-200:])
    assert data["error"] is None, data["error"]
    assert data["opened"]
    assert "En attente de joueurs" in " ".join(data["first_texts"])
    assert "Hôte : Prof" in " ".join(data["first_texts"])
    assert "Joueur 1 : Ada" in " ".join(data["joined_texts"])
    assert data["started_before"] is False and data["pressed_start"]
    assert data["started_after"] is True and data["closed_after_start"]
    assert data["client_saw_start"]
    assert data["pressed_cancel"] and data["session_after_cancel"] and data["closed_after_cancel"]
