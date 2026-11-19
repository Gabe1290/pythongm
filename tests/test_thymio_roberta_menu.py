"""Open Roberta export AND import must both be reachable with the Thymio extension on."""
import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path


def test_export_roberta_xml_writes_importable_file(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
    app = QApplication.instance() or QApplication([])
    import extensions.thymio.export as ex

    proj = tmp_path / "p"
    proj.mkdir()
    (proj / "project.json").write_text(json.dumps({
        "name": "p",
        "assets": {"objects": {"thymio_a": {"events": {
            "thymio_button_forward": {"actions": [{"action": "thymio_motor_on", "parameters": {}}]}}}}},
    }), encoding="utf-8")
    out = tmp_path / "out.xml"

    class FakeIde:
        current_project_path = str(proj)
        def tr(self, s): return s
        def _require_open_project(self): return True
        def update_status(self, *_): pass
        class project_manager:
            @staticmethod
            def is_dirty(): return False

    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(out), "")))
    shown = []
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: shown.append(a)))
    monkeypatch.setattr(QMessageBox, "warning", staticmethod(lambda *a, **k: shown.append(("warn",) + a)))
    ex.export_roberta_xml(FakeIde())
    assert out.exists(), shown
    assert "http://de.fhg.iais.roberta.blockly" in out.read_text(encoding="utf-8")


def test_menus_offer_roberta_import_and_export():
    src = (Path(__file__).resolve().parent.parent / "extensions/thymio/__init__.py").read_text(encoding="utf-8")
    for needle in ('"Export Open &Roberta XML..."', '"Import Open &Roberta XML..."',
                   "export_roberta_xml(ide)", "import_roberta_xml(ide)"):
        assert needle in src
