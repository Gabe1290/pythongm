"""Regression tests for Stage X units X7-X8: getting a generated main.py
onto a real device (X7) or built into a ready-to-flash combined hex
(X8, V1 only), plus the IDE menu/UI wiring. docs/MICROBIT_STAGE_X_PLAN.md
is the plan. device.py's actual microfs.put() over a real USB serial
connection needs real hardware and is explicitly out of this file's
scope (same standing exception Stage L's own sketch accepts for its
serial link) -- everything here is tested with microfs/the IDE mocked.
hex_build.py's combined-hex construction, by contrast, IS fully tested
here with the real vendored firmware (pure, deterministic Intel Hex
text manipulation, no hardware needed) -- see tests/test_microbit_hex_build.py
for its own, more exhaustive coverage; the classes here cover the UI
wiring around it.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# device.py -- the microfs wrapper
# ---------------------------------------------------------------------------

class TestCopyMainPyDependencyMissing:
    def test_missing_microfs_raises_runtime_error_with_install_instructions(self, tmp_path):
        from extensions.microbit.export.device import copy_main_py
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")
        with patch.dict(sys.modules, {"microfs": None}):
            with pytest.raises(RuntimeError) as exc_info:
                copy_main_py(main_py)
        message = str(exc_info.value)
        assert "microfs" in message
        assert "pip install" in message
        # The established no-admin-rights convention this message reuses.
        assert "administrator rights" in message


class TestCopyMainPyCallsMicrofsPut:
    def test_calls_put_with_target_main_py(self, tmp_path):
        from extensions.microbit.export.device import copy_main_py
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")

        fake_microfs = MagicMock()
        fake_microfs.put.return_value = True
        with patch.dict(sys.modules, {"microfs": fake_microfs}):
            copy_main_py(main_py)

        fake_microfs.put.assert_called_once_with(str(main_py), target="main.py")


class TestCopyMainPyNoBoardFound:
    def test_microbit_not_found_wraps_the_ioerror(self, tmp_path):
        from extensions.microbit.export.device import copy_main_py, MicrobitNotFound
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")

        fake_microfs = MagicMock()
        fake_microfs.put.side_effect = IOError("Could not find micro:bit.")
        with patch.dict(sys.modules, {"microfs": fake_microfs}):
            with pytest.raises(MicrobitNotFound) as exc_info:
                copy_main_py(main_py)
        assert "plugged in" in str(exc_info.value)
        assert "MicroPython" in str(exc_info.value)

    def test_unrelated_ioerror_propagates_unchanged(self, tmp_path):
        from extensions.microbit.export.device import copy_main_py
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")

        fake_microfs = MagicMock()
        fake_microfs.put.side_effect = IOError("No such file.")
        with patch.dict(sys.modules, {"microfs": fake_microfs}):
            with pytest.raises(IOError) as exc_info:
                copy_main_py(main_py)
        assert str(exc_info.value) == "No such file."


# ---------------------------------------------------------------------------
# export_microbit_code -- the File-menu handler's UI flow
# ---------------------------------------------------------------------------

def _stub_ide(tmp_path, *, project_open=True):
    """A minimal stand-in for PyGameMakerIDE, exposing only what
    export_microbit_code actually calls -- the same SimpleNamespace-stub
    approach test_thymio_extension.py uses for the Welcome-tab test,
    faster and more isolated than constructing a real IDE for a pure
    dialog-flow check (the real-IDE menu-wiring test below covers the
    other half)."""
    ide = SimpleNamespace()
    ide.tr = lambda s: s
    ide.current_project_path = str(tmp_path) if project_open else None
    ide.current_project_data = {"name": "TestProject", "assets": {}}
    ide._require_open_project = MagicMock(return_value=project_open)
    ide._ask_export_dir = MagicMock(return_value=str(tmp_path / "out"))
    ide.update_status = MagicMock()
    return ide


def _write_project(tmp_path, objects):
    (tmp_path / "project.json").write_text(json.dumps({
        "name": "TestProject", "assets": {"objects": objects},
    }), encoding="utf-8")


ONE_BOARD = {"microbit_1": {"events": {"create": {"actions": [
    {"action": "microbit_show_image", "parameters": {"image": "HEART"}},
]}}}}

TWO_BOARDS = {
    "microbit_a": {"events": {"create": {"actions": [
        {"action": "microbit_show_image", "parameters": {"image": "HEART"}}]}}},
    "microbit_b": {"events": {"create": {"actions": [
        {"action": "microbit_stop_sound", "parameters": {}}]}}},
}


class TestExportMicrobitCodeEarlyExits:
    def test_no_open_project_exports_nothing(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        ide = _stub_ide(tmp_path, project_open=False)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            export_microbit_code(ide)
        mock_input.getItem.assert_not_called()

    def test_board_version_cancelled_exports_nothing(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, ONE_BOARD)
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("", False)  # user cancelled
            export_microbit_code(ide)
        ide._ask_export_dir.assert_not_called()

    def test_no_output_dir_chosen_exports_nothing(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, ONE_BOARD)
        ide = _stub_ide(tmp_path)
        ide._ask_export_dir.return_value = ""  # user cancelled the picker
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V2 (2020 or later)", True)
            with patch("extensions.microbit.export.QMessageBox") as mock_box:
                export_microbit_code(ide)
        mock_box.information.assert_not_called()
        assert not (tmp_path / "out").exists()


class TestExportMicrobitCodeBoardVersionChoice:
    def test_v2_chosen_passes_through_to_the_exporter(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, ONE_BOARD)
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V2 (2020 or later)", True)
            with patch("extensions.microbit.export.QMessageBox"):
                with patch("extensions.microbit.export._offer_copy_to_device"):
                    export_microbit_code(ide)
        main_py = (tmp_path / "out" / "microbit_1" / "main.py").read_text(encoding="utf-8")
        assert "display.show(Image.HEART)" in main_py

    def test_v1_chosen_skips_v2_only_actions(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, {"microbit_1": {"events": {"create": {"actions": [
            {"action": "microbit_if_button", "parameters": {"button": "logo"}},
            {"action": "microbit_clear_display", "parameters": {}},
        ]}}}})
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V1 (original, 2016-2020)", True)
            with patch("extensions.microbit.export.QMessageBox") as mock_box:
                with patch("extensions.microbit.export._offer_copy_to_device"):
                    export_microbit_code(ide)
        main_py = (tmp_path / "out" / "microbit_1" / "main.py").read_text(encoding="utf-8")
        assert "pin_logo" not in main_py
        # The V1-incompatible warning should surface in the success dialog.
        info_call = mock_box.information.call_args
        assert "needs a V2 board" in info_call[0][2]


class TestExportMicrobitCodeResults:
    def test_export_exception_shows_critical_dialog(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, ONE_BOARD)
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V2 (2020 or later)", True)
            with patch("extensions.microbit.export.MicropythonExporter") as mock_cls:
                mock_cls.return_value.export.side_effect = RuntimeError("boom")
                with patch("extensions.microbit.export.QMessageBox") as mock_box:
                    export_microbit_code(ide)
        mock_box.critical.assert_called_once()
        assert "boom" in mock_box.critical.call_args[0][2]

    def test_no_microbit_objects_shows_warning_dialog(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, {"obj_player": {"events": {}}})
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V2 (2020 or later)", True)
            with patch("extensions.microbit.export.QMessageBox") as mock_box:
                export_microbit_code(ide)
        mock_box.warning.assert_called_once()
        mock_box.information.assert_not_called()

    def test_success_shows_information_dialog_with_count_and_path(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, ONE_BOARD)
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V2 (2020 or later)", True)
            with patch("extensions.microbit.export.QMessageBox") as mock_box:
                mock_box.StandardButton.No = 0
                mock_box.information.return_value = 0  # "No" to open-folder
                with patch("extensions.microbit.export._offer_copy_to_device"):
                    export_microbit_code(ide)
        message = mock_box.information.call_args[0][2]
        assert "1 micro:bit object" in message
        assert str(tmp_path / "out") in message


class TestExportMicrobitCodeDeviceCopyOffer:
    def test_offered_for_exactly_one_object(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, ONE_BOARD)
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V2 (2020 or later)", True)
            with patch("extensions.microbit.export.QMessageBox"):
                with patch("extensions.microbit.export._offer_copy_to_device") as mock_offer:
                    export_microbit_code(ide)
        mock_offer.assert_called_once()
        # Called with the one object's actual written main.py path.
        called_path = mock_offer.call_args[0][1]
        assert called_path == tmp_path / "out" / "microbit_1" / "main.py"

    def test_not_offered_for_two_objects(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, TWO_BOARDS)
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V2 (2020 or later)", True)
            with patch("extensions.microbit.export.QMessageBox"):
                with patch("extensions.microbit.export._offer_copy_to_device") as mock_offer:
                    export_microbit_code(ide)
        mock_offer.assert_not_called()


class TestExportMicrobitCodeHexBuildOffer:
    """The "build a .hex" offer (X8 for V1, docs/MICROBIT_V2_HEX_PLAN.md for
    V2) is made for either board version and, like the device-copy offer, only
    for exactly one exported object. The chosen version is passed on."""

    def test_offered_for_v1_with_one_object(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, ONE_BOARD)
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V1 (original, 2016-2020)", True)
            with patch("extensions.microbit.export.QMessageBox"):
                with patch("extensions.microbit.export._offer_copy_to_device"):
                    with patch("extensions.microbit.export._offer_build_hex") as mock_offer:
                        export_microbit_code(ide)
        mock_offer.assert_called_once()
        called_path = mock_offer.call_args[0][1]
        assert called_path == tmp_path / "out" / "microbit_1" / "main.py"
        assert mock_offer.call_args[0][2] == "v1"

    def test_offered_for_v2_with_one_object(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, ONE_BOARD)
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V2 (2020 or later)", True)
            with patch("extensions.microbit.export.QMessageBox"):
                with patch("extensions.microbit.export._offer_copy_to_device"):
                    with patch("extensions.microbit.export._offer_build_hex") as mock_offer:
                        export_microbit_code(ide)
        mock_offer.assert_called_once()
        assert mock_offer.call_args[0][1] == tmp_path / "out" / "microbit_1" / "main.py"
        assert mock_offer.call_args[0][2] == "v2"

    def test_not_offered_for_v2_with_two_objects(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, TWO_BOARDS)
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V2 (2020 or later)", True)
            with patch("extensions.microbit.export.QMessageBox"):
                with patch("extensions.microbit.export._offer_copy_to_device"):
                    with patch("extensions.microbit.export._offer_build_hex") as mock_offer:
                        export_microbit_code(ide)
        mock_offer.assert_not_called()

    def test_not_offered_for_v1_with_two_objects(self, tmp_path):
        from extensions.microbit.export import export_microbit_code
        _write_project(tmp_path, TWO_BOARDS)
        ide = _stub_ide(tmp_path)
        with patch("extensions.microbit.export.QInputDialog") as mock_input:
            mock_input.getItem.return_value = ("V1 (original, 2016-2020)", True)
            with patch("extensions.microbit.export.QMessageBox"):
                with patch("extensions.microbit.export._offer_copy_to_device"):
                    with patch("extensions.microbit.export._offer_build_hex") as mock_offer:
                        export_microbit_code(ide)
        mock_offer.assert_not_called()


class TestOfferCopyToDevice:
    def test_user_declines_copy_is_not_attempted(self, tmp_path):
        from extensions.microbit.export import _offer_copy_to_device
        ide = _stub_ide(tmp_path)
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")
        with patch("extensions.microbit.export.QMessageBox") as mock_box:
            mock_box.StandardButton.No = 0
            mock_box.question.return_value = 0
            with patch("extensions.microbit.export.device.copy_main_py") as mock_copy:
                _offer_copy_to_device(ide, main_py)
        mock_copy.assert_not_called()

    def test_user_accepts_and_copy_succeeds(self, tmp_path):
        # Patches copy_main_py on the real device module, not the module
        # object itself -- _offer_copy_to_device does `from .device import
        # copy_main_py` *inside* the function, which resolves via
        # sys.modules at call time, so swapping out the whole `device`
        # attribute on the package wouldn't be seen by that import.
        from extensions.microbit.export import _offer_copy_to_device
        ide = _stub_ide(tmp_path)
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")
        with patch("extensions.microbit.export.QMessageBox") as mock_box:
            mock_box.StandardButton.Yes = 1
            mock_box.question.return_value = 1
            with patch("extensions.microbit.export.device.copy_main_py") as mock_copy:
                _offer_copy_to_device(ide, main_py)
                mock_copy.assert_called_once_with(main_py)
        mock_box.information.assert_called_once()

    def test_copy_failure_shows_critical_dialog(self, tmp_path):
        from extensions.microbit.export import _offer_copy_to_device
        ide = _stub_ide(tmp_path)
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")
        with patch("extensions.microbit.export.QMessageBox") as mock_box:
            mock_box.StandardButton.Yes = 1
            mock_box.question.return_value = 1
            with patch("extensions.microbit.export.device.copy_main_py") as mock_copy:
                mock_copy.side_effect = RuntimeError("no board")
                _offer_copy_to_device(ide, main_py)
        mock_box.critical.assert_called_once()
        assert "no board" in mock_box.critical.call_args[0][2]


class TestOfferBuildHex:
    """_offer_build_hex does `from . import hex_build` inside the function,
    resolved via sys.modules at call time -- same reasoning as
    _offer_copy_to_device's own device.copy_main_py patch, so the attribute to
    patch is on the real hex_build module. With no version given it builds for
    V1 (X8); "v2" uses the V2 builder."""

    def test_user_declines_build_is_not_attempted(self, tmp_path):
        from extensions.microbit.export import _offer_build_hex
        ide = _stub_ide(tmp_path)
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")
        with patch("extensions.microbit.export.QMessageBox") as mock_box:
            mock_box.StandardButton.No = 0
            mock_box.question.return_value = 0
            with patch("extensions.microbit.export.hex_build.build_v1_combined_hex") as mock_build:
                _offer_build_hex(ide, main_py)
        mock_build.assert_not_called()

    def test_user_accepts_and_build_succeeds(self, tmp_path):
        from extensions.microbit.export import _offer_build_hex
        ide = _stub_ide(tmp_path)
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")
        with patch("extensions.microbit.export.QMessageBox") as mock_box:
            mock_box.StandardButton.Yes = 1
            mock_box.question.return_value = 1
            with patch("extensions.microbit.export.hex_build.build_v1_combined_hex") as mock_build:
                _offer_build_hex(ide, main_py)
                mock_build.assert_called_once_with(main_py, main_py.with_suffix('.hex'))
        mock_box.information.assert_called_once()
        assert str(main_py.with_suffix('.hex')) in mock_box.information.call_args[0][2]

    def test_build_failure_shows_critical_dialog(self, tmp_path):
        from extensions.microbit.export import _offer_build_hex
        ide = _stub_ide(tmp_path)
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")
        with patch("extensions.microbit.export.QMessageBox") as mock_box:
            mock_box.StandardButton.Yes = 1
            mock_box.question.return_value = 1
            with patch("extensions.microbit.export.hex_build.build_v1_combined_hex") as mock_build:
                mock_build.side_effect = RuntimeError("script too large")
                _offer_build_hex(ide, main_py)
        mock_box.critical.assert_called_once()
        assert "script too large" in mock_box.critical.call_args[0][2]


class TestOfferBuildHexV2:
    def _yes(self, mock_box):
        mock_box.StandardButton.Yes = 1
        mock_box.question.return_value = 1

    def test_v2_uses_the_v2_builder_and_not_the_v1_one(self, tmp_path):
        from extensions.microbit.export import _offer_build_hex
        ide = _stub_ide(tmp_path)
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")
        with patch("extensions.microbit.export.QMessageBox") as mock_box:
            self._yes(mock_box)
            with patch("extensions.microbit.export.hex_build.build_v2_combined_hex") as v2, \
                 patch("extensions.microbit.export.hex_build.build_v1_combined_hex") as v1:
                _offer_build_hex(ide, main_py, "v2")
                v2.assert_called_once_with(main_py, main_py.with_suffix('.hex'))
                v1.assert_not_called()
        mock_box.information.assert_called_once()

    def test_v1_still_uses_the_v1_builder_when_the_version_is_given(self, tmp_path):
        from extensions.microbit.export import _offer_build_hex
        ide = _stub_ide(tmp_path)
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")
        with patch("extensions.microbit.export.QMessageBox") as mock_box:
            self._yes(mock_box)
            with patch("extensions.microbit.export.hex_build.build_v2_combined_hex") as v2, \
                 patch("extensions.microbit.export.hex_build.build_v1_combined_hex") as v1:
                _offer_build_hex(ide, main_py, "v1")
                v1.assert_called_once()
                v2.assert_not_called()

    def test_the_question_names_the_board_version(self, tmp_path):
        from extensions.microbit.export import _offer_build_hex
        ide = _stub_ide(tmp_path)
        main_py = tmp_path / "main.py"
        main_py.write_text("# test\n", encoding="utf-8")
        asked = {}
        for version in ("v1", "v2"):
            with patch("extensions.microbit.export.QMessageBox") as mock_box:
                mock_box.StandardButton.No = 0
                mock_box.question.return_value = 0
                _offer_build_hex(ide, main_py, version)
                asked[version] = mock_box.question.call_args[0][2]
        assert "V1 micro:bit" in asked["v1"] and "V2" not in asked["v1"]
        assert "V2 micro:bit" in asked["v2"] and "V1" not in asked["v2"]

    def test_a_script_too_big_for_v2_shows_the_numbers_not_a_traceback(self, tmp_path):
        from extensions.microbit.export import _offer_build_hex
        ide = _stub_ide(tmp_path)
        main_py = tmp_path / "main.py"
        main_py.write_bytes(b"#" * 25000)
        with patch("extensions.microbit.export.QMessageBox") as mock_box:
            self._yes(mock_box)
            _offer_build_hex(ide, main_py, "v2")          # the REAL builder
        mock_box.critical.assert_called_once()
        text = mock_box.critical.call_args[0][2]
        assert "25000 bytes" in text and "20150" in text
        assert not main_py.with_suffix('.hex').exists()


class TestOfferBuildHexV2RealFirmware:
    """No mocking: a real V2 hex built against the vendored v2.1.2 firmware,
    through the exact function the UI calls, and read back."""

    def test_builds_a_working_v2_hex(self, tmp_path):
        from extensions.microbit.export import _offer_build_hex
        from extensions.microbit.export.hex_build import extract_v2_script
        ide = _stub_ide(tmp_path)
        main_py = tmp_path / "main.py"
        main_py.write_text("from microbit import *\ndisplay.show(Image.HEART)\n",
                            encoding="utf-8")
        with patch("extensions.microbit.export.QMessageBox") as mock_box:
            mock_box.StandardButton.Yes = 1
            mock_box.question.return_value = 1
            _offer_build_hex(ide, main_py, "v2")
        mock_box.critical.assert_not_called()
        output = main_py.with_suffix('.hex')
        assert extract_v2_script(output.read_text(encoding="utf-8")) == main_py.read_bytes()


class TestOfferBuildHexRealFirmware:
    """No mocking: a real combined hex built against the vendored
    firmware, through the exact function the UI calls."""

    def test_builds_a_working_combined_hex(self, tmp_path):
        from extensions.microbit.export.hex_build import build_v1_combined_hex, extract_script
        main_py = tmp_path / "main.py"
        main_py.write_text("from microbit import *\ndisplay.show(Image.HEART)\n",
                            encoding="utf-8")
        output = main_py.with_suffix('.hex')
        build_v1_combined_hex(main_py, output)
        assert output.exists()
        assert extract_script(output.read_text(encoding="utf-8")) == main_py.read_bytes()


# ---------------------------------------------------------------------------
# The real File-menu entry, through a real IDE -- mirrors
# test_thymio_extension.py's test_file_menu_gets_the_aseba_and_roberta_entries.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_file_menu_gets_the_microbit_export_entry(_qapp):
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from core.ide_window import PyGameMakerIDE
    ide = PyGameMakerIDE()
    try:
        texts = [a.text() for a in ide._extension_menus["file"].actions()]
        assert "Export &micro:bit (MicroPython) code..." in texts

        assert callable(ide.export_microbit_code)
        assert ide.export_microbit_action.isEnabled() is False  # no project yet
        ide.current_project_path = "/tmp/whatever"
        ide.current_project_data = {"name": "test_project", "assets": {}}
        ide.update_ui_state()
        assert ide.export_microbit_action.isEnabled() is True
    finally:
        ide.deleteLater()
