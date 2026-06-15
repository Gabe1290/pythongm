#!/usr/bin/env python3
"""
Regression tests for L34 (FULL_AUDIT_2026-06-11):
asset_utils.save_project_data must write project.json atomically so a crash /
disk-full / power-loss mid-write cannot truncate the previous (valid) file.

Pure logic — no Qt required, runs on Python 3.11.
"""

import json
from pathlib import Path
from unittest import mock

from widgets.asset_tree.asset_utils import save_project_data, load_project_data


def test_save_writes_valid_json(tmp_path):
    project_file = tmp_path / "project.json"
    data = {"assets": {"sprites": {"player": {"name": "player"}}}}

    assert save_project_data(project_file, data) is True
    assert load_project_data(project_file) == data


def test_save_creates_parent_dirs(tmp_path):
    project_file = tmp_path / "nested" / "deeper" / "project.json"
    data = {"assets": {}}

    assert save_project_data(project_file, data) is True
    assert project_file.exists()


def test_failed_write_preserves_previous_file(tmp_path):
    """A crash mid-write must leave the old project.json intact, not truncated."""
    project_file = tmp_path / "project.json"
    good = {"assets": {"sprites": {"keep": {"name": "keep"}}}}
    assert save_project_data(project_file, good) is True

    # Simulate a disk-full / power-loss error during json.dump into the temp file.
    def boom(*args, **kwargs):
        raise OSError("No space left on device")

    with mock.patch("widgets.asset_tree.asset_utils.json.dump", side_effect=boom):
        bad = {"assets": {"sprites": {"new": {"name": "new"}}}}
        assert save_project_data(project_file, bad) is False

    # The original file must still be present and fully valid (not truncated).
    assert load_project_data(project_file) == good


def test_failed_write_leaves_no_temp_debris(tmp_path):
    project_file = tmp_path / "project.json"

    def boom(*args, **kwargs):
        raise OSError("No space left on device")

    with mock.patch("widgets.asset_tree.asset_utils.json.dump", side_effect=boom):
        assert save_project_data(project_file, {"assets": {}}) is False

    # No leftover *.tmp sibling.
    tmp_siblings = list(tmp_path.glob("*.tmp"))
    assert tmp_siblings == [], f"stale temp file(s) left: {tmp_siblings}"


def test_save_is_atomic_via_replace(tmp_path):
    """Confirm the implementation goes through a temp file + os.replace,
    rather than truncating the target with a direct 'w' open."""
    project_file = tmp_path / "project.json"
    good = {"v": 1}
    assert save_project_data(project_file, good) is True

    seen = {}

    real_replace = __import__("os").replace

    def tracking_replace(src, dst):
        seen["src"] = str(src)
        seen["dst"] = str(dst)
        return real_replace(src, dst)

    with mock.patch("widgets.asset_tree.asset_utils.os.replace", side_effect=tracking_replace):
        assert save_project_data(project_file, {"v": 2}) is True

    assert seen["src"].endswith("project.json.tmp")
    assert seen["dst"].endswith("project.json")
    assert load_project_data(project_file) == {"v": 2}


def test_accepts_string_path(tmp_path):
    """Callers may pass a str; save_project_data should coerce it to Path."""
    project_file = tmp_path / "project.json"
    assert save_project_data(str(project_file), {"ok": True}) is True
    assert json.loads(project_file.read_text(encoding="utf-8")) == {"ok": True}
