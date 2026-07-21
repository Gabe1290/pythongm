"""Edition-based sample curation (filter_samples_for_edition).

The IDE edition (Beginner / Advanced / Development) gates which Welcome-tab
sample games appear, mirroring how it already gates tutorials. Beginner hides
the raycast_* samples; Advanced/Development show all. Pure logic — no Qt.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import config.editions as editions  # noqa: E402
from config.editions import filter_samples_for_edition, EDITIONS  # noqa: E402


SAMPLES = [
    ("samples/maze_1", "Maze — Level 1"),
    ("samples/plateforme_1", "Platform — Level 1"),
    ("samples/match3_1", "Match-3 — Level 1"),
    ("samples/treasure", "Treasure"),
    ("samples/raycast_1", "Raycast — Level 1"),
    ("samples/raycast_4", "Raycast — Level 4"),
]


def _pin(monkeypatch, edition_dict):
    monkeypatch.setattr(editions, "get_current_edition", lambda: edition_dict)


def test_beginner_hides_the_raycast_samples(monkeypatch):
    _pin(monkeypatch, EDITIONS["beginner"])
    out = filter_samples_for_edition(SAMPLES)
    paths = [p for p, _ in out]
    assert "samples/maze_1" in paths
    assert "samples/treasure" in paths
    assert not any("raycast" in p for p in paths), "beginner must hide raycast_*"


def test_advanced_and_development_show_everything(monkeypatch):
    for key in ("advanced", "development"):
        _pin(monkeypatch, EDITIONS[key])
        out = filter_samples_for_edition(SAMPLES)
        assert out == SAMPLES, f"{key} must show all samples unchanged"


def test_none_whitelist_returns_a_copy(monkeypatch):
    """Show-all must not hand back the caller's own list to mutate."""
    _pin(monkeypatch, {"sample_folders": None})
    out = filter_samples_for_edition(SAMPLES)
    assert out == SAMPLES and out is not SAMPLES


def test_missing_key_is_treated_as_show_all(monkeypatch):
    """An edition dict without sample_folders (older config) shows everything
    rather than hiding every sample."""
    _pin(monkeypatch, {"name": "X"})       # no sample_folders key
    assert filter_samples_for_edition(SAMPLES) == SAMPLES


def test_folder_name_is_the_basename(monkeypatch):
    _pin(monkeypatch, {"sample_folders": ["maze_1"]})
    out = filter_samples_for_edition(SAMPLES)
    assert out == [("samples/maze_1", "Maze — Level 1")]


def test_beginner_whitelist_matches_the_shipped_non_raycast_samples():
    """The beginner list should be exactly the real sample folders minus
    raycast_*, so no shipped beginner sample is accidentally omitted and no
    stale folder lingers."""
    shipped = sorted(p.name for p in (REPO_ROOT / "samples").iterdir()
                     if (p / "project.json").exists())
    expected = [s for s in shipped if not s.startswith("raycast")]
    assert sorted(EDITIONS["beginner"]["sample_folders"]) == expected


def test_welcome_tab_uses_the_filter(monkeypatch):
    """The Welcome tab and the guide chooser both route through the filter, so
    switching edition curates the visible samples."""
    src = (REPO_ROOT / "widgets" / "welcome_tab.py").read_text(encoding="utf-8")
    # Both the sample grid and the guide chooser route SAMPLE_PROJECTS through
    # the filter, so they stay in step when the edition changes.
    assert src.count("filter_samples_for_edition(SAMPLE_PROJECTS)") == 2
