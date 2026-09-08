"""L15, docs/FULL_AUDIT_2026-09-07.md: object editor validation fails for
a floated editor with no reachable IDE data.

ObjectEditor.validate_data() rejected any assigned sprite whenever
self.available_sprites was empty -- but that dict starts empty (__init__)
and is only ever populated by a push from the IDE
(apply_available_sprites) or by walking the parent chain to a reachable
project_manager. A floated (detached) editor window whose parent chain
can't reach the IDE, or hasn't received the push yet, has NO reliable
information about which sprites really exist -- so it rejected every
save with "Referenced sprite '...' does not exist", even for a sprite
that genuinely exists in the project.

Fix: skip the sprite-existence check when available_sprites is
empty/unknown, since there's nothing real to validate against in that
state -- silently blocking every save is worse than skipping a
redundant check.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _editor_with(_qapp, sprite_name, available_sprites):
    from editors.object_editor.object_editor_main import ObjectEditor
    editor = ObjectEditor()
    editor.available_sprites = available_sprites
    editor.get_data = lambda: {
        "name": "obj_test", "sprite": sprite_name, "events": {},
    }
    return editor


def test_unknown_sprite_list_does_not_block_a_valid_save(_qapp):
    """The exact bug: a floated editor with no reachable IDE data must not
    reject a save just because it can't currently confirm the sprite
    exists."""
    editor = _editor_with(_qapp, "spr_player", available_sprites={})
    is_valid, message = editor.validate_data()
    assert is_valid is True
    assert message == ""


def test_no_sprite_assigned_is_still_valid_regardless(_qapp):
    editor = _editor_with(_qapp, "", available_sprites={})
    is_valid, message = editor.validate_data()
    assert is_valid is True


def test_known_sprite_list_still_rejects_a_genuinely_missing_sprite(_qapp):
    """The fix must not disable the check entirely -- once the sprite
    list IS known, a reference to something that really doesn't exist
    must still be caught."""
    editor = _editor_with(_qapp, "spr_ghost",
                           available_sprites={"spr_player": {}, "spr_enemy": {}})
    is_valid, message = editor.validate_data()
    assert is_valid is False
    assert "spr_ghost" in message


def test_known_sprite_list_accepts_a_real_sprite(_qapp):
    editor = _editor_with(_qapp, "spr_player",
                           available_sprites={"spr_player": {}, "spr_enemy": {}})
    is_valid, message = editor.validate_data()
    assert is_valid is True
