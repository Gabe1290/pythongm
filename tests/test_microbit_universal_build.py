"""Building ONE hex for both boards (docs/MICROBIT_V2_HEX_PLAN.md, unit H6),
and offering it in the export dialog.
"""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.microbit.export import hex_build  # noqa: E402
from extensions.microbit.export import universal_hex as u  # noqa: E402
from extensions.microbit.export.intel_hex import parse_hex  # noqa: E402

SCRIPT = b"from microbit import *\nwhile True:\n    display.show(Image.HEART)\n    sleep(500)\n"


@pytest.fixture(scope="module")
def universal():
    return hex_build.build_universal_hex(SCRIPT)


# --- the builder -------------------------------------------------------------------------------

def test_the_output_is_a_valid_universal_hex_with_both_boards(universal):
    assert u.is_universal_hex(universal)
    assert [i for i, _ in u.separate_universal_hex(universal)] == [u.BOARD_ID_V1, u.BOARD_ID_V2]
    assert universal.splitlines()[-1] == ":00000001FF"
    assert all(sum(bytes.fromhex(l[1:])) & 0xFF == 0 for l in universal.splitlines())


def test_each_board_gets_exactly_its_own_build_back(universal):
    got = dict(u.separate_universal_hex(universal))
    v1 = hex_build.embed_script(hex_build.V1_FIRMWARE_HEX.read_text(encoding="utf-8"), SCRIPT)
    v2 = hex_build.build_v2_hex(SCRIPT)
    assert parse_hex(got[u.BOARD_ID_V1])[0] == parse_hex(v1)[0]
    assert parse_hex(got[u.BOARD_ID_V2])[0] == parse_hex(v2)[0]


def test_the_script_reads_back_from_both_halves(universal):
    got = dict(u.separate_universal_hex(universal))
    assert hex_build.extract_script(got[u.BOARD_ID_V1]) == SCRIPT
    assert hex_build.extract_v2_script(got[u.BOARD_ID_V2]) == SCRIPT


def test_building_is_deterministic(universal):
    assert hex_build.build_universal_hex(SCRIPT) == universal


# --- limits -------------------------------------------------------------------------------------

def test_the_documented_limits_are_the_real_ones():
    assert hex_build.v1_max_script_size() == 8187
    assert hex_build.v2_max_script_size() == 20150
    assert hex_build.universal_max_script_size() == 8187


def test_the_v1_limit_matches_what_the_v1_builder_really_accepts():
    fw = hex_build.V1_FIRMWARE_HEX.read_text(encoding="utf-8")
    hex_build.embed_script(fw, bytes(8187))                                 # fits
    with pytest.raises(hex_build.ScriptTooLargeError):
        hex_build.embed_script(fw, bytes(8188))                             # does not


def test_the_largest_universal_script_builds_and_reads_back_on_both_boards():
    script = bytes((i * 3 + 1) & 0xFF for i in range(8187))
    got = dict(u.separate_universal_hex(hex_build.build_universal_hex(script)))
    assert hex_build.extract_script(got[u.BOARD_ID_V1]) == script
    assert hex_build.extract_v2_script(got[u.BOARD_ID_V2]) == script


def test_one_byte_more_is_refused_with_both_limits_in_the_message():
    with pytest.raises(hex_build.ScriptTooLargeError, match=r"8188 bytes.*8187.*20150"):
        hex_build.build_universal_hex(bytes(8188))
    hex_build.build_v2_hex(bytes(8188))                    # ... but a V2-only hex is fine


def test_an_empty_script_is_refused():
    with pytest.raises(ValueError, match="empty"):
        hex_build.build_universal_hex(b"")


def test_the_file_helper_writes_the_same_text(tmp_path, universal):
    main_py = tmp_path / "main.py"
    main_py.write_bytes(SCRIPT)
    out = tmp_path / "main.hex"
    hex_build.build_universal_combined_hex(main_py, out)
    assert out.read_text(encoding="utf-8") == universal


def test_the_real_microbit_1_program_fits_a_universal_hex(tmp_path):
    from extensions.microbit.export.micropython_exporter import MicropythonExporter
    project = REPO_ROOT / "samples" / "microbit_1" / "project.json"
    exporter = MicropythonExporter()
    assert exporter.export(str(project), str(tmp_path), "v1")      # "both" exports as V1
    script = Path(next(iter(exporter.exported_files.values()))).read_bytes()
    assert len(script) <= hex_build.universal_max_script_size()
    got = dict(u.separate_universal_hex(hex_build.build_universal_hex(script)))
    assert hex_build.extract_v2_script(got[u.BOARD_ID_V2]) == script
    assert hex_build.extract_script(got[u.BOARD_ID_V1]) == script


# --- the dialog --------------------------------------------------------------------------------

def _ide(tmp_path):
    ide = SimpleNamespace()
    ide.tr = lambda s: s
    ide.current_project_path = str(tmp_path)
    ide.current_project_data = {"name": "p", "assets": {}}
    ide._require_open_project = MagicMock(return_value=True)
    ide._ask_export_dir = MagicMock(return_value=str(tmp_path / "out"))
    ide.update_status = MagicMock()
    return ide


@pytest.mark.parametrize("picked,expected", [
    ("V2 (2020 or later)", "v2"),
    ("V1 (original, 2016-2020)", "v1"),
    ("Both (one .hex for V1 and V2 boards)", "both"),
])
def test_the_version_question_offers_three_choices(tmp_path, picked, expected):
    from extensions.microbit.export import _ask_board_version
    with patch("extensions.microbit.export.QInputDialog") as box:
        box.getItem.return_value = (picked, True)
        assert _ask_board_version(_ide(tmp_path)) == expected
        choices = box.getItem.call_args[0][3]
    assert len(choices) == 3 and choices[0].startswith("V2")


def test_cancelling_the_version_question_returns_none(tmp_path):
    from extensions.microbit.export import _ask_board_version
    with patch("extensions.microbit.export.QInputDialog") as box:
        box.getItem.return_value = ("", False)
        assert _ask_board_version(_ide(tmp_path)) is None


def test_choosing_both_exports_under_v1_rules_and_offers_the_universal_hex(tmp_path):
    from extensions.microbit.export import export_microbit_code
    main_py = tmp_path / "out" / "microbit_1" / "main.py"
    with patch("extensions.microbit.export.QInputDialog") as box, \
         patch("extensions.microbit.export.QMessageBox"), \
         patch("extensions.microbit.export.MicropythonExporter") as exporter_cls, \
         patch("extensions.microbit.export._offer_copy_to_device"), \
         patch("extensions.microbit.export._offer_build_hex") as offer:
        box.getItem.return_value = ("Both (one .hex for V1 and V2 boards)", True)
        exporter = exporter_cls.return_value
        exporter.export.return_value = True
        exporter.exported_files = {"microbit_1": main_py}
        exporter.export_warnings = {}
        export_microbit_code(_ide(tmp_path))
    assert exporter.export.call_args[0][2] == "v1"          # the strictest rules
    assert offer.call_args[0][2] == "both"                   # but the Universal Hex is offered


def test_the_universal_offer_uses_the_universal_builder_and_names_both_boards(tmp_path):
    from extensions.microbit.export import _offer_build_hex
    main_py = tmp_path / "main.py"
    main_py.write_text("# t\n", encoding="utf-8")
    with patch("extensions.microbit.export.QMessageBox") as box:
        box.StandardButton.Yes = 1
        box.question.return_value = 1
        with patch("extensions.microbit.export.hex_build.build_universal_combined_hex") as uni, \
             patch("extensions.microbit.export.hex_build.build_v1_combined_hex") as v1, \
             patch("extensions.microbit.export.hex_build.build_v2_combined_hex") as v2:
            _offer_build_hex(_ide(tmp_path), main_py, "both")
            uni.assert_called_once_with(main_py, main_py.with_suffix(".hex"))
            v1.assert_not_called()
            v2.assert_not_called()
        assert "V1 or V2" in box.question.call_args[0][2]


def test_a_real_universal_build_through_the_ui_function_reads_back(tmp_path):
    from extensions.microbit.export import _offer_build_hex
    main_py = tmp_path / "main.py"
    main_py.write_bytes(SCRIPT)
    with patch("extensions.microbit.export.QMessageBox") as box:
        box.StandardButton.Yes = 1
        box.question.return_value = 1
        _offer_build_hex(_ide(tmp_path), main_py, "both")
    box.critical.assert_not_called()
    got = dict(u.separate_universal_hex(main_py.with_suffix(".hex").read_text(encoding="utf-8")))
    assert hex_build.extract_v2_script(got[u.BOARD_ID_V2]) == SCRIPT
    assert hex_build.extract_script(got[u.BOARD_ID_V1]) == SCRIPT


def test_a_script_too_big_for_the_universal_hex_shows_both_limits(tmp_path):
    from extensions.microbit.export import _offer_build_hex
    main_py = tmp_path / "main.py"
    main_py.write_bytes(b"#" * 9000)
    with patch("extensions.microbit.export.QMessageBox") as box:
        box.StandardButton.Yes = 1
        box.question.return_value = 1
        _offer_build_hex(_ide(tmp_path), main_py, "both")
    text = box.critical.call_args[0][2]
    assert "9000 bytes" in text and "8187" in text and "20150" in text
    assert not main_py.with_suffix(".hex").exists()
