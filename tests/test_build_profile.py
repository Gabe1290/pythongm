"""The compiled IDE's start-up profile (utils/build_profile.py, build_config/build_profile.json).

The IDE built on GitHub starts in the Beginner edition, with every extension switched off, and lists
only the beginner samples that need no extension. A choice saved in Preferences still wins; running
from source and exported games are unchanged. The tests point the module at the SHIPPED profile file.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from conftest import skip_without_pyside6  # noqa: E402

from config.editions import filter_samples_for_edition, get_current_edition  # noqa: E402
from events import plugin_loader  # noqa: E402
from utils import build_profile  # noqa: E402
from utils.config import Config  # noqa: E402

SHIPPED = ROOT / "build_config" / "build_profile.json"
EXTENSIONS = sorted(p.name for p in (ROOT / "extensions").iterdir() if (p / "extension.json").is_file())
NEEDING_NOTHING = ["maze_1", "maze_2", "maze_3", "maze_4", "plateforme_1", "plateforme_2",
                   "plateforme_3", "match3_1", "match3_2", "match3_3", "views_1", "views_2",
                   "treasure", "sky_strike_1"]


@pytest.fixture()
def settings(monkeypatch):
    """The saved user settings for this test only (nothing is written to disk)."""
    data = {}
    monkeypatch.setattr(Config, "_config_data", data, raising=False)
    monkeypatch.setattr(Config, "load", classmethod(lambda cls: cls._config_data))
    monkeypatch.setattr(Config, "get", classmethod(lambda cls, key, default=None: data.get(key, default)))
    return data


@pytest.fixture()
def compiled(monkeypatch, settings):
    monkeypatch.setattr(build_profile, "profile_path", lambda: SHIPPED)
    return settings


@pytest.fixture()
def from_source(monkeypatch, settings, tmp_path):
    monkeypatch.setattr(build_profile, "profile_path", lambda: tmp_path / "none.json")
    return settings


def _samples():
    from widgets.welcome_tab import SAMPLE_PROJECTS
    return SAMPLE_PROJECTS


def _names(shown):
    return [path.rsplit("/", 1)[-1] for path, _label in shown]


def test_the_shipped_profile_says_what_was_asked():
    assert json.loads(SHIPPED.read_text(encoding="utf-8")) == {
        "edition": "beginner",
        "extensions_enabled_by_default": False,
        "hide_samples_needing_disabled_extensions": True,
    }


def test_the_build_bundles_it_at_the_top_of_the_bundle():
    spec = (ROOT / "PyGameMaker.spec").read_text(encoding="utf-8")
    assert "(str(project_dir / 'build_config' / 'build_profile.json'), '.')" in spec
    workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
    assert "pyinstaller PyGameMaker.spec" in workflow


def test_a_frozen_bundle_looks_for_it_at_the_top_of_the_bundle(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert build_profile.profile_path() == tmp_path / "build_profile.json"


def test_running_from_source_has_no_profile_file():
    assert not (ROOT / "build_profile.json").exists()


def test_exported_games_do_not_carry_it():
    for path in (ROOT / "export").rglob("*.py"):
        assert "build_profile" not in path.read_text(encoding="utf-8"), path


@pytest.mark.parametrize("content", ["not json", "[1, 2]", ""])
def test_a_damaged_profile_changes_nothing(monkeypatch, tmp_path, content):
    bad = tmp_path / "p.json"
    bad.write_text(content, encoding="utf-8")
    monkeypatch.setattr(build_profile, "profile_path", lambda: bad)
    assert build_profile.load_profile() == {}
    assert build_profile.extension_default(True) is True


def test_every_extension_starts_off_in_the_compiled_ide(compiled):
    assert len(EXTENSIONS) >= 6
    for folder in EXTENSIONS:
        assert plugin_loader.is_extension_enabled(folder, True) is False, folder
    listed = plugin_loader.list_available_extensions()
    assert listed and not any(info["enabled"] for info in listed)


def test_a_saved_choice_wins(compiled):
    compiled["extensions"] = {"raycast_2_5d": True}
    assert plugin_loader.is_extension_enabled("raycast_2_5d", True) is True
    assert plugin_loader.is_extension_enabled("microbit", True) is False


def test_from_source_the_manifest_still_decides(from_source):
    assert plugin_loader.is_extension_enabled("raycast_2_5d", True) is True
    assert plugin_loader.is_extension_enabled("anything", False) is False


def test_the_compiled_ide_is_in_beginner_mode(compiled):
    assert get_current_edition()["name"] == "Beginner"


@skip_without_pyside6
def test_it_lists_only_beginner_samples_that_need_no_extension(compiled):
    assert _names(filter_samples_for_edition(_samples())) == NEEDING_NOTHING


@skip_without_pyside6
def test_every_listed_sample_really_needs_no_extension(compiled):
    for path, _label in filter_samples_for_edition(_samples()):
        data = json.loads((ROOT / path / "project.json").read_text(encoding="utf-8"))
        assert plugin_loader.required_extensions_for_project(data) == [], path
        assert plugin_loader.sample_works_with_enabled_extensions(ROOT / path), path


@skip_without_pyside6
def test_switching_the_microbit_extension_on_brings_its_beginner_sample(compiled):
    compiled["extensions"] = {"microbit": True}
    assert set(_names(filter_samples_for_edition(_samples()))) == set(NEEDING_NOTHING) | {"microbit_1"}


@skip_without_pyside6
def test_a_chosen_advanced_edition_shows_more_but_nothing_that_cannot_run(compiled):
    compiled["edition"] = "advanced"
    shown = _names(filter_samples_for_edition(_samples()))
    assert set(NEEDING_NOTHING) <= set(shown)
    for hidden in ("raycast_1", "raycast_6", "microbit_1", "reseau_1", "block_world_1", "fichier_1"):
        assert hidden not in shown, hidden
    compiled["extensions"] = {"raycast_2_5d": True}
    assert "raycast_1" in _names(filter_samples_for_edition(_samples()))


@skip_without_pyside6
def test_from_source_an_unset_edition_still_shows_every_sample(from_source):
    assert filter_samples_for_edition(_samples()) == list(_samples())


def test_a_sample_that_cannot_be_read_is_not_hidden(compiled, tmp_path):
    (tmp_path / "project.json").write_text("{broken", encoding="utf-8")
    assert plugin_loader.sample_works_with_enabled_extensions(tmp_path) is True
