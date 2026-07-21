"""Edition-based sample curation (filter_samples_for_edition).

Explicitly choosing the Beginner edition hides the raycast_* samples on the
Welcome tab. Everything else — an UNSET edition (fresh machine),
Advanced, Development — shows all 17. The default is show-all so a
developer's raycast samples never vanish just because Preferences was never
opened; the curation is opt-IN. Pure logic — no Qt.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from config.editions import filter_samples_for_edition, EDITIONS  # noqa: E402
from utils.config import Config  # noqa: E402


SAMPLES = [
    ("samples/maze_1", "Maze — Level 1"),
    ("samples/plateforme_1", "Platform — Level 1"),
    ("samples/match3_1", "Match-3 — Level 1"),
    ("samples/treasure", "Treasure"),
    ("samples/raycast_1", "Raycast — Level 1"),
    ("samples/raycast_4", "Raycast — Level 4"),
]


def _pin_edition(monkeypatch, edition_key):
    """Set what Config.get('edition') returns — the filter reads it directly,
    NOT get_current_edition(), so the Beginner default can't leak in."""
    real = Config.get
    monkeypatch.setattr(Config, "get",
                        classmethod(lambda cls, key, default=None:
                                    edition_key if key == "edition"
                                    else real(key, default)))


def test_unset_edition_shows_all_samples(monkeypatch):
    """The whole point of the show-all-by-default fix: a fresh machine that
    never picked an edition still shows raycast, even though tutorials default
    to Beginner."""
    _pin_edition(monkeypatch, None)
    assert filter_samples_for_edition(SAMPLES) == SAMPLES


def test_explicit_beginner_hides_the_raycast_samples(monkeypatch):
    _pin_edition(monkeypatch, "beginner")
    out = filter_samples_for_edition(SAMPLES)
    paths = [p for p, _ in out]
    assert "samples/maze_1" in paths and "samples/treasure" in paths
    assert not any("raycast" in p for p in paths), "beginner must hide raycast_*"


def test_advanced_and_development_show_everything(monkeypatch):
    for key in ("advanced", "development"):
        _pin_edition(monkeypatch, key)
        assert filter_samples_for_edition(SAMPLES) == SAMPLES, key


def test_show_all_returns_a_copy(monkeypatch):
    """Show-all must not hand back the caller's own list to mutate."""
    _pin_edition(monkeypatch, None)
    out = filter_samples_for_edition(SAMPLES)
    assert out == SAMPLES and out is not SAMPLES


def test_unknown_edition_key_shows_all(monkeypatch):
    """A stale/garbage edition value in config must not blank the samples."""
    _pin_edition(monkeypatch, "no_such_edition")
    assert filter_samples_for_edition(SAMPLES) == SAMPLES


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
