"""
Regression test for audit L5.

open_editors / detached_editor_windows were keyed by the bare asset name, so a
room and an object (or any two assets of different types) sharing a name
collided on one slot: opening the second overwrote the first's entry, and
deleting/closing one tore down the other. They are now keyed by a composite
"<category>:<name>" key.

Constructs the real IDE window offscreen (no pytest-qt), so it runs on 3.11.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def ide(_qapp):
    from core.ide_window import PyGameMakerIDE
    w = PyGameMakerIDE()
    w.current_project_path = tempfile.mkdtemp()
    yield w
    w.deleteLater()


def test_editor_key_normalizes_singular_and_plural(ide):
    # Both the singular asset_data form and the plural category map to one key.
    assert ide._editor_key("object", "foo") == ide._editor_key("objects", "foo")
    assert ide._editor_key("sprites", "foo") == "sprites:foo"


def test_same_named_object_and_sprite_coexist(ide):
    ide.open_object_editor("dup", {"name": "dup", "asset_type": "object", "events": {}})
    ide.open_sprite_editor("dup", {"name": "dup", "asset_type": "sprite", "frames": []})
    assert set(ide.open_editors) == {"objects:dup", "sprites:dup"}
    assert len(ide.open_editors) == 2


def test_closing_one_leaves_the_same_named_other(ide):
    ide.open_object_editor("dup", {"name": "dup", "asset_type": "object", "events": {}})
    ide.open_sprite_editor("dup", {"name": "dup", "asset_type": "sprite", "frames": []})

    ide.close_editor_by_name("dup", "objects")
    assert set(ide.open_editors) == {"sprites:dup"}

    # The surviving sprite editor's tab is still present.
    titles = [ide.editor_tabs.tabText(i).replace("*", "")
              for i in range(ide.editor_tabs.count())]
    assert "dup" in titles


def test_reopening_same_type_focuses_not_duplicates(ide):
    ide.open_object_editor("hero", {"name": "hero", "asset_type": "object", "events": {}})
    ide.open_object_editor("hero", {"name": "hero", "asset_type": "object", "events": {}})
    assert list(ide.open_editors) == ["objects:hero"]
