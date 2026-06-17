#!/usr/bin/env python3
"""Regression tests for L1 — tutorial-edition base-index fallback.

When an edition gates tutorials to a fixed folder whitelist, localized tutorial
indexes (de/es/it/ru/sl/uk) may omit a curated folder, so
filter_tutorials_for_edition used to return an empty list and the curated
tutorial became unreachable in those languages.

These tests pin the behaviour: when a non-empty (localized) index filters to
nothing for an edition with a fixed folder whitelist, the filter falls back to
the base English index.json so the curated tutorial is still returned. The
gated edition is synthesized here so the tests don't depend on any particular
shipped edition. Pure logic — no Qt needed.
"""

import json

import pytest

import config.editions as editions
from config.editions import filter_tutorials_for_edition


# Synthetic edition gated to a single curated folder, decoupled from the real
# EDITIONS table so removing/renaming a shipped edition can't break these tests.
CURATED = "99_curated_demo"
GATED_EDITION = {
    "name": "Gated Demo",
    "description": "test-only edition gating tutorials to one curated folder",
    "default_blockly_preset": "beginner",
    "tutorial_folders": [CURATED],
}


@pytest.fixture
def force_gated_edition(monkeypatch):
    """Pin get_current_edition to a synthetic single-folder gated edition."""
    monkeypatch.setattr(editions, "get_current_edition", lambda: GATED_EDITION)


# Mirror a real localized (German) index: folders 01-08, none curated.
LOCALIZED_DE = [
    {"folder": f"{i:02d}_x", "title": f"Tut {i}"} for i in range(1, 9)
]

# Mirror the base English index: 01-08 plus the curated folder.
BASE_EN = LOCALIZED_DE + [
    {"folder": CURATED, "title": "Curated Demo"},
]


def _write_base_index(tmp_path, tutorials):
    (tmp_path / "index.json").write_text(
        json.dumps({"tutorials": tutorials}), encoding="utf-8"
    )
    return tmp_path


def test_recovers_curated_from_base_when_localized_lacks_it(
    tmp_path, force_gated_edition
):
    base = _write_base_index(tmp_path, BASE_EN)
    result = filter_tutorials_for_edition(LOCALIZED_DE, base_tutorials_path=base)
    assert [t["folder"] for t in result] == [CURATED]


def test_localized_with_curated_folder_filters_normally(force_gated_edition):
    # If a localized index *does* include the curated folder, no fallback.
    localized_with_curated = LOCALIZED_DE + [
        {"folder": CURATED, "title": "Kuratiertes Demo"}
    ]
    result = filter_tutorials_for_edition(localized_with_curated)
    assert [t["folder"] for t in result] == [CURATED]
    # The localized title is preserved (we did not reach for the English copy).
    assert result[0]["title"] == "Kuratiertes Demo"


def test_no_base_path_means_no_fallback_preserves_old_behaviour(force_gated_edition):
    # Backward compat: without a base path the function cannot recover and
    # returns the (empty) filtered list, exactly as before.
    assert filter_tutorials_for_edition(LOCALIZED_DE) == []


def test_missing_base_index_file_is_graceful(tmp_path, force_gated_edition):
    # Path given but no index.json present -> empty, no exception.
    assert filter_tutorials_for_edition(LOCALIZED_DE, base_tutorials_path=tmp_path) == []


def test_empty_input_does_not_trigger_fallback(tmp_path, force_gated_edition):
    # A genuinely empty index must not be "recovered" into the base list;
    # an empty folder scan is the caller's signal to show a placeholder.
    base = _write_base_index(tmp_path, BASE_EN)
    assert filter_tutorials_for_edition([], base_tutorials_path=base) == []


def test_advanced_edition_returns_all_unchanged(monkeypatch):
    monkeypatch.setattr(
        editions, "get_current_edition",
        lambda: editions.EDITIONS["advanced"],
    )
    # tutorial_folders is None -> pass through untouched, base path ignored.
    assert filter_tutorials_for_edition(LOCALIZED_DE) == LOCALIZED_DE


def test_beginner_edition_filters_to_its_subset(monkeypatch):
    monkeypatch.setattr(
        editions, "get_current_edition",
        lambda: editions.EDITIONS["beginner"],
    )
    tutorials = [
        {"folder": "01_getting_started", "title": "a"},
        {"folder": "02_first_game", "title": "b"},
        {"folder": "08_lunar_lander", "title": "c"},
    ]
    result = filter_tutorials_for_edition(tutorials)
    assert [t["folder"] for t in result] == ["01_getting_started", "02_first_game"]
