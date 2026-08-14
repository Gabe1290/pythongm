"""PlaygroundEditor._refresh_linkable_objects read project.json's embedded
object 'events' directly, with no merge from objects/<name>.json (found
while auditing TODO.md's "Manifest-ify objects & sprites" fallback-read
call sites). An object detectable as Thymio only via its thymio_* event
names (not a 'thymio'-prefixed asset name or an explicit is_thymio flag)
would silently vanish from the Playground Editor's "linkable objects" list
the moment project.json's embedded copy no longer carries the real events.

run_playground (right below it in the same file) already merges via
_load_external_objects -- _refresh_linkable_objects now reuses that same
helper instead of duplicating the merge.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _write_project_with_manifest_object(tmp_path):
    proj_dir = tmp_path / "proj"
    proj_dir.mkdir()
    (proj_dir / "project.json").write_text(json.dumps({
        "name": "T",
        "assets": {
            # No 'thymio' in the name, no is_thymio flag -- only detectable
            # via its thymio_* events, which live ONLY in the side file.
            "objects": {"obj_bot": {"name": "obj_bot"}},
        },
    }), encoding="utf-8")
    objects_dir = proj_dir / "objects"
    objects_dir.mkdir()
    (objects_dir / "obj_bot.json").write_text(json.dumps({
        "name": "obj_bot",
        "events": {"thymio_button_forward": {"actions": []}},
    }), encoding="utf-8")
    return proj_dir


def test_thymio_object_detected_only_via_merged_events(_qapp, tmp_path):
    from editors.playground_editor import PlaygroundEditor

    proj_dir = _write_project_with_manifest_object(tmp_path)
    editor = PlaygroundEditor(str(proj_dir))

    captured = []
    editor.element_properties.set_linkable_objects = lambda names: captured.append(names)

    editor._refresh_linkable_objects()

    assert captured == [["obj_bot"]], (
        "obj_bot's thymio_* event lives only in objects/obj_bot.json -- "
        "must still be detected as linkable")


def test_non_thymio_object_not_linkable(_qapp, tmp_path):
    from editors.playground_editor import PlaygroundEditor

    proj_dir = tmp_path / "proj2"
    proj_dir.mkdir()
    (proj_dir / "project.json").write_text(json.dumps({
        "name": "T",
        "assets": {"objects": {"obj_plain": {"name": "obj_plain"}}},
    }), encoding="utf-8")
    objects_dir = proj_dir / "objects"
    objects_dir.mkdir()
    (objects_dir / "obj_plain.json").write_text(json.dumps({
        "name": "obj_plain",
        "events": {"create": {"actions": []}},
    }), encoding="utf-8")

    editor = PlaygroundEditor(str(proj_dir))
    captured = []
    editor.element_properties.set_linkable_objects = lambda names: captured.append(names)

    editor._refresh_linkable_objects()

    assert captured == [[]]
