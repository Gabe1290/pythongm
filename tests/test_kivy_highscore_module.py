"""Tests for the exported high-score module (game/highscore.py).

The Kivy export now ships a standalone highscore.py (written verbatim, so its
many literal braces need no escaping) that persists the top scores to
highscores.json and shows a Kivy popup table. show_highscore / clear_highscore
actions call into it.

These tests exercise the module's persistence logic (load/save/qualify/add/
clear) by importing the generated source against a temp data file — the Kivy
popup UI itself isn't driven headlessly, but the storage core is.
"""

import importlib.util
import json
import py_compile
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO_ROOT = Path(__file__).parent.parent
SAMPLE = REPO_ROOT / "samples" / "plateforme_1"


def _export(tmp_path):
    from export.Kivy.kivy_exporter import KivyExporter
    data = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    out = tmp_path / "export"
    exporter = KivyExporter(data, SAMPLE, out)
    assert exporter.export() is True
    return out / "game" / "highscore.py"


def _load_module(path, data_file):
    """Import the generated highscore.py in isolation, redirecting its store."""
    spec = importlib.util.spec_from_file_location("exported_highscore", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod._FILE = str(data_file)  # redirect persistence off the cwd
    return mod


@pytest.mark.skipif(not (SAMPLE / "project.json").exists(),
                    reason="bundled sample not present")
def test_highscore_module_is_generated_and_compiles(tmp_path):
    hs = _export(tmp_path)
    assert hs.exists()
    py_compile.compile(str(hs), doraise=True)
    text = hs.read_text(encoding="utf-8")
    assert "def show_highscore(" in text
    assert "def clear_highscore(" in text


@pytest.mark.skipif(not (SAMPLE / "project.json").exists(),
                    reason="bundled sample not present")
def test_highscore_persistence_roundtrip(tmp_path):
    hs = _export(tmp_path)
    data_file = tmp_path / "highscores.json"
    mod = _load_module(hs, data_file)

    # Empty table: any positive score qualifies.
    assert mod._load() == []
    assert mod._qualifies(10, []) is True

    # Add entries; they persist sorted descending and survive a reload.
    mod._add("Alice", 100)
    mod._add("Bob", 250)
    mod._add("Cara", 50)
    entries = mod._load()
    assert [n for n, _ in entries] == ["Bob", "Alice", "Cara"]
    assert [s for _, s in entries] == [250, 100, 50]

    # clear_highscore wipes it.
    mod.clear_highscore()
    assert mod._load() == []


@pytest.mark.skipif(not (SAMPLE / "project.json").exists(),
                    reason="bundled sample not present")
def test_highscore_caps_at_ten_and_keeps_top(tmp_path):
    hs = _export(tmp_path)
    mod = _load_module(hs, tmp_path / "hs.json")
    for i in range(15):
        mod._add(f"P{i}", i * 10)
    entries = mod._load()
    assert len(entries) == mod._MAX_ENTRIES == 10
    # Only the top 10 scores (50..140) survive; the lowest five are dropped.
    assert min(s for _, s in entries) == 50
    # A score below the current floor no longer qualifies; one above does.
    assert mod._qualifies(40, entries) is False
    assert mod._qualifies(1000, entries) is True
