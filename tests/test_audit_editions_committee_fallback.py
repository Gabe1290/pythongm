#!/usr/bin/env python3
"""Regression tests for L1 (config/editions.py:12).

The 'committee' edition gates tutorials to the single curated folder
'09_catch_the_coins'. Localized tutorial indexes (de/es/it/ru/sl/uk) omit that
folder, so filter_tutorials_for_edition used to return an empty list and the
curated tutorial became unreachable in every IDE language except en/fr.

These tests pin the new behaviour: when a non-empty (localized) index filters
to nothing for an edition with a fixed folder whitelist, the filter falls back
to the base English index.json so the curated tutorial is still returned.
Pure logic — no Qt needed.
"""

import json

import pytest

import config.editions as editions
from config.editions import filter_tutorials_for_edition


@pytest.fixture
def force_committee(monkeypatch):
    """Pin get_current_edition to the committee config regardless of Config."""
    monkeypatch.setattr(
        editions, "get_current_edition",
        lambda: editions.EDITIONS["committee"],
    )


# Mirror the real localized (German) index: folders 01-08, no 09.
LOCALIZED_DE = [
    {"folder": f"{i:02d}_x", "title": f"Tut {i}"} for i in range(1, 9)
]

# Mirror the base English index: 01-08 plus the committee's curated 09.
BASE_EN = LOCALIZED_DE + [
    {"folder": "09_catch_the_coins", "title": "Catch the Coins"},
]


def _write_base_index(tmp_path, tutorials):
    (tmp_path / "index.json").write_text(
        json.dumps({"tutorials": tutorials}), encoding="utf-8"
    )
    return tmp_path


def test_committee_recovers_curated_from_base_when_localized_lacks_it(
    tmp_path, force_committee
):
    base = _write_base_index(tmp_path, BASE_EN)
    result = filter_tutorials_for_edition(LOCALIZED_DE, base_tutorials_path=base)
    assert [t["folder"] for t in result] == ["09_catch_the_coins"]


def test_committee_localized_with_curated_folder_filters_normally(force_committee):
    # If a localized index *does* include 09, no fallback is needed.
    localized_with_09 = LOCALIZED_DE + [
        {"folder": "09_catch_the_coins", "title": "Schnapp die Muenzen"}
    ]
    result = filter_tutorials_for_edition(localized_with_09)
    assert [t["folder"] for t in result] == ["09_catch_the_coins"]
    # The localized title is preserved (we did not reach for the English copy).
    assert result[0]["title"] == "Schnapp die Muenzen"


def test_no_base_path_means_no_fallback_preserves_old_behaviour(force_committee):
    # Backward compat: without a base path the function cannot recover and
    # returns the (empty) filtered list, exactly as before.
    assert filter_tutorials_for_edition(LOCALIZED_DE) == []


def test_missing_base_index_file_is_graceful(tmp_path, force_committee):
    # Path given but no index.json present -> empty, no exception.
    assert filter_tutorials_for_edition(LOCALIZED_DE, base_tutorials_path=tmp_path) == []


def test_empty_input_does_not_trigger_fallback(tmp_path, force_committee):
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
