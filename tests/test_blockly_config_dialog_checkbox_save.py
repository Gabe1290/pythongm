"""Regression test: checking an individual block (e.g. "Set Variable") in
the Configure Action Blocks dialog silently got wiped again before Save,
so it never actually persisted.

Real classroom report, 2026-10-11 (French IDE): "I tried to make the set
variable block appear but the IDE will not save the new configuration."
Root cause, found by driving the real dialog rather than guessing: category
QTreeWidgetItems carry Qt.ItemIsAutoTristate (populate_tree in
dialogs/_block_config_dialog_base.py), so checking ANY one child makes Qt
recompute the category's own checkbox and re-fire itemChanged for the
CATEGORY item too -- a second, automatic call into on_item_changed for the
very same click. When not every sibling block in that category is also
enabled, the recompute lands on PartiallyChecked. The old code did
`is_checked = item.checkState(0) == Qt.Checked`, which is False for
PartiallyChecked -- so the category branch read that as "the user
unchecked the whole category" and called disable_category(), discarding
the block the child branch had just enabled a moment earlier in the same
click. "Set Variable" specifically could never stick, because Control
already has other blocks enabled in every preset (test_variable, exit_event,
...), so it's never anything BUT partially-checked there.

Traced with real instrumentation (not guessed): on_item_changed fires
TWICE per single checkbox click in this scenario -- once for the child
(correctly enabling the block) and once more, synchronously, for the
auto-tristate-recomputed category (which used to immediately undo it).

2026-10-23: beginner's own Blockly preset gained "set_variable" by default
(docs/... beginner-sample coverage audit -- views_1/treasure/sky_strike_1
etc. actually use it), so Set Variable/Control is no longer a currently-off-
by-default/partially-checked pairing to reproduce the bug with. The tests
below switched their verification vehicle to "If Can Push"/Instance, which
has the identical shape (If Can Push stays off by default; Instance already
has other blocks on, so it's always partially-checked) -- same mechanism,
different block. The history above is left as written; it's the real report
that found the bug, not a description of today's defaults.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

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


def _find_block_item(dialog, label):
    for i in range(dialog.tree.topLevelItemCount()):
        cat_item = dialog.tree.topLevelItem(i)
        for j in range(cat_item.childCount()):
            child = cat_item.child(j)
            if child.text(0) == label:
                return child
    raise AssertionError(f"Block item {label!r} not found in the tree")


def _dialog_from_preset(preset_name):
    from config.blockly_config import PRESETS, BlocklyConfig
    from dialogs.blockly_config_dialog import BlocklyConfigDialog
    config = BlocklyConfig.from_dict(PRESETS[preset_name].to_dict())
    return BlocklyConfigDialog(None, config)


def test_if_can_push_is_unchecked_by_default_in_beginner(_qapp):
    """Baseline: confirms the starting state this bug report actually hit
    (see the module docstring for why "If Can Push"/Instance replaced the
    original "Set Variable"/Control reproduction)."""
    dialog = _dialog_from_preset("beginner")
    assert "if_can_push" not in dialog.config.enabled_blocks
    item = _find_block_item(dialog, "If Can Push")
    from PySide6.QtCore import Qt
    assert item.checkState(0) == Qt.Unchecked


def test_checking_if_can_push_survives_the_auto_tristate_recompute(_qapp):
    """The actual bug: Instance is already partially-checked in beginner
    (other blocks there are on), so checking one more child triggers the
    category's own PartiallyChecked re-fire -- which used to wipe the
    child's change immediately."""
    from PySide6.QtCore import Qt
    dialog = _dialog_from_preset("beginner")
    item = _find_block_item(dialog, "If Can Push")
    item.setCheckState(0, Qt.Checked)
    assert "if_can_push" in dialog.config.enabled_blocks


def test_checking_if_can_push_does_not_disable_the_rest_of_instance(_qapp):
    """The old bug's blast radius was worse than just "If Can Push"
    missing -- disable_category() wiped every OTHER already-enabled
    Instance block too (instance_create, instance_destroy, ...)."""
    from PySide6.QtCore import Qt
    dialog = _dialog_from_preset("beginner")
    assert "instance_create" in dialog.config.enabled_blocks  # beginner default
    item = _find_block_item(dialog, "If Can Push")
    item.setCheckState(0, Qt.Checked)
    assert "instance_create" in dialog.config.enabled_blocks
    assert "Instance" in dialog.config.enabled_categories


def test_full_save_and_reload_round_trip_persists_the_change(_qapp, tmp_path, monkeypatch):
    """End-to-end: check the box, save (as clicking OK does), and reload
    the config from disk the way reopening the dialog after an app restart
    does -- the actual user-visible symptom ("will not save")."""
    from PySide6.QtCore import Qt
    from config.blockly_config import get_config_path, load_config

    monkeypatch.setattr("config.blockly_config.Path.home", lambda: tmp_path)
    config_path = get_config_path()
    assert str(tmp_path) in str(config_path)

    dialog = _dialog_from_preset("beginner")
    item = _find_block_item(dialog, "If Can Push")
    item.setCheckState(0, Qt.Checked)
    assert dialog.config.preset_name == "custom"

    dialog.save_and_close()  # the real Save/OK path

    reloaded = load_config()
    assert "if_can_push" in reloaded.enabled_blocks


def test_unchecking_a_block_still_works_normally(_qapp):
    """Sanity check the fix didn't break the ordinary, non-tristate-tricky
    direction: unchecking an enabled block must still disable it."""
    from PySide6.QtCore import Qt
    dialog = _dialog_from_preset("beginner")
    item = _find_block_item(dialog, "Test Variable")
    assert "test_variable" in dialog.config.enabled_blocks
    item.setCheckState(0, Qt.Unchecked)
    assert "test_variable" not in dialog.config.enabled_blocks
