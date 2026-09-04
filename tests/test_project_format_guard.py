"""Project-format-version guard — DEFERRED_ITEMS_PLAN.md Tier 0, item 12.

Task 1 of docs/extension_compat_2_0/PLAN.md: a 1.x-line PyGameMaker build
must refuse (not crash, not silently save-and-corrupt) a project whose
format_version is newer than it understands. Covers the pure guard
function, its wiring into ProjectManager.load_project(), and the IDE-layer
message it triggers.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


class TestCheckProjectFormat:
    def test_absent_format_version_defaults_to_1_0(self):
        from core.project_format import check_project_format
        assert check_project_format({}) == (1, 0)

    def test_explicit_1_0(self):
        from core.project_format import check_project_format
        assert check_project_format({"format_version": "1.0"}) == (1, 0)

    def test_at_the_supported_boundary(self):
        from core.project_format import check_project_format, SUPPORTED_FORMAT
        assert check_project_format({"format_version": "1.9"}) == SUPPORTED_FORMAT

    def test_newer_major_version_refused(self):
        from core.project_format import check_project_format, ProjectTooNewError
        with pytest.raises(ProjectTooNewError) as exc_info:
            check_project_format({"format_version": "2.0"})
        assert exc_info.value.fmt == (2, 0)

    def test_newer_minor_version_refused(self):
        from core.project_format import check_project_format, ProjectTooNewError
        with pytest.raises(ProjectTooNewError) as exc_info:
            check_project_format({"format_version": "1.10"})
        assert exc_info.value.fmt == (1, 10)

    def test_malformed_format_version_does_not_crash(self):
        from core.project_format import check_project_format
        assert check_project_format({"format_version": "banana"}) == (1, 0)

    def test_non_string_format_version_does_not_crash(self):
        from core.project_format import check_project_format
        # A hand-edited or generator-produced file could have this as a
        # bare number rather than a string; must not raise TypeError.
        assert check_project_format({"format_version": 1.0}) == (1, 0)


class TestLoadProjectFormatGuard:
    @pytest.fixture
    def project_manager(self):
        with patch('PySide6.QtCore.QTimer'):
            from core.project_manager import ProjectManager
            pm = ProjectManager(asset_manager=MagicMock())
            pm.auto_save_timer = MagicMock()
            return pm

    def test_ordinary_project_loads_and_clears_format_error(self, project_manager, temp_project_dir):
        assert project_manager.load_project(temp_project_dir) is True
        assert project_manager.last_load_format_error is None
        assert project_manager.current_project_path == temp_project_dir

    def test_too_new_project_is_refused(self, project_manager, temp_project_dir):
        project_file = temp_project_dir / "project.json"
        data = json.loads(project_file.read_text(encoding="utf-8"))
        data["format_version"] = "2.0"
        project_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        before = project_file.read_bytes()

        result = project_manager.load_project(temp_project_dir)

        assert result is False
        assert project_manager.last_load_format_error == (2, 0)
        # Refused before current_project_path/current_project_data were
        # ever set — the load never "half completed".
        assert project_manager.current_project_path is None
        # The guard must fire before any code path could resave the file;
        # confirm the on-disk bytes are untouched by the failed attempt.
        assert project_file.read_bytes() == before

    def test_forward_compatible_minor_version_still_loads(self, project_manager, temp_project_dir):
        project_file = temp_project_dir / "project.json"
        data = json.loads(project_file.read_text(encoding="utf-8"))
        data["format_version"] = "1.5"
        project_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

        assert project_manager.load_project(temp_project_dir) is True
        assert project_manager.last_load_format_error is None

    def test_successful_load_clears_a_previous_format_error(self, project_manager, temp_project_dir, temp_dir):
        # First attempt: too-new project sets last_load_format_error.
        too_new_dir = temp_dir / "too_new"
        too_new_dir.mkdir()
        (too_new_dir / "project.json").write_text(
            json.dumps({"name": "X", "version": "1.0.0", "assets": {},
                        "format_version": "9.9"}),
            encoding="utf-8")
        assert project_manager.load_project(too_new_dir) is False
        assert project_manager.last_load_format_error == (9, 9)

        # Second attempt: an ordinary project must clear the stale flag,
        # not leave the UI thinking the CURRENT project is too new.
        assert project_manager.load_project(temp_project_dir) is True
        assert project_manager.last_load_format_error is None


class TestShowLoadFailureMessage:
    """core/ide_window.py's PyGameMakerIDE._show_load_failure_message, via
    the repo's established unbound-call-on-a-stub pattern (see
    tests/test_build_game.py)."""

    def _ide_cls(self):
        from core.ide_window import PyGameMakerIDE
        return PyGameMakerIDE

    class _StubIDE:
        def __init__(self, last_load_format_error):
            self.project_manager = MagicMock()
            self.project_manager.last_load_format_error = last_load_format_error

        def tr(self, text):
            return text

    def test_format_error_shows_specific_message(self):
        stub = self._StubIDE(last_load_format_error=(2, 0))
        with patch('core.ide._project_actions.QMessageBox') as mock_box:
            self._ide_cls()._show_load_failure_message(stub, "Failed to load project")
        title = mock_box.warning.call_args[0][1]
        message = mock_box.warning.call_args[0][2]
        assert "Too New" in title
        assert "2.0" in message

    def test_other_failure_shows_generic_message(self):
        stub = self._StubIDE(last_load_format_error=None)
        with patch('core.ide._project_actions.QMessageBox') as mock_box:
            self._ide_cls()._show_load_failure_message(stub, "Failed to load project")
        title = mock_box.warning.call_args[0][1]
        message = mock_box.warning.call_args[0][2]
        assert title == "Error"
        assert message == "Failed to load project"
