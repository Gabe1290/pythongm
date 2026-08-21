"""Every bundled sample must actually load through the IDE's real loader.

Found the gap this closes the hard way: samples/sky_strike_1's project.json
was missing the top-level "name"/"version" keys ProjectManager._validate_
project_data requires, so opening it from the Welcome tab failed with
"Failed to load project" -- while every existing test for that sample went
through runtime.game_runner.GameRunner directly, which reads project_data
with no such validation at all, so the whole authoring/testing pass never
touched the actual failure. No prior test in this repo loaded a sample
through ProjectManager at all -- this was true of every OTHER bundled
sample too, just never triggered because none of them happened to be
missing the same fields.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLES_DIR = REPO_ROOT / "samples"

SAMPLE_DIRS = sorted(
    p for p in SAMPLES_DIR.iterdir()
    if p.is_dir() and (p / "project.json").exists()
)


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.mark.parametrize("sample_dir", SAMPLE_DIRS, ids=lambda p: p.name)
def test_sample_loads_through_project_manager(_qapp, sample_dir):
    from core.project_manager import ProjectManager

    pm = ProjectManager()
    failures = []
    pm.status_changed.connect(failures.append)

    assert pm.load_project(sample_dir) is True, (
        f"{sample_dir.name} failed to load through the real IDE loader: "
        f"{failures}")
    # project_name is whatever the author put in project.json's "name" --
    # not required to match the folder name (match3_1's is "Match3Game").
    # Loading successfully at all is the property this test protects.
    assert pm.project_name


def test_every_sample_project_json_has_the_required_top_level_keys():
    """Same check ProjectManager._validate_project_data makes, run directly
    over every sample's project.json so a future missing key is caught as a
    plain assertion, not just "the loader silently returned False"."""
    import json

    required = {"name", "version", "assets"}
    for sample_dir in SAMPLE_DIRS:
        data = json.loads((sample_dir / "project.json").read_text(encoding="utf-8"))
        missing = required - data.keys()
        assert not missing, f"{sample_dir.name}/project.json missing {missing}"
        assert isinstance(data["assets"], dict)
