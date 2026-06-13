"""Regression tests for export-target routing (audit M13).

docs/FULL_AUDIT_2026-06-11.md: the export-platform combo items were added
via self.tr(), so in a localized IDE currentText() returns the translated
label. accept_export compared that against hard-coded English literals, so
'Desktop Executable' and 'Source Code (.zip)' silently no-op'd (the else
branch just self.accept()'d) in French/etc., with a false 'Export
completed' status. Routing now uses a locale-independent userData id.
"""

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

EXPECTED_IDS = ["exe", "html5", "kivy", "apk", "zip"]


def _dialog(qapp):
    from dialogs.project_dialogs import ExportProjectDialog
    return ExportProjectDialog(None, {"name": "G"})


class TestComboData:
    def test_items_carry_stable_ids(self, qapp):
        dlg = _dialog(qapp)
        ids = [dlg.export_platform.itemData(i)
               for i in range(dlg.export_platform.count())]
        assert ids == EXPECTED_IDS

    def test_find_data_locates_kivy(self, qapp):
        dlg = _dialog(qapp)
        assert dlg.export_platform.findData("kivy") == 2


class TestRoutingByDataNotText:
    def _route(self, qapp, index):
        dlg = _dialog(qapp)
        # Simulate a translated UI: scramble every display label, keep ids.
        for i in range(dlg.export_platform.count()):
            dlg.export_platform.setItemText(i, f"TRANSLATED_{i}")
        dlg.export_platform.setCurrentIndex(index)
        dlg.output_path_edit.setText("/tmp/out")
        calls = []
        dlg._export_executable = lambda: calls.append("exe")
        dlg._export_html5 = lambda: calls.append("html5")
        dlg._export_kivy = lambda: calls.append("kivy")
        dlg._export_zip = lambda: calls.append("zip")
        dlg.accept_export()
        return calls

    def test_exe_routes_even_when_translated(self, qapp):
        assert self._route(qapp, 0) == ["exe"]  # pre-fix: silent no-op

    def test_zip_routes_even_when_translated(self, qapp):
        assert self._route(qapp, 4) == ["zip"]  # pre-fix: silent no-op

    def test_kivy_and_apk_route_to_kivy(self, qapp):
        assert self._route(qapp, 2) == ["kivy"]
        assert self._route(qapp, 3) == ["kivy"]

    def test_settings_store_stable_id(self, qapp):
        dlg = _dialog(qapp)
        dlg.export_platform.setCurrentIndex(4)  # zip
        dlg.output_path_edit.setText("/tmp/out")
        dlg._export_zip = lambda: None
        dlg.accept_export()
        assert dlg.export_settings["platform"] == "zip"
